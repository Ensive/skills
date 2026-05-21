---
name: typescript-unit-tester
description: >-
  Writes and reviews TypeScript unit tests using bun:test or Vitest with AAA structure,
  mocks and spies, deterministic time/random/fs, clear naming, and coverage targets.
  Use when adding tests, characterization tests, golden characterization before refactor,
  "unit test", "mock", "vitest", "bun test", or "coverage". Not for full agent/CLI
  e2e transcripts, fake LLM transports, or golden CLI output — use integration-tester.
---

# TypeScript Unit Tester

## When to use

- User adds or fixes unit tests for TS modules, parsers, or pure functions.
- User chooses between Bun test runner and Vitest for a project.
- User needs mocks for `fetch`, filesystem, clock, or randomness.
- User asks for naming conventions, AAA layout, or coverage goals.
- User has flaky tests due to timers, dates, or unordered assertions.

## Runner selection

If both Bun and Vitest configs exist:

1. Prefer the runner already used in colocated `*.test.ts` files (check imports: `bun:test` vs `vitest`).
2. Else if `bun.lockb` or `bunfig.toml` exists → `bun:test`.
3. Else if `vitest.config.*` exists → Vitest.
4. Else ask once; default Vitest for Node-only repos.

## Core principles

1. One behavior per test; name describes scenario and expected outcome.
2. Arrange-Act-Assert structure with blank lines between phases.
3. Prefer testing public API; avoid testing private implementation details.
4. Mock at boundaries (I/O, network, clock), not every internal call.
5. Freeze time and RNG in tests that depend on them.
6. No network or disk in unit tests unless explicitly isolated with fakes.
7. Deterministic assertions: exact match over loose snapshots unless reviewing UI text.
8. Coverage targets: critical paths high; generated boilerplate excluded thoughtfully.
9. Keep unit tests fast enough to run on every save (typical target: sub-second per changed file's suite). If a test approaches integration scope, move it to integration-tester.
10. End-to-end agent flows belong in integration-tester, not here.

## Checklist

- [ ] Pick runner per **Runner selection** above; confirm CI command matches (`bun test` vs `vitest run`).
- [ ] Colocate tests as `*.test.ts` or `__tests__/` per repo convention.
- [ ] Name tests: `it("does X when Y")` or `test("returns Z given W")`.
- [ ] Use AAA with single logical assertion group per behavior.
- [ ] Mock external I/O with `mock`, `spyOn`, or injectable interfaces.
- [ ] Use fake timers (`vi.useFakeTimers` / Bun equivalent) for scheduled code.
- [ ] Reset mocks in `afterEach` to prevent bleed across tests.
- [ ] Avoid real `fetch`; stub with fixed Response objects.
- [ ] Run coverage locally; note gaps on security and error branches.
- [ ] Ensure tests pass in CI without TTY or env secrets.

## Patterns

**AAA with bun:test**

```typescript
import { describe, expect, it, mock } from "bun:test";

describe("parseArgs", () => {
  it("returns help when -h passed", () => {
    const log = mock(() => {});
    const code = runCli(["-h"], { log });
    expect(code).toBe(0);
    expect(log).toHaveBeenCalledWith(expect.stringContaining("Usage"));
  });
});
```

**Vitest module mock**

```typescript
import { vi } from "vitest";
vi.mock("./client", () => ({
  complete: vi.fn().mockResolvedValue({ text: "ok" }),
}));
```

**bun:test module mock (set BEFORE importing the SUT)**

```typescript
import { mock } from "bun:test";

mock.module("./client", () => ({
  complete: mock(() => Promise.resolve({ text: "ok" })),
}));

const { runOnce } = await import("./under-test");
```

Bun's `mock.module` does *not* hoist like Vitest's `vi.mock`. Register the mock first, then dynamically import the module under test, or the real module will already be in the ESM cache.

**Fake timers — Vitest**

```typescript
vi.useFakeTimers();
vi.setSystemTime(new Date("2020-01-01T00:00:00Z"));
vi.runAllTimers();
vi.useRealTimers();
```

**Fake timers — bun:test**

```typescript
import { setSystemTime } from "bun:test";

setSystemTime(new Date("2020-01-01T00:00:00Z"));
// run code that calls Date.now()
setSystemTime(); // reset to real time
```

Bun's timer-mocking surface is narrower than Vitest's. If you need `runAllTimers`-style fast-forward of `setTimeout`/`setInterval`, inject a clock via the pattern below instead of relying on the runner.

**Injectable clock**

```typescript
export type Clock = () => number;
export function expire(ts: number, now: Clock = () => Date.now()) {
  return now() > ts;
}
```

## Anti-patterns

- **Testing private functions via re-export hacks** — brittle; test public contract.
- **Shared mutable state between tests** — order-dependent flakes; reset each test.
- **Real network calls in unit suite** — slow and flaky; stub transport.
- **Huge snapshot of entire objects** — opaque failures; assert key fields.
- **Sleep-based waiting** — flaky; use fake timers or await known promises.
- **Duplicating production logic in assertions** — copy-paste bug; assert outcomes.
- **Importing the SUT before `mock.module` (Bun)** — real module caches; test hits network/disk. Register mock first, then `await import("./under-test")`.

## Output format

```markdown
# Unit test plan: <module>

## Runner
- Tool: bun:test | vitest
- Command: `<cmd>`

## Cases
| Test name | Arranges | Acts | Asserts |
|-----------|----------|------|---------|
| ... | ... | ... | ... |

## Mocks
- <boundary>: <strategy>

## Coverage
- Target: <percent or critical paths>
- Gaps after run: <files/lines>

## Files touched
- `<path>`
```

## Escalation

- Ask preferred runner if repo has both Bun and Vitest configs.
- Ask coverage threshold if CI enforces thresholds.
- Proceed with matching existing test file style when convention is visible.
