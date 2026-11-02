# Verify a provider adapter

Select sources for the provider already approved by the project. Check the installed SDK lockfile and official API reference together. Record URLs, verification date and tested SDK version in the target project's implementation report. This skill deliberately stores no model prices, default model ID or assumed context limit.

| Contract | Evidence to collect |
| --- | --- |
| Endpoint and authentication | Official request schema; supported SDK method; no secret values |
| Capabilities | Selected model's tools, schema output, modality, context and streaming support |
| Tool translation | IDs, argument fragments, result ordering and completion markers |
| Retry | Official error semantics plus SDK retries and idempotency support |
| Usage | Terminal/stream fields, cumulative versus per-chunk counts, cache/reasoning categories |
| Fallback | Same required capabilities and approved data handling; explicit quality tradeoff |
| Pricing | Dated official source, currency, input/output/cache units; unknown when unavailable |

Official entrypoints to verify when relevant: [OpenAI](https://developers.openai.com/api/docs/), [Anthropic](https://docs.anthropic.com/), [OpenRouter](https://openrouter.ai/docs/). Links are starting points, not evidence that every provider contract has been tested here. An OpenAI-compatible route does not imply identical tools, SSE events or usage fields. For a local model, inspect its actual server version and fixtures.

Offline adapter tests can verify translation and failure policy; they cannot prove live model quality, price accuracy, service availability or residency compliance. Report each separately.
