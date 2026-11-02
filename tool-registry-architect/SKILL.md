---
name: tool-registry-architect
description: >-
  Designs the tool registry for an agent runner: typed tool schemas (Zod or JSON
  Schema), capability flags (read/write/exec/network), input validation, per-tool
  timeouts with AbortSignal propagation, normalized result shape, and audit
  logging. Use when defining new agent tools, "tool schema", "tool registry",
  capability flags, per-tool timeout, "validate tool input", or "what shape does
  a tool result return". Not for system-prompt authoring, HTTP retries, or
  greenfield loop orchestration.
---

# Tool Registry Architect

## Project discovery

Read applicable project instructions, manifests, nearby code/tests and CI. Discover paths, runtime, contracts, data restrictions and commands with working directories. Preserve existing stack choices; adapt the examples to those conventions. Use a reversible step when context is incomplete; ask only when behavior or authorization blocks it. Optional neighbors are not prerequisites.

## When to use

- User defines a new tool the agent can call (read file, run shell, fetch URL, query db).
- User wires Zod or JSON Schema validation between the model's tool call and the handler.
- User needs to declare capability flags (read, write, exec, network) and gate them by config.
- User wants per-tool timeouts and AbortSignal propagation that interrupts long calls.
- User asks how tool results should look so agentic-loop-engineer can classify retry/fatal.

## Core principles

1. Keep definitions stable for each run. A process catalog may be shared, but authorization and visible tool selection must be scoped to the authenticated request/tenant.
2. Every tool declares: name, description, input schema, capability set, timeout, handler.
3. Validate input before the handler runs; failures are non-retryable. Model-facing errors use fixed public messages, never exception or validation-library text that can include credentials or rejected values. Keep diagnostics separate under the project's redaction policy.
4. Handlers receive `(input, ctx)` where `ctx` carries `signal`, `workspaceRoot`, `logger`, and the tool-call id. Never `process.env`.
5. Filter visible tools by granted capabilities and recheck invocation authorization against the current request/tenant. Hiding a tool is not an authorization boundary.
6. Per-tool timeout is wrapped around the handler at the registry layer; the same `AbortSignal` flows into FS reads, fetch, and child processes.
7. Handlers and the loop use the target project’s result contract; adapt the example shape below instead of importing a catalog-owned type.
8. Audit log every invocation: tool name, hashed input, duration, outcome class. Use the project’s allowlisted observability/redaction policy; hashes are not anonymization.
9. Provider adapters own wire-format translation. The registry validates normalized calls and exposes provider-neutral descriptors.
10. Schema and capability descriptions are sent to the model verbatim; treat them as part of the prompt surface and review under prompt-engineer.

## Checklist

- [ ] Define `ToolDefinition<I>` with `name`, `description`, `schema`, `capabilities`, `timeoutMs`, `handler`.
- [ ] Validate `input` with the schema; on failure return `{ isError: true, content: "{\"error\":\"invalid_input\",...}" }` and mark non-retryable.
- [ ] Resolve capability set from config; drop tools whose required capabilities are not granted before registration.
- [ ] Wrap each handler in `withTimeout(signal, timeoutMs)`; propagate the linked signal into all I/O.
- [ ] Standardize error categories: `invalid_input`, `not_found`, `forbidden`, `timeout`, `transient`, `internal`. Map to `isError: true`.
- [ ] Log allowlisted metadata such as input size; use hashes only under the project's data policy.
- [ ] Expose provider-neutral descriptors; the provider adapter translates them to its wire schema.
- [ ] Forbid mutation of the registry after `freeze()` is called during boot.
- [ ] Cover registry behavior with unit tests; cover full loop+registry wiring in integration-tester.
- [ ] Document which capabilities the default profile enables (typically: `read`, no `write`/`exec`/`network`).

## Patterns

Use existing project contracts. The TypeScript/Zod recipe below uses illustrative imports, a Node filesystem handler and a cooperative cancellation model. Adapt schemas to the installed version. For hostile mutable filesystems, the path helper alone is insufficient containment. No sibling skill is required.

