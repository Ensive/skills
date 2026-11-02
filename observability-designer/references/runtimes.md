# Runtime-specific instrumentation

These are implementation examples. Keep the project's logger, event names and module layout. No catalog skill owns an executable `safeBody` module to import.

## Node / TypeScript

For server/CLI async context, Node AsyncLocalStorage can carry run metadata. Preserve nested context and establish it at each request boundary. Explicit parameter passing is also valid, especially in browser/shared packages.

```typescript
import { AsyncLocalStorage } from "node:async_hooks";
const context = new AsyncLocalStorage<{ runId: string }>();
export function withRun<T>(runId: string, fn: () => T): T {
  return context.run({ runId }, fn);
}
```

Do not import `node:async_hooks` into browser code. A CLI can emit one NDJSON event per stderr line without corrupting machine-readable stdout. Server sinks follow the collector contract; web experiments may retain events in memory. Bound queue size and define drop/flush behavior without blocking the product indefinitely.

## Python / FastAPI

```python
from contextvars import ContextVar
run_id = ContextVar("run_id", default=None)

async def with_run(identifier, operation):
    token = run_id.set(identifier)
    try:
        return await operation()
    finally:
        run_id.reset(token)
```

Reset context even on exceptions/cancellation. Verify propagation through background tasks, thread pools and streaming generators; task inheritance does not prove end-to-end propagation. FastAPI instrumentation should encompass the response body lifecycle, not just response-object creation. Reuse existing OpenTelemetry instrumentation instead of double-wrapping its HTTP spans.

## Event/usage example

```json
{"event":"model_attempt_finished","run_id":"synthetic-run-1","attempt":1,"status":"cancelled","usage_status":"unavailable","input_tokens":null,"output_tokens":null,"estimated_cost":null}
```

An allowlisted event builder selects approved fields; arbitrary objects and raw exceptions do not flow into the writer. Exact credential keys can be redacted as defense in depth. A `/token/` key regex would incorrectly erase token-count metrics, yet still miss a credential in an exception message. Hashes can expose low-entropy values and are still high-cardinality labels.

Normalize IDs in golden tests with a stable mapping so shared IDs remain shared. Preserve causal links, status and measurements. Separate a fixture run's measured render duration from unavailable LLM latency.

Sources checked 2026-10-30: [Python contextvars](https://docs.python.org/3/library/contextvars.html), [Node AsyncLocalStorage](https://nodejs.org/api/async_context.html). Confirm installed runtime support before use.
