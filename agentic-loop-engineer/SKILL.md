---
name: agentic-loop-engineer
description: >-
  Engineers reliable agent tool-calling loops with iteration caps, parallel vs
  sequential execution, tool-class retry classification, tool-error shaping,
  history growth control, token budgets, and deterministic termination. Use when
  building an agent runner, agent harness, ReAct loop, tool dispatcher, "tool
  loop", "max iterations", "parallel tool calls", "why is my agent looping",
  tool errors, or "when to stop the agent". HTTP 429/5xx and provider retries:
  llm-client-architect only. Tool argument/validation failures and tool-class
  backoff: this skill only. For tool schema and capability flags see
  tool-registry-architect.
---

# Agentic Loop Engineer

## When to use

- User implements a while-loop that calls LLM then executes tools until done.
- User hits runaway loops, duplicate tool calls, or unbounded message history.
- User needs parallel tool calls vs strict ordering for dependent steps.
- User shapes tool errors for model recovery without leaking stack traces.
- User asks about token limits, summarization, or stopping conditions for agents.

## Core principles

1. Cap iterations explicitly; every loop has a max count and a no-progress breaker.
2. Terminate on explicit terminal tool, structured "done" flag, or user abort only.
3. Run independent tools in parallel; serialize when outputs are inputs to next step.
4. Retry transient failures with exponential backoff and jitter; never retry validation errors.
5. Return tool errors as structured, concise strings; omit internal paths unless policy allows.
6. Trim or summarize history when approaching context limits; preserve system + latest user goal.
7. Deduplicate identical tool calls within the same turn when safe.
8. Record token usage per iteration for budget alerts and downgrade paths.
9. Make termination conditions testable without live LLM calls when possible.
10. Keep prompts and roles in prompt-engineer; provider HTTP and HTTP-layer retry/backoff in llm-client-architect.
11. Use one shared types module (default path `src/agent/types.ts`; full definitions in `reference.md`). llm-client-architect, tool-registry-architect, and integration-tester import the same module — do not redefine fields in adapters or handlers.

## Checklist

- [ ] Define `MAX_ITERATIONS` and `MAX_TOOL_CALLS_PER_TURN` constants in config.
- [ ] Implement no-progress detection (same tool+args repeated N times).
- [ ] Classify tool results: success, retryable, fatal, user-input-required.
- [ ] Apply backoff only to retryable classes with capped attempts per tool id.
- [ ] Batch parallel calls when model returns multiple independent tool_use blocks.
- [ ] Append tool results immediately after assistant tool_use messages (API ordering rules).
- [ ] Prune or summarize messages before each LLM call when over token threshold.
- [ ] Expose abort via AbortSignal wired from SIGINT or cancel API.
- [ ] Emit per-iteration NDJSON logs per observability-designer (`correlation_id`, `iteration`, `event`, `component`); reuse redaction from llm-client-architect.
- [ ] Add integration tests with fake transport (see integration-tester).

## Patterns

Canonical type definitions and the full error-code table live in `reference.md`. Create the types file before wiring the loop.

**Iteration cap with abort**

```typescript
for (let i = 0; i < MAX_ITERATIONS; i++) {
  if (signal.aborted) break;
  const response = await client.complete(messages, { signal });
  if (response.stopReason === "end_turn" && response.toolCalls.length === 0) break;
  const results = await executeTools(response.toolCalls, { signal });
  messages.push(assistantMessage(response), ...toolResultMessages(results));
}
```

**Parallel independent tools**

```typescript
const results: NormalizedToolResult[] = await Promise.all(
  toolCalls.map((tc) => registry.run(tc.name, tc.input, { signal, id: tc.id })),
);
```

**Shaped tool error (normalized)**

```typescript
const result: NormalizedToolResult = {
  id: toolCall.id,
  content: JSON.stringify({ error: "file_not_found", path: relPath }),
  isError: true,
};
```

**History trim before LLM**

```typescript
messages = trimToTokenBudget(messages, budget, { keepSystem: true, keepLastUser: true });
```

