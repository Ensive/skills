"""Synthetic AI service fixture. No real model, credentials or operational telemetry."""
import asyncio
from contextvars import ContextVar
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

request_id = ContextVar("request_id", default=None)


class Input(BaseModel):
    samples: list[float] = Field(min_length=1)


def create_app(provider):
    app = FastAPI()
    app.state.events = []

    @app.post("/analyze/{run_id}")
    async def analyze(run_id: str, payload: Input):
        token = request_id.set(run_id)
        status = "failed"
        try:
            result = await provider(payload.samples)
            status = "completed"
            return {"source": "synthetic", "result": result, "usage": None}
        except asyncio.CancelledError:
            status = "cancelled"
            raise
        except RuntimeError:
            raise HTTPException(status_code=502, detail="provider_failure") from None
        finally:
            app.state.events.append({"run_id": request_id.get(), "status": status})
            request_id.reset(token)

    return app
