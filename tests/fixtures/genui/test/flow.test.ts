import { test } from "node:test";
import assert from "node:assert/strict";
import { run } from "../packages/experiment-core/run.ts";
import { view } from "../apps/web/view.ts";

test("analysis crosses real orchestration/presentation boundaries; usage stays unavailable", async () => {
  const requests: unknown[] = [];
  const result = await run([28, 55, 31], async analysis => {
    requests.push(analysis);
    return "synthetic report";
  }, new AbortController().signal);
  assert.equal(requests.length, 1);
  assert.deepEqual(view(result.analysis), { heading: "Synthetic telemetry", summary: "55 °C", source: "synthetic" });
  assert.equal(result.usage, null);
});

test("invalid domain input never reaches the representation boundary", async () => {
  let calls = 0;
  await assert.rejects(run([], async () => { calls++; return "unexpected"; }, new AbortController().signal), /invalid_samples/);
  assert.equal(calls, 0);
});

test("cancellation releases cooperative boundary and produces no completed result", async () => {
  const controller = new AbortController();
  let released = false;
  let markStarted!: () => void;
  const started = new Promise<void>(resolve => { markStarted = resolve; });
  const pending = run([30], async (_analysis, signal) => {
    try {
      return await new Promise<string>((_resolve, reject) => {
        signal.addEventListener("abort", () => reject(signal.reason), { once: true });
        markStarted();
      });
    } finally { released = true; }
  }, controller.signal);
  await started;
  controller.abort(new Error("cancelled"));
  await assert.rejects(pending, /cancelled/);
  assert.equal(released, true);
});

test("already cancelled run does not call the boundary", async () => {
  let calls = 0;
  await assert.rejects(run([30], async () => { calls++; return "unexpected"; }, AbortSignal.abort(new Error("cancelled"))), /cancelled/);
  assert.equal(calls, 0);
});
