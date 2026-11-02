---
name: observability-designer
description: Design logs, metrics and traces for browser, service, CLI and AI workflows in TypeScript or Python. Use for request correlation, event contracts, redaction, usage attribution and diagnostic gaps; exclude provider transport implementation and optimization without measurements.
---

# Observability Designer

## When to use

Instrument a workflow so an operator can explain its outcome, latency and failure. Own event semantics, correlation, redaction at export, metrics and trace boundaries. Provider retries belong to llm-client-architect; measured optimization belongs to program-performance-optimizer. Instrument only layers that exist.

## Discover and decide

Read applicable instructions, manifests, current logger/tracer, dashboards, tests and deployment configuration. Record the diagnostic question, execution boundaries, approved sink, retention/data restrictions and correlation convention. Preserve event names and units. Read [runtime recipes](references/runtimes.md) for the relevant runtime only.

Default to minimal metadata and existing instrumentation. Use an in-memory collector for offline experiments. A CLI may use stderr NDJSON; a container service may collect stdout; a browser needs explicit context and an approved collector. Missing credentials do not block a local contract. Unknown permission to export user data blocks export, not local design.

## Workflow

1. Produce an **event contract** mapping user-visible outcomes to start, progress and terminal events, required fields and owners. Represent cancellation, failure and incomplete streams separately from success.
2. Choose propagation at each boundary: explicit IDs, Node AsyncLocalStorage, Python contextvars or existing tracing context. Process-local context does not automatically cross HTTP, queues or browser callbacks.
3. Define bounded metric labels, units and aggregation. Request/user IDs belong in authorized logs/traces, not metric dimensions; hashing does not reduce cardinality. Measure durations with a monotonic clock and wall time separately.
4. Apply an export allowlist and shared project redaction before persistence. Keep content, credentials and raw exception bodies out by default, including debug mode. Test nesting, URLs, headers and errors using synthetic sentinel secrets.
5. For model calls, attribute provider/model, attempt, request/run and terminal status. Separate reported, estimated and unavailable usage. Never turn missing usage into zero or invent tokens, TTFT or cost for fixture-only runs. Prices need source/date/currency; avoid counting cumulative chunks or retries twice.
6. Produce **instrumentation changes** and a **verification report**: run discovered checks; exercise concurrent requests, error/cancel paths, redaction and schema compatibility. Report sampling, drop/flush policy and remaining diagnostic gaps.

## Tools and acceptance

Read access supports a plan. Local edits/tests use host permissions; production queries and exporters require authorized access. Without a collector, assert captured local events and document the untested delivery path.

Accept when failed runs can be correlated without sensitive payloads, concurrent runs stay isolated, spans close on failure/cancel, cardinality is bounded and absent measurements stay absent. Watch for unbounded queues, blocking exporters, duplicate spans and debug switches that bypass privacy policy.

## Handoffs

Required sibling skills: none.

- Optional: `llm-client-architect` — Instrument provider attempts and normalize reported usage.
- Optional: `agentic-loop-engineer` — Emit loop progress and terminal reasons.
- Optional: `tool-registry-architect` — Emit authorized invocation outcomes.
- Optional: `integration-tester` — Verify event ordering and correlation through application wiring.
- Optional: `program-performance-optimizer` — Investigate measured latency or resource bottlenecks.
