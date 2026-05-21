---
name: observability-designer
description: >-
  Designs unified observability for a TypeScript agent/CLI: NDJSON structured
  logs, correlation ids via AsyncLocalStorage, metric naming, redaction reuse,
  and trace boundaries across CLI, agent loop, LLM client, and tool registry.
  Use when adding structured logging, "correlation id", "trace id", NDJSON,
  metrics naming, log levels, or "make logs greppable across layers". Not for
  authoring system prompts or implementing redaction from scratch without
  llm-client-architect Patterns.
---

# Observability Designer

## When to use

- User adds logging, metrics, or tracing to an agent runner or CLI and needs one consistent shape.
- User needs correlation between a CLI invocation, the agent iterations it spawned, and the LLM/tool calls inside each iteration.
- User integrates with an existing log aggregator (Datadog, Loki, CloudWatch) and needs stable field names.
- User wants to keep integration-tester goldens stable by normalizing timestamps and ids.
- User asks where to put log redaction so it is not reimplemented in every layer.

## Core principles

1. One log format across all layers: NDJSON to stderr, one event per line, UTF-8, newline-terminated.
2. Every event carries a `correlation_id` propagated via `AsyncLocalStorage`; never thread it through parameters.
3. Stable top-level fields: `ts`, `level`, `event`, `correlation_id`, `iteration`, `component`, plus event-specific fields under `data`.
4. Log levels are enums (`debug | info | warn | error`); never numbers, never strings outside the enum.
5. Redaction is a single shared `safeBody` function (implement per `llm-client-architect` Patterns § Redacted headers and body, typically `src/llm/redact.ts`); never inlined per layer.
6. Metrics use dotted names (`agent.iteration.duration_ms`, `llm.request.tokens.input`); tags are low-cardinality.
7. Trace boundaries: CLI invocation → agent run → iteration → llm request → tool call. Each opens a span with the parent's id.
8. Timestamps are ISO-8601 UTC at millisecond precision. Integration tests strip them; production keeps them.
9. Never log full prompts, file contents, or tool inputs by default; log sizes, hashes, and event ids. Provide a `debug`-only verbose mode behind config.
10. Logs are an interface — breaking changes to field names require the same review as breaking changes to a CLI flag.

## Checklist

- [ ] Pick a logger: a 50-line in-house NDJSON writer is preferable to a heavyweight dependency for a CLI.
- [ ] Implement `withCorrelation(id, fn)` using `AsyncLocalStorage` and use it at every entry point (CLI main, server handler, test harness).
- [ ] Define a typed `LogEvent` discriminated union per component to prevent typo drift.
- [ ] Wire redaction into the log writer; do not trust callers to pre-redact.
- [ ] Emit `iteration_start` / `iteration_end` from agentic-loop-engineer with `iteration`, `tool_calls`, `tokens_in`, `tokens_out`, `duration_ms`.
- [ ] Emit `llm_request_start` / `llm_request_end` from llm-client-architect with `provider`, `model`, `status`, `attempt`, `duration_ms`.
- [ ] Emit `tool_call_start` / `tool_call_end` from tool-registry-architect with `tool`, `tool_call_id`, `outcome`, `duration_ms`.
- [ ] Integration tests normalize `ts`, `correlation_id`, and `tool_call_id` to fixed placeholders before golden comparison.
- [ ] Document how to enable verbose mode (`LOG_LEVEL=debug`) and what additional fields appear.
- [ ] Confirm no secrets and no file contents appear in any sample log line during CI.

## Patterns

**Correlation context via AsyncLocalStorage**

```typescript
import { AsyncLocalStorage } from "node:async_hooks";

type Ctx = { correlationId: string; iteration?: number };
const als = new AsyncLocalStorage<Ctx>();

export function withCorrelation<T>(ctx: Ctx, fn: () => Promise<T>): Promise<T> {
  return als.run(ctx, fn);
}

export function currentCtx(): Ctx {
  return als.getStore() ?? { correlationId: "uncorrelated" };
}
```

**NDJSON logger with shared redaction**

Copy `safeBody` from `llm-client-architect` Patterns (or import from your project's redact module, e.g. `src/llm/redact.ts`):

```typescript
// import { safeBody } from "../llm/redact";
const SECRET_KEY_RX = /key|token|secret|password|authorization/i;
function safeBody(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(safeBody);
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = SECRET_KEY_RX.test(k) ? "[REDACTED]" : safeBody(v);
    }
    return out;
  }
  return value;
}

type Level = "debug" | "info" | "warn" | "error";

export function log(level: Level, event: string, data: object = {}): void {
  const { correlationId, iteration } = currentCtx();
  const line = JSON.stringify({
    ts: new Date().toISOString(),
    level,
    event,
    correlation_id: correlationId,
    iteration,
    data: safeBody(data),
  });
  process.stderr.write(line + "\n");
}
```

**Typed events per component**

```typescript
export type AgentEvent =
  | { event: "iteration_start"; data: { iteration: number } }
  | { event: "iteration_end"; data: { iteration: number; tool_calls: number; tokens_in: number; tokens_out: number; duration_ms: number } }
  | { event: "loop_terminated"; data: { reason: "end_turn" | "max_iterations" | "abort" | "no_progress" } };
```

**Normalization for golden tests**

```typescript
export function normalizeLogs(lines: string[]): string {
  return lines
    .map((l) => JSON.parse(l))
    .map((e) => ({ ...e, ts: "<ts>", correlation_id: "<cid>", data: stripIds(e.data) }))
    .map((e) => JSON.stringify(e))
    .join("\n");
}
```

## Anti-patterns

- **Logging to stdout** — mixes with machine-readable CLI output; logs always go to stderr.
- **Per-module ad-hoc redaction** — drift; import one redactor and put it in the writer.
- **Threading `correlationId` through function parameters** — pollutes every signature; use `AsyncLocalStorage`.
- **High-cardinality metric tags** (e.g., file paths, user ids) — explodes the metric store; bucket or hash.
- **Logging full prompts or tool inputs at `info`** — leaks and noise; size/hash at `info`, content only at `debug` behind a flag.
- **Renaming a top-level field without a deprecation window** — breaks dashboards; treat field names as API.

## Output format

```markdown
# Observability plan: <project>

## Transport
- Format: NDJSON
- Sink: stderr (default) | file | <aggregator>

## Top-level fields
| Field | Type | Notes |
|-------|------|-------|
| ts | string ISO-8601 | UTC ms |
| level | enum | debug/info/warn/error |
| event | string | <component>_<verb> |
| correlation_id | string | propagated via ALS |
| iteration | number? | present in agent events |
| data | object | redacted before write |

## Events
| Event | Component | Fields under data |
|-------|-----------|-------------------|

## Metrics
| Name | Tags | Source |
|------|------|--------|

## Test normalization
- Stripped fields: ts, correlation_id, tool_call_id
- Helper: <path>
```

## Escalation

- Ask whether logs ship to an aggregator (affects field naming conventions) and whether tracing is required (OpenTelemetry vs lightweight).
- Ask whether the CLI must support `--quiet` and `--json` modes that change stderr/stdout policy.
- Proceed with stderr-NDJSON + AsyncLocalStorage when scope is unclear; flag any aggregator-specific schema as a follow-up.
