# Agentic Loop Engineer — reference

## Module placement

Create shared types at a configurable path (default `src/agent/types.ts`). Re-export from one module; sibling skills import the same file — do not redefine fields in adapters.

## Canonical types (copy into `src/agent/types.ts`)

```typescript
export type NormalizedToolCall = {
  id: string;
  name: string;
  input: unknown;
};

export type NormalizedToolResult = {
  id: string;
  content: string;
  isError: boolean;
};

export type LlmResponse = {
  stopReason: "end_turn" | "tool_use";
  toolCalls: NormalizedToolCall[];
  text?: string;
};

export type LlmError = {
  code: string;
  message: string;
  retryable: boolean;
};
```

## Tool error → outcome mapping

Registry error codes (`tool-registry-architect` § Error taxonomy):

| `content.error` | ToolOutcome | Retry in loop |
|-----------------|-------------|---------------|
| `invalid_input` | fatal | no |
| `not_found` | fatal | no |
| `forbidden` | fatal | no |
| `timeout` | retryable | yes |
| `transient` | retryable | yes |
| `internal` | fatal | no |
| `file_not_found`, `path_outside_root` | fatal | no |
| `user_input_required` | user_input_required | no |

HTTP-layer errors (`rate_limited`, `http_5xx`) are classified in `llm-client-architect`, not here.
