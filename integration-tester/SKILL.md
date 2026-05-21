---
name: integration-tester
description: >-
  Builds integration and end-to-end tests for agent systems using fake LLM transports,
  scripted LLM, fixture-driven tool harnesses, golden-file diffs, and flake control.
  Use when testing "agent e2e", tool loops, tool executor, test harness, golden files,
  "fake LLM", "fake transport", "scripted transport", or full CLI integration flows.
  Not for isolated unit tests of pure functions — use typescript-unit-tester.
---

# Integration Tester

## When to use

- User tests full agent loop: prompt, model response, tool execution, final answer.
- User needs fake LLM transport instead of live API in CI.
- User builds fixture JSON for tool inputs/outputs and expected transcripts.
- User compares CLI or agent output to golden files across versions.
- User fights flaky integration tests, ordering issues, or timing races.

## Core principles

1. Integration tests exercise real wiring with fakes only at external boundaries (LLM, network).
2. Fake transport returns scripted message sequences deterministically.
3. Tool harness uses fixtures for registry handlers; no live filesystem unless temp sandbox.
4. Golden files are reviewed intentionally; update only with explicit diff review.
5. Control time, randomness, and env the same way as typescript-unit-tester.
6. Isolate temp dirs per test; unique workspace roots (see secure-filesystem-access).
7. Assert on structured events (tool calls, exit codes), not full prose when possible.
8. Retry only for known infra flakes; default zero retries for agent transcripts.
9. Keep tests parallel-safe with separate temp roots and env overrides.
10. Unit-test pure helpers separately; do not duplicate unit coverage here.

## Checklist

- [ ] Define scenario: user message in, expected tools called, expected final state.
- [ ] Implement `FakeLlmTransport` with queue of assistant/tool messages.
- [ ] Register fixture tool handlers returning canned success/error payloads.
- [ ] Run agent runner with `MAX_ITERATIONS` low enough to fail fast on loops.
- [ ] Pass `AbortSignal` from harness; include at least one scenario that aborts mid-loop (SIGINT/cancel) and assert clean stop.
- [ ] Capture transcript artifact: messages, tool calls, timings (optional).
- [ ] Compare to golden with stable normalization (paths, timestamps stripped).
- [ ] Use temp directory per test; cleanup in `afterEach`.
- [ ] Set env via test harness, not developer `.env`.
- [ ] Serialize tests only when sharing global resource is unavoidable. Vitest: `test.sequential` or `describe.sequential`. bun:test: chain assertions inside one `describe` with shared setup/teardown (no `@serial` annotation exists in either runner).
- [ ] Call `transport.assertExhausted()` in `afterEach`. An agent that exits early leaves scripted steps unconsumed; without this assertion the test silently passes.
- [ ] Document how to refresh goldens: one command, requires human review.

## Patterns

**Fake LLM transport (with drain assertion)**

```typescript
type ScriptedStep = { role: "assistant"; content: string; toolCalls?: NormalizedToolCall[] };

function toLlmResponse(step: ScriptedStep): LlmResponse {
  const toolCalls = step.toolCalls ?? [];
  return {
    stopReason: toolCalls.length > 0 ? "tool_use" : "end_turn",
    toolCalls,
    text: step.content,
  };
}

export class FakeLlmTransport {
  private index = 0;
  constructor(private readonly queue: readonly ScriptedStep[]) {}

  async complete(): Promise<LlmResponse> {
    const step = this.queue[this.index++];
    if (!step) throw new Error(`unexpected complete() call #${this.index}`);
    return toLlmResponse(step);
  }

  get remaining(): number { return this.queue.length - this.index; }

  assertExhausted(): void {
    if (this.remaining !== 0) {
      throw new Error(`transport has ${this.remaining} unused scripted steps`);
    }
  }
}
```

Import `NormalizedToolCall` and `LlmResponse` from the project types module (default `src/agent/types.ts`; definitions in `agentic-loop-engineer/reference.md`).

**Fixture tool registry**

```typescript
registry.register("read_file", async (input) => {
  return fixtures.readFile[input.path] ?? { error: "file_not_found" };
});
```

**Golden diff with normalization (runner-agnostic)**

`toMatchFileSnapshot` is Vitest-only. Use a small helper that works under Vitest, bun:test, or node:test:

```typescript
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname } from "node:path";

function stableStringify(value: unknown): string {
  return JSON.stringify(value, (_k, v) =>
    v && typeof v === "object" && !Array.isArray(v)
      ? Object.fromEntries(Object.entries(v as object).sort(([a], [b]) => a.localeCompare(b)))
      : v, 2);
}

export async function assertGolden(actual: unknown, goldenPath: string): Promise<void> {
  const serialized = stableStringify(actual);
  if (process.env.UPDATE_GOLDENS === "1") {
    await mkdir(dirname(goldenPath), { recursive: true });
    await writeFile(goldenPath, serialized + "\n");
    return;
  }
  const expected = await readFile(goldenPath, "utf8");
  if (serialized + "\n" !== expected) {
    throw new Error(`golden mismatch: ${goldenPath}\nrun with UPDATE_GOLDENS=1 after review`);
  }
}

const actual = normalizePaths(stripTimestamps(await runScenario()));
await assertGolden(actual, "goldens/agent-basic.json");
```

**Temp workspace per test**

```typescript
const root = await mkdtemp(path.join(os.tmpdir(), "agent-test-"));
afterEach(async () => rm(root, { recursive: true, force: true }));
```

## Anti-patterns

- **Live API keys in CI integration tests** — cost and flake; use fake transport.
- **Asserting exact LLM prose wording** — brittle; assert structure and tool args.
- **Shared golden file mutated by parallel tests** — races; one temp root per test.
- **Fake transport without a drain check** — agents that exit early leave the queue partially consumed; the test passes for the wrong reason. Always call `assertExhausted()` (or assert `remaining === expected`) in teardown.
- **Sleep-based synchronization** — flake; await explicit promises or events.
- **Oversized golden files with noise** — review burden; normalize and trim.
- **Re-testing pure parsers here** — slow suite; unit test instead.

## Output format

```markdown
# Integration test pack: <feature>

## Scenarios
### <name>
- Input: <user message / argv>
- Scripted model steps: <count>
- Expected tools: <name, args>
- Expected exit/output: <summary>

## Fixtures
- `<path>`: <purpose>

## Goldens
- `<path>`: update via `<command>`

## CI
- Command: `<cmd>`
- Env: <vars set in test>

## Flake controls
- <timers, retries, serial flags>
```

## Escalation

- Ask whether live API smoke tests are required outside CI (nightly only).
- Ask golden update policy if large diffs expected after prompt changes.
- Proceed with fake transport when provider is unspecified.
