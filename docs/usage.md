# Using the skills

These files guide an agent or a human working in an existing project. Read the project's own instructions first so the skill can be applied to its architecture, commands, and constraints.

## Get a copy

Clone into a new directory and record the revision you are using:

```sh
git clone https://github.com/Ensive/skills.git ensive-skills
cd ensive-skills
git rev-parse HEAD
git ls-files '*/SKILL.md'
```

The final command lists the tracked skills. A clone includes the owned skills and their reference files; folders ignored in a maintainer's local checkout are not distributed by Git.

Open the [router](router.md), then read the selected folder's `SKILL.md` and any reference it calls for. Keep the checkout's folder structure intact so relative references resolve. Give your coding agent the selected file's absolute path, or attach its contents and the relevant references if the agent cannot access local files. Tell it which target project to work in.

For example, replace the paths with your own:

```text
In /path/to/my-agent, implement the requested read_file tool.
Read the project's AGENTS.md and existing tool code first.
Use /path/to/ensive-skills/secure-filesystem-access/SKILL.md
and its referenced material for the filesystem implementation.
Report changed files, checks run, and any unresolved assumptions.
```

This direct-file workflow does not depend on a particular editor's skill discovery mechanism. For automatic discovery, use your agent host's documented installation procedure; directory locations and invocation syntax vary by host. Keep the recorded revision with your project notes so later behavior can be traced to the instructions used.

## Worked routing example: add a file-read tool

Suppose an existing TypeScript agent needs `read_file(path)`. It must stay inside a configured workspace, enforce a file-size limit, and return a structured failure for invalid arguments or paths outside the workspace.

Start with [secure-filesystem-access](../secure-filesystem-access/SKILL.md): the request is about implementing file access. As the work reaches another responsibility, open the corresponding skill:

| Work in the target project | Skill and observable result |
| --- | --- |
| Implement the workspace boundary and bounded read | [secure-filesystem-access](../secure-filesystem-access/SKILL.md): guard code and focused cases for allowed paths, traversal, symlink escapes, and size limits. |
| Expose the handler as an agent tool | [tool-registry-architect](../tool-registry-architect/SKILL.md): input schema, read capability gate, timeout, and normalized result contract. Invalid arguments fail before the handler runs. |
| Consume tool failures in the existing runner | [agentic-loop-engineer](../agentic-loop-engineer/SKILL.md): validation/path failures remain non-retryable, with bounded loop execution and testable termination. |
| Exercise the connected flow | [integration-tester](../integration-tester/SKILL.md): a scripted model requests the tool, receives its result, and ends the turn. Assertions cover tool calls, final state, and exhaustion of the script. |
| Review the implemented boundary | [typescript-security-auditor](../typescript-security-auditor/SKILL.md): findings tied to code and a threat model; filesystem fixes return to the filesystem skill. |

Use [typescript-unit-tester](../typescript-unit-tester/SKILL.md) for isolated helpers. If the provider returns HTTP 429 during a separate client task, follow [llm-client-architect](../llm-client-architect/SKILL.md); that policy does not retry an invalid file path. The [FAQ](maintainer-faq.md) explains these splits, and the [boundary table](boundaries.md) links their sources.

## Verify the result in your project

Review the diff, then run the project's existing type-check, unit, and integration commands. Record the exact commands and results, including failures. For this example, check that an allowed read succeeds, invalid arguments never reach the handler, an escaping path fails without a retry, and the scripted integration scenario consumes every step. Review golden-output changes explicitly.

The walkthrough defines a task and its acceptance checks. It does not include an implementation or measured model-performance results. Skill instructions and snippets require adaptation and testing against the target runtime, operating system, and threat model.
