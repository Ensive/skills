---
name: agentic-loop-engineer
description: >-
  Engineers reliable agent tool-calling loops with iteration caps, parallel vs
  sequential execution, tool-class retry classification, tool-error shaping,
  history growth control, token budgets, and deterministic termination. Use when
  building an agent runner, agent harness, ReAct loop, tool dispatcher, "tool
  loop", "max iterations", "parallel tool calls", "why is my agent looping",
  tool errors, or "when to stop the agent". HTTP 429/5xx and provider retries:
  llm-client-architect only. Tool-result recovery and tool-class
  backoff belong here; argument validation, schemas and capability flags belong to
  tool-registry-architect.
---

# Agentic Loop Engineer

## Project discovery

Read applicable project instructions, manifests, nearby code/tests and CI. Discover paths, runtime, contracts, data restrictions and commands with working directories. Preserve existing stack choices; adapt the examples to those conventions. Use a reversible step when context is incomplete; ask only when behavior or authorization blocks it. Optional neighbors are not prerequisites.

## When to use

- User implements a while-loop that calls LLM then executes tools until done.
- User hits runaway loops, duplicate tool calls, or unbounded message history.
- User needs parallel tool calls vs strict ordering for dependent steps.
- User shapes tool errors for model recovery without leaking stack traces.
- User asks about token limits, summarization, or stopping conditions for agents.

## Core principles

1. Cap iterations explicitly; every loop has a max count and a no-progress breaker.
2. Terminate on the project’s explicit completion signal, cancellation, exhausted budget/cap, no-progress breaker or unrecoverable failure; report the actual reason.
3. Run independent tools in parallel; serialize when outputs are inputs to next step.
4. Retry only failures known safe to repeat within a total deadline and attempt cap; a timeout can leave an unknown side effect. Never automatically retry invalid arguments.
5. Return tool errors as structured, concise strings; omit internal paths unless policy allows.
6. Trim or summarize history when approaching context limits; preserve system + latest user goal.
7. Deduplicate identical tool calls within the same turn when safe.
8. Record token usage per iteration for budget alerts and downgrade paths.
9. Make termination conditions testable without live LLM calls when possible.
10. Keep prompts and roles in prompt-engineer; provider HTTP and HTTP-layer retry/backoff in llm-client-architect.
11. Reuse the target project’s tool-call/result contracts. [reference.md](reference.md) contains a TypeScript example, not mandatory types or a directory layout. Provider adapters and tools agree at that project boundary.

## Checklist

- [ ] Define `MAX_ITERATIONS` and `MAX_TOOL_CALLS_PER_TURN` constants in config.
- [ ] Implement no-progress detection (same tool+args repeated N times).
- [ ] Classify tool results: success, retryable, fatal, user-input-required.
- [ ] Apply backoff only to retryable classes with capped attempts per tool id.
- [ ] Batch parallel calls when model returns multiple independent tool_use blocks.
- [ ] Append tool results immediately after assistant tool_use messages (API ordering rules).
- [ ] Prune or summarize messages before each LLM call when over token threshold.
- [ ] Expose abort via AbortSignal wired from SIGINT or cancel API.
- [ ] Emit iteration/terminal events through the project’s observability contract; choose sink and redaction there. NDJSON is a CLI example.
- [ ] Add integration tests with fake transport (see integration-tester).

## Patterns

Example TypeScript contracts and error mapping live in [reference.md](reference.md). Discover existing types before adding a module. The snippets below are sketches requiring project-specific helpers.

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

**Dedupe identical calls within one turn (read-only example)**

Only coalesce operations whose semantics permit it. Preserve a result for every original call ID, including duplicates; dropping IDs breaks provider message pairing. Never deduplicate mutations merely because their arguments match. This helper identifies representatives; the caller must fan results back to all original IDs.

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

// Candidate categories only: the caller must also establish safe repetition.
const RETRYABLE_CODES = new Set(["transient"]);

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
  safeToRepeat: boolean,
): Promise<NormalizedToolResult> {
  // Sketch: project sleep must support cancellation and the remaining deadline.
  let attempt = 0;
  while (attempt < MAX_TOOL_RETRIES) {
    const result = await run();
    const outcome = classify(result);
    if (outcome !== "retryable" || !safeToRepeat) return result;
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

- Optional CLI composition example: typescript-cli-architect, only for a new CLI; no sibling is required.
- Discover message contracts from existing adapters; ask only if the required boundary remains unknown.
- Use conservative bounded execution; resolve latency/cost tradeoffs only if the requested change depends on them.
- Proceed with conservative caps when limits unspecified; document assumptions.

## Tools and verification

Use existing tools and synthetic fixtures within the task's authorization. If execution is unavailable, provide the check and mark it unexecuted. Report changed artifacts, assumptions, exact commands/cwd, results and remaining gaps; verify the affected success/failure boundary and project conventions. Examples do not authorize downloads or external mutations.

## Handoffs

Required sibling skills: none. Local references are implementation examples, included with this skill.

- Optional: `llm-client-architect` — Own provider HTTP retries and protocol translation.
- Optional: `tool-registry-architect` — Own schemas, invocation authorization and result classification.
- Optional: `prompt-engineer` — Own prompt wording and roles.
- Optional: `observability-designer` — Define event correlation and export policy.
- Optional: `integration-tester` — Verify loop behavior through real wiring.
- Optional: `typescript-cli-architect` — Map terminal outcomes to CLI exits when a CLI exists.
