# Python and FastAPI integration

Use only for a Python service. Discover the supported Python version, environment manager, pytest/unittest configuration and service entrypoint. The following uses pytest, AnyIO and HTTPX only when already appropriate for the project.

```python
import httpx
import pytest

@pytest.mark.anyio
async def test_rejects_invalid_input(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"samples": "invalid"})
    assert response.status_code == 422
```

`app` is the project's fixture, not a new global application. Use its established lifespan manager: HTTPX ASGITransport does not trigger startup/shutdown. A route test that skips startup cannot verify pool initialization or cleanup. Select the AnyIO backend the application supports; an asyncio-only driver does not establish Trio compatibility.

Inject the provider at the application's dependency seam. Use FastAPI `dependency_overrides` only for dependencies actually resolved through `Depends`; restore overrides in `finally` or fixture teardown. Script expected requests, reject extra calls and assert exhaustion after success. Assert expected remaining calls after cancellation. Do not replace the route/adapter you intend to test.

For async database reliability, use an isolated database/schema or a transaction rollback strategy compatible with background tasks and separate connections. Exercise rollback on error, tenant scoping, exhausted pools and cancelled queries where relevant. A fake repository proves application decisions, not SQL behavior or pool safety.

For a streaming response, ASGITransport can test payload shape but may buffer and does not prove socket disconnect, proxy flushing or backpressure. Use a separately bounded local-server test for those behaviors; close connections and check generator finalization. Do not catch `CancelledError` and report success; release resources then propagate cancellation.

If LangGraph is present, inspect its pinned streaming/checkpointer API. Test graph state and resume identity separately from the HTTP stream. A graph's interrupt/resume is not proof of transport reconnect/replay.

Sources checked 2026-10-30: [FastAPI async tests](https://fastapi.tiangolo.com/advanced/async-tests/), [HTTPX async resources](https://www.python-httpx.org/async/), [Python task cancellation](https://docs.python.org/3/library/asyncio-task.html), [LangGraph streaming](https://docs.langchain.com/oss/python/langgraph/streaming). Recheck APIs against the project's pinned versions.
