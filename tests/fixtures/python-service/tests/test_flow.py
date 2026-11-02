import asyncio
import unittest
import httpx
from service.app import create_app, request_id


class FlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_route_provider_result_and_unknown_usage(self):
        calls = []

        async def provider(samples):
            calls.append((request_id.get(), samples))
            return max(samples)

        app = create_app(provider)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/analyze/test-a", json={"samples": [28, 55, 31]})
        self.assertEqual(response.json(), {"source": "synthetic", "result": 55, "usage": None})
        self.assertEqual(calls, [("test-a", [28, 55, 31])])
        self.assertEqual(app.state.events, [{"run_id": "test-a", "status": "completed"}])
        self.assertIsNone(request_id.get())

    async def test_invalid_input_does_not_call_provider(self):
        async def provider(_samples):
            self.fail("invalid input reached provider")

        app = create_app(provider)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/analyze/test-a", json={"samples": []})
        self.assertEqual(response.status_code, 422)

    async def test_provider_error_is_safe(self):
        async def provider(_samples):
            raise RuntimeError("synthetic-secret-DO-NOT-LOG")

        app = create_app(provider)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/analyze/test-a", json={"samples": [30]})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("DO-NOT-LOG", response.text + str(app.state.events))
        self.assertEqual(app.state.events[0]["status"], "failed")

    async def test_cancel_and_concurrent_context_cleanup(self):
        started = {name: asyncio.Event() for name in ("a", "b")}
        released = set()

        async def provider(_samples):
            name = request_id.get()
            started[name].set()
            try:
                await asyncio.Event().wait()
            finally:
                released.add(request_id.get())

        app = create_app(provider)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            tasks = [asyncio.create_task(client.post(f"/analyze/{name}", json={"samples": [30]})) for name in started]
            try:
                await asyncio.wait_for(asyncio.gather(*(event.wait() for event in started.values())), timeout=2)
            finally:
                for task in tasks:
                    task.cancel()
                outcomes = await asyncio.gather(*tasks, return_exceptions=True)
        self.assertTrue(all(isinstance(outcome, asyncio.CancelledError) for outcome in outcomes))
        self.assertEqual(released, {"a", "b"})
        self.assertEqual({(event["run_id"], event["status"]) for event in app.state.events}, {("a", "cancelled"), ("b", "cancelled")})
        self.assertIsNone(request_id.get())
