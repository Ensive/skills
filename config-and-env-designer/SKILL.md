---
name: config-and-env-designer
description: >-
  Designs twelve-factor configuration with schema validation, typed config objects,
  fail-fast loading, and clear separation of secrets vs non-secret settings. Use when
  setting up env vars, ".env", config schema, Zod or TypeBox env schema, validating
  environment at process startup, "fail fast on boot", "validate env at startup",
  missing env vars at boot, or "typed config".
---

# Config and Env Designer

## When to use

- User adds `.env`, environment variables, or config files for a TS service or CLI.
- User needs validation at startup and typed access instead of raw `process.env`.
- User mixes secrets and feature flags and wants a clear policy.
- User asks for defaults, dev vs prod profiles, or 12-factor compliance.
- User debugs "undefined at runtime" config errors after deploy.

## Core principles

1. Config is validated once at process start; crash with actionable message on failure.
2. Secrets come from environment or secret store—never committed defaults in repo.
3. Non-secret settings may have safe defaults documented in schema.
4. Use a schema (Zod, TypeBox, or similar) to produce a single typed `Config` object.
5. Separate `Config` (settings) from `Secrets` (credentials) in types and loaders.
6. No silent coercion: invalid types fail, do not fall back to zero or empty string.
7. Print effective non-secret config in debug mode; never print secret values.
8. Path and URL fields are validated as absolute or normalized per environment.
9. Feature flags are explicit booleans, not truthy string parsing of `"false"`.
10. LLM keys and endpoints feed llm-client-architect; FS roots feed secure-filesystem-access.

## Checklist

- [ ] Inventory all env vars: name, required?, secret?, default, description.
- [ ] Define schema with types, enums, min/max, and URL/path formats.
- [ ] Load dotenv only in local dev; production relies on platform env injection.
- [ ] Fail fast: aggregate all validation errors in one startup report.
- [ ] Export readonly `config` singleton; forbid mutation after load.
- [ ] Document example `.env.example` without real secrets.
- [ ] Map CLI flags to override env only where intentional; document precedence.
- [ ] Test loader with missing required vars and invalid types.
- [ ] Ensure log level and NODE_ENV are validated enums.
- [ ] Cross-check secret names with logging redaction in llm-client-architect.
- [ ] On schema failure at boot, log only field names + error codes (e.g. `flatten().fieldErrors` keys). Never print the offending value for any field whose name is in the secret allowlist.

## Patterns

**Schema with secret classification (derive redaction set from schema)**

```typescript
import { z } from "zod";

const SECRET_FIELDS = new Set<string>();

function envKey<T extends z.ZodTypeAny>(name: string, schema: T, opts?: { secret?: boolean }): T {
  if (opts?.secret) SECRET_FIELDS.add(name);
  return schema;
}

const EnvSchema = z.object({
  PORT: envKey("PORT", z.coerce.number().int().positive().default(3000)),
  API_KEY: envKey("API_KEY", z.string().min(1), { secret: true }),
  LOG_LEVEL: envKey("LOG_LEVEL", z.enum(["debug", "info", "warn", "error"]).default("info")),
});
```

**Split secrets and settings (canonical loader)**

```typescript
export type Secrets = Readonly<{ apiKey: string }>;
export type Settings = Readonly<{ port: number; logLevel: "debug" | "info" | "warn" | "error" }>;

export function load(): { settings: Settings; secrets: Secrets } {
  const parsed = EnvSchema.parse(process.env);
  return Object.freeze({
    settings: Object.freeze({ port: parsed.PORT, logLevel: parsed.LOG_LEVEL }),
    secrets: Object.freeze({ apiKey: parsed.API_KEY }),
  });
}

export function printEffective(s: Settings): void {
  console.error(JSON.stringify(s));
}
```

`printEffective` is typed against `Settings` only, so secrets cannot be passed by mistake.

**Fail-fast with secret-safe error logging**

```typescript
const result = EnvSchema.safeParse(process.env);
if (!result.success) {
  const fieldErrors = result.error.flatten().fieldErrors;
  for (const [name, errs] of Object.entries(fieldErrors)) {
    if (SECRET_FIELDS.has(name)) {
      console.error(`${name}: invalid (value redacted)`);
    } else {
      console.error(`${name}: ${errs?.join("; ")}`);
    }
  }
  process.exit(1);
}
```

**.env.example only placeholders**

```bash
API_KEY=replace-me
PORT=3000
```

## Anti-patterns

- **Reading `process.env` ad hoc in modules** — inconsistent; central loader only.
- **Defaulting secrets to empty string** — silent auth failures; require or fail.
- **Truthy check `if (process.env.FEATURE)`** — `"false"` is true; use boolean schema.
- **Committing `.env` with real keys** — leakage; gitignore and use example file.
- **Late validation on first request** — flaky prod; validate at boot.
- **Storing secrets in typed `Config` with settings** — conflates redaction policies.

## Output format

```markdown
# Configuration design: <app>

## Variables
| Name | Secret | Required | Default | Description |
|------|--------|----------|---------|-------------|

## Precedence
1. CLI flags (`parseArgs` in typescript-cli-architect) — only where explicitly wired
2. process.env (production) or dotenv (local dev only)
3. Schema defaults for non-secret settings

## Schema location
- `<path>`

## Startup behavior
- On invalid: <exit code, message shape>

## Examples
- `.env.example` keys listed
```

## Escalation

- Greenfield agent/CLI order: `typescript-cli-architect/reference.md`.
- CLI flag overrides: coordinate with typescript-cli-architect `parseArgs` schema; default precedence argv > env > schema default.
- Ask deployment target (local, Docker, Vercel, bare metal) for env injection pattern.
- Ask which vars are secrets vs settings if list is incomplete.
- Proceed with strict fail-fast schema when unknown; mark assumed defaults.
