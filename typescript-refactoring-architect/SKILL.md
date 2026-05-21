---
name: typescript-refactoring-architect
description: >-
  Plans and executes behavior-preserving TypeScript refactors for modularity and
  reusability: characterization tests first, small mechanical steps, module
  boundary and public-export discipline, dependency direction, dead-code and
  circular-dep detection, generic-type reusability, dependency injection at
  adapter seams, and codemods via ts-morph or jscodeshift. Use when the user
  says "refactor", "make it modular", "make it reusable", "decouple", "extract
  function", "split module", "DRY", "clean up", "improve design", "reduce
  duplication", or "rename a public API safely". For the security pass see
  typescript-security-auditor; for performance see program-performance-optimizer.
---

# TypeScript Refactoring Architect

## When to use

- User asks to refactor, decouple, or modularize existing TS code without changing behavior.
- User wants reusable abstractions (generics, branded types, dependency injection) extracted from concrete code.
- User has a god-module, deep barrel re-exports, or circular dependencies they want to untangle.
- User plans a rename, move, or signature change on a public API and needs a safe migration path.
- User asks "is this DRY?" or "where should this live?" and needs a boundary decision, not a perf or security pass.

## Core principles

1. Behavior first: write characterization tests that pin current behavior before any structural change (see typescript-unit-tester).
2. One refactor per commit: no feature work, no formatting churn, no dependency bumps mixed in. Diff must be reviewable.
3. Smallest mechanical step that still compiles and tests pass: extract, inline, rename, move — one at a time.
4. Dependency direction follows the composition chain (config → cli → loop → registry → tools → fs/llm adapters). Higher layers may import lower; never the reverse.
5. Public exports are an interface. Renames and signature changes on exported symbols require a deprecation window (re-export with a typed deprecation tag) unless the package is pre-1.0 and the change is documented.
6. Reusability comes from removing implicit coupling (hidden globals, `process.env` reads, `Date.now()`, singletons), not from inventing abstract base classes.
7. Generics earn their keep: introduce a type parameter only when there are two real call sites that disagree on a concrete type. Otherwise inline.
8. Prefer parameter objects over positional arguments past arity 3; prefer discriminated unions over optional-flag soup.
9. Codemods (ts-morph, jscodeshift) for mechanical edits across more than ~10 sites; manual edits below that threshold.
10. Refactoring never weakens validation, capability gates, or path guards (see typescript-security-auditor, secure-filesystem-access). If a refactor removes a check, the check moves; it does not disappear.

## Checklist

- [ ] Confirm a characterization test suite exists for the target. If not, write one *before* refactoring.
- [ ] Run the full test suite green; record baseline coverage on the changing files.
- [ ] Identify the smallest reversible step and a stopping condition (e.g., "extract `parseHeader` and inline call sites; stop after green").
- [ ] Audit the export surface: list which symbols are public, internal, or accidentally public via a barrel.
- [ ] Map dependency direction: `npx madge --circular src/` (or `pnpm exec madge --circular src/`). If unavailable, document a manual import-graph review in the plan output.
- [ ] Detect dead code: `npx knip` or `npx ts-prune`. If unavailable, grep for unreferenced exports before deleting.
- [ ] For each extracted function, confirm it is pure or document its side-effects explicitly.
- [ ] For each new generic, confirm at least two distinct concrete instantiations exist or are scheduled in the same change set.
- [ ] For each renamed/moved public symbol, add a deprecated re-export from the old path/name with a JSDoc `@deprecated` tag.
- [ ] After each step: build, type-check, run unit tests, run integration tests (see integration-tester) — in that order.
- [ ] Re-run the security and perf passes if the refactor touched FS, LLM client, or hot paths.

## Patterns

**Characterization test before refactor**

```typescript
import { describe, it, expect } from "bun:test";
import { handle } from "./handler";

describe("handle (characterization)", () => {
  it("returns the current shape for the canonical input", async () => {
    expect(await handle({ kind: "read", path: "a.txt" })).toEqual({
      ok: true,
      bytes: 12,
      hash: "sha256:...",
    });
  });
});
```

These tests are intentionally tied to the current implementation; once the refactor is done, decide deliberately whether to keep, generalize, or delete them.

**Dependency injection at the seam (reusability without inheritance)**

```typescript
export interface Clock { now(): number; }
export const systemClock: Clock = { now: () => Date.now() };

export function withinTtl(deadline: number, clock: Clock = systemClock): boolean {
  return clock.now() < deadline;
}
```

The default keeps call sites unchanged; tests inject a fake clock. Same shape works for `Fs`, `Fetcher`, `Logger` — the seams already named in sibling skills.

