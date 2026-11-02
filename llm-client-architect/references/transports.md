# Transport and stream recipes

Implementation examples, not a bundled runtime. Use the project's SDK/HTTP client and normalized types. Verify SDK built-in retry and timeout behavior before adding wrappers.

## Shared retry decision

```text
before each attempt: reject cancellation or expired total deadline
perform request with remaining deadline and bounded response size
on failure:
  classify transport + operation + possible committed effects
  if partial output, invalid request, auth failure, or retry unsafe: surface failure
  if attempts exhausted: surface failure
  delay = max(valid Retry-After, exponential delay with jitter)
  if delay cannot fit remaining deadline: stop / schedule later
  wait interruptibly; retry within the same total budget
```

Parse Retry-After as nonnegative seconds or HTTP date using an injectable clock. Do not cap a server minimum downward. Account for time spent reading failed bodies. Preserve an error category and safe summary rather than reflecting provider text containing input or credentials.

## TypeScript

Pass an AbortSignal through request, stream consumption and backoff. Check an already-aborted parent before registering listeners. Clear timeout/listeners in `finally`. A Promise.race that rejects a caller does not stop the losing request. SDK methods and fetch have different cancellation APIs; verify the actual version.

For an async iterator, cancel/close the response when its consumer exits early. Preserve decoder state across UTF-8 byte boundaries. EventSource cannot attach arbitrary authorization headers through its standard constructor; choose the transport and credential mechanism from the application's auth policy rather than placing secrets in query parameters.

## Python / FastAPI / LangGraph

Reuse a bounded `httpx.AsyncClient` for the intended application lifecycle. Close streamed responses with `async with client.stream(...)`; if manually streaming, close the response explicitly. Apply an overall deadline in addition to client phase timeouts. `asyncio.timeout` is a Python 3.11+ example; use the project's supported runtime. Clean up in `finally` and propagate `CancelledError`.

A FastAPI request disconnect must cancel upstream work under the service's policy. Test generator cleanup and DB/session ownership. If work intentionally survives disconnect, give it an explicit job identity/status route and authorization model rather than silently orphaning it.

For LangGraph, inspect installed version and existing `stream`/`astream` or event-streaming usage. Map only the selected graph projections to the external protocol; graph state remains authoritative. Checkpointer resume identity, user authorization and SSE replay IDs are separate concerns.

## SSE / recovery acceptance cases

- Split UTF-8, CRLF, field lines and event delimiters across transport chunks.
- Handle comments, multiline data, event IDs, malformed JSON and oversized/unterminated events.
- Cancel before headers, during data and during backoff; assert resource cleanup.
- Disconnect after one visible delta: mark incomplete; do not append a fresh generation as a continuation.
- Resume only when the server implements a durable cursor and replay retention; Last-Event-ID alone does not supply storage or exactly-once processing.
- Bound slow-consumer buffers; choose pause/drop/abort behavior consistent with the application.
- Revalidate authorization on reconnect and never execute a repeated mutating tool effect automatically.

Checked 2026-10-30: [WHATWG SSE](https://html.spec.whatwg.org/multipage/server-sent-events.html), [HTTPX async](https://www.python-httpx.org/async/), [Python cancellation/timeouts](https://docs.python.org/3/library/asyncio-task.html), [LangGraph streaming](https://docs.langchain.com/oss/python/langgraph/streaming).
