# TypeScript CLI Architect — reference

## Composition chain (new TS agent CLI)

**Greenfield vs maintenance:** bootstrapping a new agent/CLI → follow the numbered chain below. Refactors on existing code → run **typescript-refactoring-architect** before test/audit passes (step 0), then re-enter at step 9.

When bootstrapping, run skills in this order; each skill's outputs feed the next. If a sibling skill is not loaded, emit the **minimum viable** stub from that step instead of skipping the concern.

1. **config-and-env-designer** — schema, secrets/settings split, fail-fast loader.
2. **typescript-cli-architect** — entrypoint, parseArgs, signals, exit codes.
3. **llm-client-architect** — provider adapter emitting normalized types (`agentic-loop-engineer/reference.md`).
4. **prompt-engineer** — system prompt, tool preamble, refusals.
5. **agentic-loop-engineer** — runner with normalized tool calls/results.
6. **tool-registry-architect** — tool schemas, capability flags, per-tool timeouts.
   - *MV stub if unavailable:* `ToolRegistry` with `register`, `freeze`, `describeForModel`, `run(name, rawInput, ctx)`; `Capability = "read" | "write" | "exec" | "network"`; gate tools by `granted` at boot; Zod `safeParse` before handler → `{ id, content: JSON.stringify({ error: "invalid_input" }), isError: true }` (fatal, no retry); per-tool timeout + parent `AbortSignal`; return `NormalizedToolResult` per `agentic-loop-engineer/reference.md`; error codes: `invalid_input | not_found | forbidden | timeout | transient | internal`.
7. **secure-filesystem-access** — FS-capable tools (`resolveInside`, `readBounded` from `reference.md`).
8. **observability-designer** — NDJSON + ALS; `safeBody` from `llm-client-architect` Patterns.
   - *MV stub if unavailable:* `AsyncLocalStorage` for `{ correlationId, iteration }`; NDJSON to stderr: `{ ts, level, event, correlation_id, iteration, component, data }` with `data` via `safeBody`; emit `iteration_*`, `llm_request_*`, `tool_call_*`; levels `debug|info|warn|error` only.
9. **typescript-unit-tester** — pure-function and parser coverage.
10. **integration-tester** — fake-LLM e2e transcripts with goldens.
11. **typescript-security-auditor** — final review pass before release.

For maintenance (refactors, decoupling), run **typescript-refactoring-architect** before steps 9–11 when available.
