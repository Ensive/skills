export type Analysis = { source: "synthetic"; peak: number; unit: "°C" };
export function analyze(samples: number[]): Analysis {
  if (!samples.length || samples.some(value => !Number.isFinite(value)))
    throw new Error("invalid_samples");
  return { source: "synthetic", peak: Math.max(...samples), unit: "°C" };
}
