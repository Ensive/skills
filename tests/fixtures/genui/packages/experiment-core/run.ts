import { analyze } from "../domain/analysis.ts";
import type { Analysis } from "../domain/analysis.ts";

export async function run(
  samples: number[],
  represent: (analysis: Analysis, signal: AbortSignal) => Promise<string>,
  signal: AbortSignal,
) {
  signal.throwIfAborted();
  const analysis = analyze(samples);
  const representation = await represent(analysis, signal);
  signal.throwIfAborted();
  return { analysis, representation, usage: null };
}
