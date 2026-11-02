# Evaluating skill behavior

Static validation, executable fixture tests, routing evaluations and native assistant integration answer different questions. Report them separately. A valid directory or a manual walkthrough does not prove that an assistant discovered, invoked or followed a skill.

## Controlled comparisons

Choose a small set of held-out requests from realistic target repositories before running the evaluation. Include positive, adjacent-negative, ambiguous and missing-context cases; `scenarios.json` supplies starting examples, not a routing oracle. Reserve additional cases that were not used to edit the skill.

For each task, prepare disposable copies of the same synthetic or authorized public fixture. Compare no skill and the candidate skill; include a previous skill only when its revision is trustworthy. Keep the task, project instructions, tools, permissions, model, settings and budget equal. Each fresh session receives only its own condition and no expected solution or other condition's output. Make required resources available with the selected skill. Do not authorize live credentials, external writes or edits outside the fixture.

Record source/fixture revisions (or a content hash for unpublished changes), assistant and runtime versions, OS, model identifier, tool permissions, network policy, exact commands and working directories, trial counts, elapsed time, usage/cost when reported, and provider-controlled settings that cannot be fixed. Select repetition and spending limits before execution. Keep raw transcripts and outputs in ignored `.artifacts/` or temporary directories; publish only sanitized summaries and reproducible inputs.

## Outcome rubric

Score each criterion 0 (incorrect/missing), 1 (partial) or 2 (satisfied), using produced artifacts and independently rerun commands:

| Criterion | Evidence |
| --- | --- |
| Routing and scope | Correct boundary; adjacent work handed off or declined; no unrelated scaffolding |
| Commands | Existing commands and installed tools used from the correct working directory |
| Conventions | Project boundaries, runner and architecture preserved unless the task justifies a change |
| Useful output | Runnable tests, implementation or decisions satisfy the requested observable outcome |
| Verification honesty | Failure paths covered where relevant; executed checks and remaining uncertainty separated |

Treat secret exposure, unauthorized mutation or fabricated execution as failures regardless of total score. Review model-graded judgments against concrete artifacts; an authoring agent's approval is not independent validation. Report failed trials, variation, ties and confounders. Small diagnostic samples cannot establish statistical superiority or reliability across the catalog.

## Native assistant checks

Install one selected skill into a clean temporary project using the documented host path. Record initialization/discovery evidence, explicitly invoke it, and confirm actual loading of its local references in the tool trace. Verify the task outcome independently. Evaluate automatic selection separately with requests that do not name the skill, including negative cases. Do not generalize a CLI result to an editor, cloud surface or another OS.

Use precise outcomes: executed and passed, executed and failed, documentation-supported but untested, unsupported, or unknown. When runtime access is unavailable, preserve an unexecuted plan rather than recording a pass. Keep the public support summary in [compatibility](../docs/compatibility.md), and track follow-ups in [GitHub issues](https://github.com/Ensive/skills/issues).
