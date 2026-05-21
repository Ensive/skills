---
name: program-performance-optimizer
description: >-
  Optimizes programs by measuring first, identifying hot paths, and applying async
  I/O, caching tiers, and batching with ROI-ranked recommendations—never trading
  away correctness or security for speed. Use when the user says "slow", "optimize",
  "performance", "benchmark", "latency", "make it faster", "faster file reads",
  "cache realpath", or "agent read tools slow". For safe FS caching see
  secure-filesystem-access scoped realpath cache. Not for removing path guards,
  skipping realpath checks, or bypassing capability gates for speed.
---

# Program Performance Optimizer

## When to use

- User reports slow CLI, agent loop, API handler, or batch job.
- User asks to reduce latency, memory, or CPU without a baseline measurement.
- User considers caching, pooling, parallel I/O, or removing await chains.
- User wants ROI-ranked changes before a large refactor.
- User proposes skipping validation or security checks for speed (must refuse).
- User wants faster agent file-read tools without dropping path guards — load secure-filesystem-access and apply only its scoped realpath cache; never remove prefix guards, `realpath`, or fd-stat.
- User asks to speed up reads without weakening security — measure first (this skill), then implement the per-request cache from secure-filesystem-access; refuse shortcuts that skip validation.

## Core principles

1. Measure before changing; capture baseline p50/p95 and resource use.
2. Profile hot paths; optimize what evidence shows, not assumptions.
3. Prefer async I/O and streaming over loading whole files into memory.
4. Cache only with explicit invalidation, bounds, and hit-rate rationale.
5. Batch network and disk operations when latency dominates per-call overhead.
6. Rank recommendations by impact, effort, and risk; do highest ROI first.
7. Never weaken correctness, authZ, or security for performance (see typescript-security-auditor).
8. Preserve deterministic tests; avoid flaky timing-dependent assertions.
9. Document tradeoffs when accepting higher memory for lower latency.
10. Agent token costs are a budget dimension; see agentic-loop-engineer for history pruning.

## Checklist

- [ ] Reproduce slowness with a minimal scenario and record environment (runtime, hardware).
- [ ] Capture baseline metrics: wall time, CPU, memory, I/O wait, network round trips.
- [ ] Identify top 3 hotspots via profiler, logs, or tracing spans.
- [ ] Classify bottleneck: CPU, sync I/O, lock contention, network, token/context size.
- [ ] Propose changes with estimated impact and implementation cost.
- [ ] Verify optimizations with A/B timing on the same fixture inputs.
- [ ] Check regressions in unit and integration tests after each change.
- [ ] Confirm security and validation paths remain intact post-change.
- [ ] Add guards (timeouts, size caps) where optimization introduced buffering.
- [ ] Stop when p95 meets target; avoid premature micro-optimizations.

## Patterns

**Baseline harness**

```typescript
const t0 = performance.now();
await runScenario(fixture);
console.error(`scenario_ms=${(performance.now() - t0).toFixed(1)}`);
```

**Async parallel independent I/O**

```typescript
const [a, b] = await Promise.all([readA(), readB()]);
```

**Bounded LRU cache**

```typescript
import { LRUCache } from "lru-cache";

const cache = new LRUCache<string, Buffer>({
  max: 100,
  maxSize: 10 * 1024 * 1024,
  sizeCalculation: (buf) => buf.byteLength,
});
```

If a runtime dependency is undesirable, use a `Map` with manual eviction at insert time — cap both entry count and total bytes and document the eviction policy.

**Batch API calls**

```typescript
const chunks = chunk(items, 50);
for (const c of chunks) await client.batch(c);
```

**Stream large file**

```typescript
const stream = createReadStream(path, { highWaterMark: 64 * 1024 });
```

## Anti-patterns

- **Optimizing without measurements** — wrong target; profile first.
- **Sync `readFileSync` on request path** — blocks event loop; use async/stream.
- **Unbounded in-memory caches** — OOM; cap entries and bytes.
- **Removing authZ or path checks for speed** — vulnerability; reject change.
- **Removing `realpath`, prefix guards, or fd-stat from FS tools for speed** — symlink and TOCTOU regressions; reject. Use the scoped `realpath` cache pattern in secure-filesystem-access (per-request, invalidated on writes) to recover the cost safely.
- **Micro-optimizing cold paths** — noise; focus on proven hotspots.
- **Parallelizing without understanding ordering** — races; see agentic-loop-engineer.

## Output format

```markdown
# Performance report: <scope>

## Baseline
- Scenario: <description>
- p50 / p95: <ms>
- Bottleneck class: <cpu|io|network|tokens>

## Hotspots
1. <location> — <evidence>

## Recommendations (ROI order)
| # | Change | Impact | Effort | Risk |
|---|--------|--------|--------|------|
| 1 | ... | high | low | low |

## Applied changes
- <file>: <what> — delta: <before → after>

## Verification
- Tests: <pass/fail>
- New metrics: <numbers>

## Deferred
- <item and why>
```

## Escalation

- Ask target SLO (p95 ms, memory cap) if missing.
- Ask whether correctness-critical paths may change behavior.
- Refuse proposals that skip security validation; offer safe alternatives.
