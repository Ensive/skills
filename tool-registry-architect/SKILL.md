---
name: tool-registry-architect
description: >-
  Designs the tool registry for an agent runner: typed tool schemas (Zod or JSON
  Schema), capability flags (read/write/exec/network), input validation, per-tool
  timeouts with AbortSignal propagation, normalized result shape, and audit
  logging. Use when defining new agent tools, "tool schema", "tool registry",
  capability flags, per-tool timeout, "validate tool input", or "what shape does
  a tool result return". Not for system-prompt authoring, HTTP retries, or
  greenfield loop design without types from agentic-loop-engineer/reference.md.
---

# Tool Registry Architect

## When to use

- User defines a new tool the agent can call (read file, run shell, fetch URL, query db).
- User wires Zod or JSON Schema validation between the model's tool call and the handler.
- User needs to declare capability flags (read, write, exec, network) and gate them by config.
- User wants per-tool timeouts and AbortSignal propagation that interrupts long calls.
- User asks how tool results should look so agentic-loop-engineer can classify retry/fatal.

## Core principles

1. One registry per process; tools register at boot, never at request time.
2. Every tool declares: name, description, input schema, capability set, timeout, handler.
3. Input is validated against the schema before the handler runs; validation failures are *fatal* (do not retry, return shaped error to model).
4. Handlers receive `(input, ctx)` where `ctx` carries `signal`, `workspaceRoot`, `logger`, and the tool-call id. Never `process.env`.
5. Capability flags gate the registry, not the handler: a write-disabled run cannot even *see* write tools.
6. Per-tool timeout is wrapped around the handler at the registry layer; the same `AbortSignal` flows into FS reads, fetch, and child processes.
7. Handlers return the `NormalizedToolResult` shape owned by agentic-loop-engineer; loop and registry never disagree on field names.
8. Audit log every invocation: tool name, hashed input, duration, outcome class. Redact via the rules in llm-client-architect.
9. The registry is the *only* place that knows the model-provider's tool-call format; loop and adapters consume the normalized shape.
10. Schema and capability descriptions are sent to the model verbatim; treat them as part of the prompt surface and review under prompt-engineer.

## Checklist

- [ ] Define `ToolDefinition<I>` with `name`, `description`, `schema`, `capabilities`, `timeoutMs`, `handler`.
- [ ] Validate `input` with the schema; on failure return `{ isError: true, content: "{\"error\":\"invalid_input\",...}" }` and mark non-retryable.
- [ ] Resolve capability set from config; drop tools whose required capabilities are not granted before registration.
- [ ] Wrap each handler in `withTimeout(signal, timeoutMs)`; propagate the linked signal into all I/O.
- [ ] Standardize error categories: `invalid_input`, `not_found`, `forbidden`, `timeout`, `transient`, `internal`. Map to `isError: true`.
- [ ] Hash large inputs (e.g. file contents) before logging; log only sizes and hashes.
- [ ] Expose `describeForModel()` that emits the provider-shaped tool descriptor list.
- [ ] Forbid mutation of the registry after `freeze()` is called during boot.
- [ ] Cover registry behavior with unit tests; cover full loop+registry wiring in integration-tester.
- [ ] Document which capabilities the default profile enables (typically: `read`, no `write`/`exec`/`network`).

## Patterns

Import normalized types from the project types module (default `src/agent/types.ts`; definitions in `agentic-loop-engineer/reference.md`). Import FS helpers from the project FS module (implement per `secure-filesystem-access`; export contract in `secure-filesystem-access/reference.md`).

**Tool definition with Zod schema and capabilities**

```typescript
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import type { NormalizedToolResult } from "../agent/types";
import { resolveInside, readBounded } from "../fs/workspace";

export type Capability = "read" | "write" | "exec" | "network";

export interface ToolContext {
  signal: AbortSignal;
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

  constructor(private readonly granted: ReadonlySet<Capability>) {}

  register<I>(def: ToolDefinition<I>): void {
    if (this.frozen) throw new Error("registry frozen");
    for (const cap of def.capabilities) {
      if (!this.granted.has(cap)) return; // silently drop; not visible to model
    }
    this.tools.set(def.name, def as ToolDefinition<unknown>);
  }

  freeze(): void { this.frozen = true; }

  describeForModel(): Array<{ name: string; description: string; input_schema: unknown }> {
    return [...this.tools.values()].map((t) => ({
      name: t.name,
      description: t.description,
      input_schema: zodToJsonSchema(t.schema),
    }));
  }

  async run(name: string, rawInput: unknown, ctx: ToolContext): Promise<NormalizedToolResult> {
    const def = this.tools.get(name);
    if (!def) return errorResult(ctx.toolCallId, "not_found", `unknown tool ${name}`);
    const parsed = def.schema.safeParse(rawInput);
    if (!parsed.success) return errorResult(ctx.toolCallId, "invalid_input", parsed.error.message);

    const ac = new AbortController();
    const onParent = () => ac.abort(ctx.signal.reason);
    ctx.signal.addEventListener("abort", onParent, { once: true });
    const timer = setTimeout(() => ac.abort(new Error("tool_timeout")), def.timeoutMs);
    const started = performance.now();
    try {
      const content = await def.handler(parsed.data, { ...ctx, signal: ac.signal });
      return { id: ctx.toolCallId, content, isError: false };
    } catch (e) {
      const code = classifyRegistryError(e);
      return errorResult(ctx.toolCallId, code, (e as Error).message);
    } finally {
      clearTimeout(timer);
      ctx.signal.removeEventListener("abort", onParent);
      ctx.logger.info("tool_call", { name, ms: performance.now() - started, id: ctx.toolCallId });
    }
  }
}

function errorResult(id: string, code: string, message: string): NormalizedToolResult {
  return { id, content: JSON.stringify({ error: code, message }), isError: true };
}

function classifyRegistryError(e: unknown): string {
  if (e instanceof Error && e.name === "AbortError") return "timeout";
  const msg = e instanceof Error ? e.message : String(e);
  if (msg.includes("path outside workspace") || msg.includes("not permitted")) return "forbidden";
  if (msg.includes("ENOENT") || msg.includes("file_not_found")) return "not_found";
  if (msg.includes("EAGAIN") || msg.includes("EBUSY")) return "transient";
  return "internal";
}
```

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
- **Registering write/exec tools and then checking capability in the handler** — the model still sees the tool and tries it. Drop at registration.
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
- Redaction source: llm-client-architect
```

## Escalation

- Ask which capabilities the deployment grants by default (read-only is the safe starting point).
- Ask the timeout budget per request before assigning per-tool timeouts.
- Proceed with read-only Zod-based registry when scope is unclear; flag any write/exec tool as requiring an explicit capability flip.