**No-progress breaker (same tool + args repeated)**

```typescript
const seen = new Map<string, number>();
function fingerprint(tc: NormalizedToolCall): string {
  return `${tc.name}:${JSON.stringify(tc.input)}`;
}
function registerProgress(toolCalls: NormalizedToolCall[]): void {
  for (const tc of toolCalls) {
    const key = fingerprint(tc);
    seen.set(key, (seen.get(key) ?? 0) + 1);
    if ((seen.get(key) ?? 0) >= MAX_REPEAT) throw new Error("no_progress");
  }
}
```

**Dedupe identical calls within one turn**

```typescript
function dedupeToolCalls(calls: NormalizedToolCall[]): NormalizedToolCall[] {
  const out: NormalizedToolCall[] = [];
  const keys = new Set<string>();
  for (const tc of calls) {
    const key = fingerprint(tc);
    if (keys.has(key)) continue;
    keys.add(key);
    out.push(tc);
  }
  return out;
}
```

**Retry by tool outcome class (not validation errors)**

```typescript
type ToolOutcome = "success" | "retryable" | "fatal" | "user_input_required";

const RETRYABLE_CODES = new Set(["timeout", "transient"]);

function parseToolError(result: NormalizedToolResult): string | undefined {
  if (!result.isError) return undefined;
  try {
    const body = JSON.parse(result.content) as { error?: string };
    return typeof body.error === "string" ? body.error : undefined;
  } catch {
    return undefined;
  }
}

function classify(result: NormalizedToolResult): ToolOutcome {
  if (!result.isError) return "success";
  const code = parseToolError(result);
  if (code === "user_input_required") return "user_input_required";
  if (code && RETRYABLE_CODES.has(code)) return "retryable";
  return "fatal";
}

async function runWithRetry(
  tc: NormalizedToolCall,
  run: () => Promise<NormalizedToolResult>,
): Promise<NormalizedToolResult> {
  let attempt = 0;
  while (attempt < MAX_TOOL_RETRIES) {
    const result = await run();
    const outcome = classify(result);
    if (outcome !== "retryable") return result;
    await sleep(delayMs(attempt++));
  }
  return { id: tc.id, content: JSON.stringify({ error: "transient", message: "retries exhausted" }), isError: true };
}
```

## Anti-patterns

- **Unbounded `while (true)` without cap** — runaway cost; set MAX_ITERATIONS.
- **Retrying invalid tool arguments** — amplifies errors; fail fast with shaped message.
- **Dumping full stack traces to the model** — noise and leak; return minimal error codes.
- **Parallelizing dependent tool chains** — race bugs; topological order or sequential.
- **Growing history without pruning** — context overflow; summarize or drop middle turns.
- **Stopping only when model says "done" in prose** — unreliable; use tool or schema flag.

## Output format

```markdown
# Agent loop design: <runner name>

## Termination
- Max iterations: <n>
- Stop when: <conditions>
- No-progress rule: <rule>

## Tool execution
- Parallelism: <policy>
- Retry: <classes, max, backoff>

## History policy
- Token budget: <n>
- Prune strategy: <summary>

## Observability
- Per-iteration logs: <fields per observability-designer>

## Error code table
| Code | Layer | Retryable | User-facing |
|------|-------|-----------|-------------|
| <e.g. path_outside_root> | tool/fs | no | ... |
| <e.g. validation_error> | registry | no | ... |
| <e.g. rate_limited> | llm | yes | ... |

Canonical taxonomy and registry mapping: tool-registry-architect § Error taxonomy. CLI exit codes: typescript-cli-architect.

## Test hooks
- Fake transport: <yes/no>
```

## Escalation

- Greenfield agent/CLI order: `typescript-cli-architect/reference.md` (composition chain).
- Ask provider tool-call format (Anthropic, OpenAI, custom) if message shape is unknown.
- Ask required latency vs cost tradeoff before aggressive parallelization.
- Proceed with conservative caps when limits unspecified; document assumptions.
