# Configuration recipes

Discover the schema library and runtime first. These small examples accept injected mappings to avoid importing process state throughout the application. Paths, key names and defaults are examples.

## TypeScript

```typescript
export function readPort(env: Readonly<Record<string, string | undefined>>): number {
  const raw = env.PORT ?? "3000";
  if (!/^[0-9]+$/.test(raw)) throw new Error("PORT: invalid_integer");
  const port = Number(raw);
  if (!Number.isSafeInteger(port) || port < 1 || port > 65535)
    throw new Error("PORT: out_of_range");
  return port;
}
```

Use the existing Zod/TypeBox schema for a larger config; verify its version-specific coercion and error APIs. Keep settings and credentials distinct at the consumer boundary. Build safe output by selecting fields; TypeScript's structural typing does not remove extra secret properties at runtime. Browser-exposed build prefixes are public, even when the variable name contains `SECRET`.

## Python

```python
from dataclasses import dataclass
from collections.abc import Mapping

@dataclass(frozen=True)
class Settings:
    port: int

def load_settings(env: Mapping[str, str]) -> Settings:
    raw = env.get("PORT", "3000")
    if not raw.isascii() or not raw.isdecimal():
        raise ValueError("PORT: invalid_integer")
    port = int(raw)
    if not 1 <= port <= 65535:
        raise ValueError("PORT: out_of_range")
    return Settings(port=port)
```

If Pydantic Settings already exists, keep its configured source order and validator behavior rather than adding another loader. Instantiate service settings through its application factory/lifespan, especially where tests create multiple apps. Avoid printing a full settings object with credentials or exception input values.

## Verification matrix

| Input | Expected behavior |
| --- | --- |
| Missing optional port | Documented non-secret default |
| Empty, fractional, negative or out-of-range port | Safe field/code failure |
| `FEATURE=false` | False after explicit parsing |
| Optional provider disabled; key missing | Startup succeeds without contacting a provider |
| Provider enabled; key missing | Safe startup failure |
| Synthetic secret in invalid value | No secret in logs/errors/public bundle |
| Two apps with distinct injected mappings | No settings leak between apps |

Production secret injection, rotation and deployment-time interpolation require checks in that environment. Local tests do not establish them.
