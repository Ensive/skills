# Browser and publishing scenarios

Find the existing browser/component test runner, build command, base URL and server lifecycle. Exercise user-visible behavior through semantic roles where possible. A DOM or HTML parser test cannot establish layout, keyboard focus, contrast or screen-reader behavior.

For a writing site, verify draft/public content separation, stable article URLs, headings/landmarks, link destinations, navigation, search/filter empty states and preservation of supplied text. Read real editorial conventions; do not introduce model APIs, auth or persistence for a static layout task.

For interactive UI, define initial/loading/empty/success/error/cancelled states and test transitions at the actual state boundary. Assert identity survives reorder/patch, rejected input leaves authoritative state intact, and stale responses cannot overwrite newer state. For generated components, include unknown component names, invalid props and forbidden actions in negative fixtures.

For telemetry displays, use synthetic provenance, known units/timezone, gaps and an annotated anomaly interval. Assert the table/description and chart represent the same data; do not infer causes from a visually prominent spike. For replay, preserve event IDs and ordering rules rather than snapshotting a freshly randomized run.

Use screenshots for visual comparisons and a browser for keyboard/viewport checks when available. Record separate results for structural checks, automated accessibility rules and manual assistive-technology checks. An automated accessibility pass is not a claim of full conformance.