**Tool definition with Zod schema and capabilities**

```typescript
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import type { NormalizedToolResult } from "../agent/types";
import { resolveInside, readBounded } from "../fs/workspace";

export type Capability = "read" | "write" | "exec" | "network";

export interface ToolContext {
  signal: AbortSignal;
  granted: ReadonlySet<Capability>;
  workspaceRoot: string;
  logger: { info: (msg: string, fields?: object) => void };
  toolCallId: string;
}

export interface ToolDefinition<I> {
  name: string;
  description: string;
  schema: z.ZodType<I>;
  capabilities: ReadonlySet<Capability>;
  timeoutMs: number;
  handler: (input: I, ctx: ToolContext) => Promise<string>;
}

export const readFileTool: ToolDefinition<{ path: string; maxBytes?: number }> = {
  name: "read_file",
  description: "Read a UTF-8 text file inside the workspace.",
  schema: z.object({ path: z.string().min(1), maxBytes: z.number().int().positive().max(1_048_576).optional() }),
  capabilities: new Set(["read"]),
  timeoutMs: 5_000,
  handler: async ({ path, maxBytes = 64_000 }, ctx) => {
    const real = await resolveInside(ctx.workspaceRoot, path);
    return (await readBounded(real, maxBytes)).toString("utf8");
  },
};
```

If `zod-to-json-schema` is unavailable, emit a minimal JSON Schema manually or use `@asteasolutions/zod-to-openapi` — do not leave `zodToJsonSchema` undefined.

**Registry with capability gating and per-tool timeout**

```typescript
export class ToolRegistry {
  private tools = new Map<string, ToolDefinition<unknown>>();
  private frozen = false;

  private readonly granted: ReadonlySet<Capability>;
  constructor(granted: ReadonlySet<Capability>) { this.granted = granted; }

  register<I>(def: ToolDefinition<I>): void {
    if (this.frozen) throw new Error("registry frozen");
    for (const cap of def.capabilities) {
      if (!this.granted.has(cap)) return; // silently drop; not visible to model
    }
    this.tools.set(def.name, def as ToolDefinition<unknown>);
  }

  freeze(): void { this.frozen = true; }

  describeTools(granted: ReadonlySet<Capability>): Array<{ name: string; description: string; inputSchema: unknown }> {
    return [...this.tools.values()].filter(t => [...t.capabilities].every(cap => granted.has(cap))).map((t) => ({
      name: t.name,
      description: t.description,
      inputSchema: zodToJsonSchema(t.schema),
    }));
  }

  async run(name: string, rawInput: unknown, ctx: ToolContext): Promise<NormalizedToolResult> {
    const def = this.tools.get(name);
    if (!def) return errorResult(ctx.toolCallId, "not_found");
    if (![...def.capabilities].every(cap => ctx.granted.has(cap)))
      return errorResult(ctx.toolCallId, "forbidden");
    const parsed = def.schema.safeParse(rawInput);
    if (!parsed.success) return errorResult(ctx.toolCallId, "invalid_input");

    // The trusted caller supplies current request grants; object-level auth stays in its service boundary.
    if (ctx.signal.aborted) return errorResult(ctx.toolCallId, "cancelled");
    const ac = new AbortController();
    const onParent = () => ac.abort(ctx.signal.reason);
    ctx.signal.addEventListener("abort", onParent, { once: true });
    const timer = setTimeout(() => ac.abort(new Error("tool_timeout")), def.timeoutMs);
    const started = performance.now();
    try {
      const content = await def.handler(parsed.data, { ...ctx, signal: ac.signal });
      return { id: ctx.toolCallId, content, isError: false };
    } catch (e) {
      const code = ctx.signal.aborted ? "cancelled" : ac.signal.aborted ? "timeout" : classifyRegistryError(e);
      return errorResult(ctx.toolCallId, code);
    } finally {
      clearTimeout(timer);
      ctx.signal.removeEventListener("abort", onParent);
      ctx.logger.info("tool_call", { name, ms: performance.now() - started, id: ctx.toolCallId });
    }
  }
}

const PUBLIC_ERRORS = {
  invalid_input: "Tool arguments do not match the input schema.",
  not_found: "The requested tool or resource was not found.",
  forbidden: "This operation is not permitted.",
  cancelled: "The operation was cancelled.",
  timeout: "The operation timed out.",
  transient: "The operation is temporarily unavailable.",
  internal: "The tool could not complete the operation.",
} as const;
type ToolErrorCode = keyof typeof PUBLIC_ERRORS;

function errorResult(id: string, code: ToolErrorCode): NormalizedToolResult {
  return { id, content: JSON.stringify({ error: code, message: PUBLIC_ERRORS[code] }), isError: true };
}

function classifyRegistryError(e: unknown): ToolErrorCode {
  if (e instanceof Error && e.name === "AbortError") return "timeout";
  const msg = e instanceof Error ? e.message : String(e);
  if (msg.includes("path outside workspace") || msg.includes("not permitted")) return "forbidden";
  if (msg.includes("ENOENT") || msg.includes("file_not_found")) return "not_found";
  if (msg.includes("EAGAIN") || msg.includes("EBUSY")) return "transient";
  return "internal";
}
```

