---
name: frontend-contract-engineer
description: Implement or repair an existing frontend or publishing interface from explicit state, content and interaction contracts. Use for accessible UI states, controlled generated components, telemetry views and article layouts; exclude backend orchestration, model-provider integration and editorial ghostwriting.
---

# Frontend Contract Engineer

## When to use

Turn an existing design/content requirement into a working interface with clear state ownership and accessible behavior. Own presentation, interaction and component contracts. For a writing site, preserve supplied prose and voice. For GenUI, validate representations without allowing them to become domain truth. Do not introduce AI, a backend or a new framework unless the task requires it.

## Discover and decide

Read applicable project instructions, framework/package versions, routes, nearby components, design tokens, content schemas, domain vocabulary and tests. Identify the authoritative state/content owner, supported interactions, target viewports and accessibility expectations. Record commands/cwd from the repository. Reuse current components and styling; default to semantic HTML for static content.

Missing design polish can use existing tokens. Missing behavior for a destructive action or permission to publish blocks that action; it does not block a local rendering change. If no code is available, deliver a contract and implementation sketch, not a claim of a working interface.

## Workflow

1. Produce a **UI contract**: source of truth, rendered fields, units/provenance, stable identities, allowed actions and state transitions. Distinguish loading, empty, success, partial, error and cancelled states only where applicable.
2. Choose the smallest implementation within existing boundaries. For React/generated UI use [state and schema guidance](references/react-genui.md); for reading/publishing use [content and layout guidance](references/publishing.md). Read only the relevant branch.
3. Implement validated inputs at the boundary and actions through the state owner's API. Preserve identity on reorder/patch, reject unsupported components/actions and avoid stale responses overwriting new state. Plain static content needs no artificial state machine.
4. Make controls semantic and keyboard reachable; keep focus visible and labels/errors associated. Pair charts with readable summaries/tables, units and provenance. Label simulated data and avoid causal claims unsupported by evidence.
5. Produce **interface changes** plus focused **interaction checks** for success and a meaningful failure/empty state. Verify reading order, responsive layout, zoom and keyboard flow with a browser when available; preserve supplied editorial text.
6. Run project checks and report exact commands, observed outcomes and unverified visual/assistive-technology behavior. Publishing or deploying is a separate authorized action.

## Tools and acceptance

Needs repository read/edit tools; browser access improves interaction/layout verification. Without a browser, run available structural/component checks and explicitly leave visual, keyboard and screen-reader checks unverified. External design tools are optional, not required integrations.

Accept when source state remains authoritative, actions respect its contract, content/units/provenance survive rendering, and available checks cover the requested change. Watch for index keys, arbitrary executable generated markup, false zero values for unknown metrics, color-only alerts and copy rewrites hidden in a layout change.

## Handoffs

Required sibling skills: none.

- Optional: `integration-tester` — Verify UI/API wiring, replay or browser flows.
- Optional: `observability-designer` — Instrument real interaction and rendering outcomes.
- Optional: `typescript-unit-tester` — Test an isolated TypeScript state/schema helper.
- Optional: `llm-client-architect` — Implement an explicitly requested model-provider adapter.
