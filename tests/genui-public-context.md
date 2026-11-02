# Public GenUI Lab context snapshot

Verified on 2026-10-30 at `9a596eb15b16502ea1248d04450ec0a21afb171b`. This is an observed context example for the same shared integration/frontend workflows; it does not install or execute that repository.

- Instructions: root AGENTS.md → GLOSSARY.md → docs/adr → docs/design/roadmap.md → relevant milestone design. Use the project's own vocabulary and milestone scope.
- Source owners: `packages/domain` for authoritative telemetry analysis; `packages/fixtures` for deterministic synthetic data; `packages/ui-contract` for controlled components/IDs; `packages/experiment-core` for runs/representation adapters; `packages/observability` for measured events; `packages/ag-ui-adapter` for simulated protocol events; `apps/web` for React rendering.
- Manifest: Node >=22, `pnpm@12.14.0`; lockfile `pnpm-lock.yaml`. Actual project tests use Vitest and Playwright. Do not install the synthetic fixture's node:test runner into GenUI Lab.
- Commands from repository root: `pnpm check` (lint, typecheck, tests, build), `pnpm test`, `pnpm test:e2e`; browser installation may be a separate prerequisite. These were **read**, not executed in this task.
- Relevant seams: `packages/domain/src/analyze.ts`, `packages/experiment-core/src/runner.ts`, `packages/ag-ui-adapter/src/telemetry-fixture-agent.ts`, `apps/web/e2e/experiment.spec.ts`.
- Acceptance for a fixture interaction: domain result retains synthetic source/units; shared-state approval/rejection is represented consistently; protocol and lab lifecycle events remain separate; unknown model timing/tokens/cost remain null/unavailable.
- Working modes: Markdown and tool UI. AG-UI interrupt/resume uses an in-process fixture agent. Live model integration and other declarative modes remain planned at the inspected commit. A socket reconnect test would require new transport scope.
- Restrictions: synthetic data only; no employer/customer records, no invented model measurements, no claim of satellite operations. No model key is needed for the implemented fixture path.

Sources: [package.json](https://github.com/Ensive/genui-lab/blob/9a596eb15b16502ea1248d04450ec0a21afb171b/package.json), [AGENTS.md](https://github.com/Ensive/genui-lab/blob/9a596eb15b16502ea1248d04450ec0a21afb171b/AGENTS.md), [roadmap](https://github.com/Ensive/genui-lab/blob/9a596eb15b16502ea1248d04450ec0a21afb171b/docs/design/roadmap.md), [browser tests](https://github.com/Ensive/genui-lab/blob/9a596eb15b16502ea1248d04450ec0a21afb171b/apps/web/e2e/experiment.spec.ts).
