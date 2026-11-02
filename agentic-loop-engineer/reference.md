# Agentic Loop Engineer — reference

## Module placement

Reuse existing project contracts. If none exist, the following TypeScript shapes are an implementation example; choose placement from repository conventions. Skill folders are instructions, not importable runtime modules.

## TypeScript contract example

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
| `timeout` | uncertain | only after proving repetition safe and reconciling possible effects |
| `transient` | candidate | only if idempotent or protected by an effective idempotency mechanism |
| `internal` | fatal | no |
| `file_not_found`, `path_outside_root` | fatal | no |
| `user_input_required` | user_input_required | no |

HTTP-layer errors (`rate_limited`, `http_5xx`) are classified in `llm-client-architect`, not here.
