---
name: typescript-refactoring-architect
description: >-
  Plans and executes behavior-preserving TypeScript refactors for modularity and
  reusability: existing coverage or focused characterization, small mechanical steps, module
  boundary and public-export discipline, dependency direction, dead-code and
  circular-dep detection, generic-type reusability, dependency injection at
  adapter seams, and codemods via ts-morph or jscodeshift. Use when the user
  says "refactor", "make it modular", "make it reusable", "decouple", "extract
  function", "split module", "DRY", "clean up", "improve design", "reduce
  duplication", or "rename a public API safely". For the security pass see
  typescript-security-auditor; for performance see program-performance-optimizer.
---

# TypeScript Refactoring Architect

## Project discovery

Read applicable project instructions, manifests, nearby code/tests and CI. Discover paths, runtime, contracts, data restrictions and commands with working directories. Preserve existing stack choices; adapt the examples to those conventions. Use a reversible step when context is incomplete; ask only when behavior or authorization blocks it. Optional neighbors are not prerequisites.

## When to use

- User asks to refactor, decouple, or modularize existing TS code without changing behavior.
- User wants reusable abstractions (generics, branded types, dependency injection) extracted from concrete code.
- User has a god-module, deep barrel re-exports, or circular dependencies they want to untangle.
- User plans a rename, move, or signature change on a public API and needs a safe migration path.
- User asks "is this DRY?" or "where should this live?" and needs a boundary decision, not a perf or security pass.

## Core principles

1. Identify behavior at risk and existing coverage. Add focused characterization only for uncovered affected behavior (see typescript-unit-tester); a mechanical change does not require a new test scaffold.
2. One refactor per commit: no feature work, no formatting churn, no dependency bumps mixed in. Diff must be reviewable.
3. Smallest mechanical step that still compiles and tests pass: extract, inline, rename, move — one at a time.
4. Discover the project’s dependency boundaries and preserve them. A CLI composition example is not the default architecture for React, services or libraries.
5. Find actual consumers before changing exports. Preserve or deprecate externally consumed APIs according to the project's compatibility policy; update internal-only consumers together. An exported symbol is not automatically a published API.
6. Reusability comes from removing implicit coupling (hidden globals, `process.env` reads, `Date.now()`, singletons), not from inventing abstract base classes.
7. Generics earn their keep: introduce a type parameter only when there are two real call sites that disagree on a concrete type. Otherwise inline.
8. Prefer parameter objects over positional arguments past arity 3; prefer discriminated unions over optional-flag soup.
9. Codemods (ts-morph, jscodeshift) for mechanical edits across more than ~10 sites; manual edits below that threshold.
10. Refactoring never weakens validation, capability gates, or path guards (see typescript-security-auditor, secure-filesystem-access). If a refactor removes a check, the check moves; it does not disappear.

## Checklist

- [ ] Identify existing checks for affected behavior; add focused characterization where the change exposes a meaningful gap.
- [ ] Run relevant baseline checks and record pre-existing failures or unavailable checks.
- [ ] Identify the smallest reversible step and a stopping condition (e.g., "extract `parseHeader` and inline call sites; stop after green").
- [ ] Audit the export surface: list which symbols are public, internal, or accidentally public via a barrel.
- [ ] Map dependency direction with existing tooling over the discovered source roots, or inspect imports directly if no tool is installed.
- [ ] Check consumers before deleting exports; use the project's installed dead-code tools if available.
- [ ] For each extracted function, confirm it is pure or document its side-effects explicitly.
- [ ] For each new generic, confirm at least two distinct concrete instantiations exist or are scheduled in the same change set.
- [ ] For externally consumed symbols, follow the project's compatibility policy; add a deprecated re-export only when that policy needs one.
- [ ] After meaningful steps, run checks affected by the change. Run broader build/type/integration checks when required by the repository or changed contracts; avoid repeating unrelated suites mechanically.
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

These tests pin externally observable behavior; once the refactor is done, decide deliberately whether to keep, generalize, or delete them.

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

- **Refactor without characterization tests** — use existing coverage or add focused characterization where behavior is at risk; explain unverified behavior when tests cannot run.
- **Mixing refactor with feature work or formatting** — unreviewable diffs; split commits.
- **Speculative generality** ("we might need this later") — adds surface area for no current consumer; inline until a second site exists.
- **Abstract base classes for code reuse** — couples lifecycle to inheritance; prefer composition + small interfaces.
- **Deep barrel re-exports** (`export * from "./*"` everywhere) — destroys tree-shaking and makes public-vs-internal invisible; curate the public barrel by hand.
- **Changing an external contract without checking consumers** — follow the compatibility policy; internal-only renames can update all callers in the same change.
- **Removing validation/capability checks "because the refactor moved them"** — checks must move with the data, not vanish; verify with the security auditor.
- **Introducing a generic for a single concrete call site** — extra noise; inline and revisit when a second case appears.
- **Folder reorganization without checking dependency direction** — inspect the affected import graph or run the existing cycle check.

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

- Inspect package version and consumers before changing public APIs; ask only if compatibility requirements cannot be established.
- Infer the intended boundary from existing contracts; ask only if the requested structural change cannot be bounded. Use the CLI composition example solely for CLI work.
- Refuse refactors that propose removing validation, capability gates, or path guards for "cleanliness"; route to typescript-security-auditor instead.
- Add focused tests when thin coverage leaves affected behavior at risk; document what remains unverified if checks cannot run.

## Tools and verification

Use existing tools and synthetic fixtures within the task's authorization. If execution is unavailable, provide the check and mark it unexecuted. Report changed artifacts, assumptions, exact commands/cwd, results and remaining gaps; verify the affected success/failure boundary and project conventions. Examples do not authorize downloads or external mutations.

## Handoffs

Required sibling skills: none. Local references are implementation examples, included with this skill.

- Optional: `typescript-unit-tester` — Cover behavior at risk with existing tests or focused characterization at changed TypeScript seams.
- Optional: `integration-tester` — Verify affected integration contracts.
- Optional: `typescript-security-auditor` — Review changed authorization or validation boundaries.
- Optional: `secure-filesystem-access` — Preserve filesystem policy when moving code.
- Optional: `program-performance-optimizer` — Measure hot paths when performance is part of the task.
- Optional: `typescript-cli-architect` — Use the CLI composition example only for CLI work.