This is a wiring sketch: production instrumentation must also record denied/invalid calls before these early returns. The timeout only signals cooperative handlers. A handler that ignores cancellation may keep running; bound isolated workers/processes where hard termination is required, and do not retry an unknown mutation outcome. A Node filesystem read does not become cancellable just because the context has a signal.

**Read-only default profile**

```typescript
const registry = new ToolRegistry(new Set(["read"]));
registry.register(readFileTool);
registry.register(listDirTool);
// writeFileTool with capability "write" is silently dropped — the model never sees it
registry.freeze();
```

## Anti-patterns

- **Validating tool input inside the handler** — duplicates schema; failures escape as 500s. Validate at the registry boundary.
- **Per-tool AbortControllers not linked to the loop signal** — Ctrl+C cannot interrupt the tool; always chain from `ctx.signal`.
- **Treating model visibility as authorization** — filter descriptors and enforce current grants before every invocation.
- **Returning provider-shaped objects from handlers** — couples handlers to one provider; emit `NormalizedToolResult` only.
- **Logging full tool input verbatim** — file contents and secrets leak; hash or summarize.
- **Mutating the registry mid-run** — non-deterministic; freeze after boot.

## Output format

```markdown
# Tool registry design: <project>

## Capabilities
- Granted: <set>
- Denied (tools dropped): <list>

## Tools
| Name | Capabilities | Timeout | Schema summary |
|------|--------------|---------|----------------|

## Error taxonomy
- invalid_input | not_found | forbidden | timeout | transient | internal

## Wiring
- Loop consumes: NormalizedToolResult
- Adapter emits: NormalizedToolCall

## Audit logging
- Fields per call: <list>
- Redaction source: the project observability/export policy
```

## Escalation

- Discover deployment grants and request budgets from configuration; ask only if a required authorization or timeout decision remains unresolved.
- Use existing schema tooling and a conservative read-only proposal when grants are unspecified; actual write/exec authorization comes from the host/project policy.

## Tools and verification

Use existing tools and synthetic fixtures within the task's authorization. If execution is unavailable, provide the check and mark it unexecuted. Report changed artifacts, assumptions, exact commands/cwd, results and remaining gaps; verify the affected success/failure boundary and project conventions. Examples do not authorize downloads or external mutations.

## Handoffs

Required sibling skills: none. Local references are implementation examples, included with this skill.

- Optional: `agentic-loop-engineer` — Choose recovery and termination from normalized outcomes.
- Optional: `secure-filesystem-access` — Implement filesystem-capable handlers.
- Optional: `observability-designer` — Keep redacted invocation diagnostics separate from allowlisted model-facing errors.
- Optional: `prompt-engineer` — Review model-visible tool descriptions.
- Optional: `integration-tester` — Verify registry and application wiring.
