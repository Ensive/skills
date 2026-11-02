# React, generated UI and telemetry

Use the project's installed React and schema libraries. Domain state belongs in its existing store/service; presentation state such as an expanded panel can remain local. Derive display values from authoritative data rather than maintaining a second synchronized copy.

For generated components, define a controlled vocabulary of component names, prop schemas, stable IDs and permitted actions. Validate depth/node counts and payload size before rendering. Unknown components get a safe error/fallback. Never evaluate generated JavaScript, accept arbitrary event handlers or let a generated label imply authorization.

Keep protocol adapters separate from presentation: an AG-UI event transport is not the same boundary as an A2UI or component-tree renderer. Translate at an explicit seam, preserving source IDs and schema version. Define whether updates replace or patch state and how stale/out-of-order updates are rejected. An interrupt/resume fixture does not establish network recovery.

For a time-series chart, document timestamp timezone, sampling interval, units, missing values and aggregation. Use stable series/point identities; do not connect gaps as if samples existed. Add a text summary or table and distinguish observed deviation from inferred cause. Synthetic scenarios should include provenance, a deterministic seed or explicit values, baseline behavior and known anomalies. A satellite-themed fixture is simulated data, not operational telemetry.

Verify: rejected props leave domain state unchanged; patching preserves focus where appropriate; stale updates cannot overwrite the latest result; errors and empty results are visible without relying on color; summary/table values match the chart. Do not invent model metrics for deterministic renderers.

Sources checked 2026-10-30: [React state structure](https://react.dev/learn/choosing-the-state-structure), [WAI page structure](https://www.w3.org/WAI/tutorials/page-structure/). Framework-specific generated-UI APIs require separate verification against the selected dependency.