**Discriminated union over flag soup**

```typescript
type ReadOp =
  | { kind: "text"; path: string; maxBytes: number }
  | { kind: "binary"; path: string; maxBytes: number }
  | { kind: "meta"; path: string };

function run(op: ReadOp) {
  switch (op.kind) {
    case "text":   return readText(op.path, op.maxBytes);
    case "binary": return readBinary(op.path, op.maxBytes);
    case "meta":   return stat(op.path);
    default: {
      const _exhaustive: never = op;
      return _exhaustive;
    }
  }
}
```

The `never` arm makes future variants a compile-time failure rather than a runtime fallthrough.

**Generic earns its keep**

```typescript
export async function withTimeout<T>(
  promise: Promise<T>,
  ms: number,
  signal?: AbortSignal,
): Promise<T> { /* ... */ }

const text  = await withTimeout(readText(p, 64_000), 5_000, signal);
const stats = await withTimeout(stat(p), 1_000, signal);
```

Two distinct concrete `T`s at call sites — the generic is justified. If only one call site existed, inline it.

**Deprecation re-export during a rename**

```typescript
// src/fs/read-bounded.ts  (new home)
export { readBounded } from "./internal/read-bounded";

// src/fs/read.ts  (old home, kept one release)
/** @deprecated use readBounded from "./read-bounded" instead */
export { readBounded } from "./read-bounded";
```

Consumers see the deprecation in their IDE before the old path is removed.

**Codemod with ts-morph (mechanical rename across many sites)**

```typescript
import { Project, SyntaxKind } from "ts-morph";

const project = new Project({ tsConfigFilePath: "tsconfig.json" });
for (const sf of project.getSourceFiles("src/**/*.ts")) {
  sf.getDescendantsOfKind(SyntaxKind.CallExpression).forEach((c) => {
    if (c.getExpression().getText() === "oldName") {
      c.getExpression().replaceWithText("newName");
    }
  });
}
await project.save();
```

Use when more than ~10 sites change identically; commit the codemod script alongside the diff.

**Module-boundary review (public vs internal)**

```typescript
// src/llm/index.ts — the package's public surface
export type { ChatRequest, ChatResponse, LlmError } from "./types";
export { createClient } from "./client";
// no re-export of ./internal/*
```

Internal helpers live under `src/llm/internal/`; the barrel never re-exports them. Tests import from `./internal/...` directly when they need to.

## Anti-patterns

- **Refactor without characterization tests** — silent regressions; write tests first or refuse the refactor.
- **Mixing refactor with feature work or formatting** — unreviewable diffs; split commits.
- **Speculative generality** ("we might need this later") — adds surface area for no current consumer; inline until a second site exists.
- **Abstract base classes for code reuse** — couples lifecycle to inheritance; prefer composition + small interfaces.
- **Deep barrel re-exports** (`export * from "./*"` everywhere) — destroys tree-shaking and makes public-vs-internal invisible; curate the public barrel by hand.
- **Renaming a public export with no deprecation window** — breaks downstream; re-export from the old name for one release.
- **Removing validation/capability checks "because the refactor moved them"** — checks must move with the data, not vanish; verify with the security auditor.
- **Introducing a generic for a single concrete call site** — extra noise; inline and revisit when a second case appears.
- **Folder reorganization without updating dependency direction** — circular deps reappear; run `madge --circular` after each move.

## Output format

```markdown
# Refactor plan: <scope>

## Goal
- Modularity / reusability / both
- Non-goals: <e.g., behavior change, perf>

## Baseline
- Tests: <pass/fail, coverage on target files>
- Cycles: <madge result>
- Dead exports: <ts-prune/knip result>

## Steps (each step compiles + tests pass)
1. <smallest step, e.g., "extract parseHeader, inline call sites">
2. ...
N. <stopping condition>

## Public-API impact
| Symbol | Change | Deprecation path |
|--------|--------|------------------|

## Cross-skill follow-ups
- Security re-check: <yes/no, why>
- Perf re-check: <yes/no, why>
- Tests touched: <unit / integration>

## Rollback
- <how to revert if a step regresses>
```

## Escalation

- Ask whether the package is pre-1.0 (looser deprecation rules) or has external consumers (strict deprecation window).
- Ask the target architecture if "modular" is unspecified — typically the composition chain in `typescript-cli-architect/reference.md` is the right layering.
- Refuse refactors that propose removing validation, capability gates, or path guards for "cleanliness"; route to typescript-security-auditor instead.
- Proceed with characterization-test-first when the test suite is thin; flag the gap in the plan output rather than silently skipping.
