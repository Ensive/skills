import type { Analysis } from "../../../packages/domain/analysis.ts";

export function view(analysis: Analysis) {
  return { heading: "Synthetic telemetry", summary: `${analysis.peak} ${analysis.unit}`, source: analysis.source };
}
