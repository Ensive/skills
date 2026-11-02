---
name: integration-tester
description: Design and run deterministic integration tests across real application boundaries in TypeScript or Python, including UI interactions, API contracts, agent flows and stream cancellation. Use for wiring regressions, scripted transports, replay and golden comparisons; exclude isolated helper tests and live-model quality evaluation.
---

# Integration Tester

## When to use

Test behavior crossing modules, browser/API boundaries, persistence or an agent transport. Own the scenario, fixture, harness and observable assertions. Isolated TypeScript helpers belong to typescript-unit-tester; probabilistic model quality needs a separate evaluation design. A publishing site can use this workflow without a backend or model.

## Discover and decide

Read applicable project instructions, manifests, lockfiles, CI and nearby tests before naming files or commands. Find the actual public seam and schemas. Record target behavior, expected state, command/cwd, data restrictions and external systems that may be replaced. Reuse the installed runner; language alone does not select Vitest or pytest.

Default to synthetic inputs, injected time and external-boundary fakes. Missing credentials do not block offline testing. Ask only when desired behavior or authority to touch a shared service cannot be established; continue local harness work.

## Workflow

1. Produce a **scenario table**: initial state, action, boundary, expected output/state and failure case. Include a negative case that must not call a provider or create infrastructure.
2. Keep application wiring real. Fake external nondeterminism; isolate temporary files, dependency overrides and database transactions per test. Use project domain types, not types imported from this catalog.
3. Implement a **test pack** using the relevant recipe: [TypeScript](references/typescript.md), [Python/FastAPI](references/python.md) or [browser/publishing](references/browser.md). Reject unexpected fake calls and verify consumed steps; cancelled runs assert the expected unconsumed remainder.
4. For streams, test fragmented frames, cancellation, partial failure and terminal-state delivery. Assert no post-cancel side effect, released resources and no duplicate action on replay. In-process cancellation is not real socket-disconnect coverage.
5. Compare semantic fields and ordering constraints. Normalize only nondeterministic IDs/times; preserve identity relationships, units, errors and event order. Review golden diffs before acceptance. Schema validity alone is insufficient.
6. Run the discovered focused command and relevant project checks. Produce **verification evidence**: exact cwd/commands, results, fixtures and gaps. Live-provider smoke tests and model evaluations are separate, authorized suites.

## Tools and acceptance

Repository read access supports a plan; editing and test execution use host permissions. Use installed dependencies and temporary resources. If a runtime/browser/service is unavailable, deliver runnable tests and the missing prerequisite, labelled unexecuted. Do not silently contact paid providers, migrate shared databases or update goldens.

Accept when real wiring exercises the intended path and a representative failure, early/extra scripted calls fail, resources are cleaned up, and no real credentials are needed. Watch for fakes bypassing the code under test, sleeps hiding races, snapshots erasing order and ASGI tests presented as network proof.

## Handoffs

Required sibling skills: none. Optional help is loaded only for a crossed boundary, when available.

- Optional: `typescript-unit-tester` — Test an isolated TypeScript helper.
- Optional: `secure-filesystem-access` — Repair a production filesystem guard.
- Optional: `agentic-loop-engineer` — Repair loop ordering, retries or termination.
- Optional: `llm-client-architect` — Repair provider transport or partial-stream behavior.
- Optional: `frontend-contract-engineer` — Repair UI state ownership or accessible interactions.
