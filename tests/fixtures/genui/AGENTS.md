# Synthetic GenUI fixture

This is newly authored synthetic code, using public GenUI Lab package boundaries as a small test context. It is not the real application or operational telemetry. Domain state belongs in packages/domain, orchestration in packages/experiment-core, and presentation in apps/web. No provider key is required. Use the existing node:test runner; do not add Vitest, a backend, a provider SDK or a universal src/agent/types.ts module.

From this directory: `node --experimental-strip-types --test test/flow.test.ts`. Node 22.6+ is needed for this example's type stripping; this does not run the TypeScript typechecker. The real public project uses pnpm and Vitest; its commands are documented separately in the evaluation context.
