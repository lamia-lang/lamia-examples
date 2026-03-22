# PRD Implementor

An LLM dev team that implements PRDs end-to-end, built with Lamia `.hu` agents
orchestrated by a `.lm` script. Any software is a living artifact, and it should be updated in the incremental manner. The pipeline is designed to implement any change in the PRD files in the incremental manner. Any time you make a change a the PRD file or add a new PRD file, the next line of the orchestrator.lm script will implement the change in the incremental manner.

## Usage

```bash
lamia orchestrator.lm
```

The example comes with a Todo List API PRD. This is just an example to help you check how the pipeline works. Please delete this PRD and drop your own PRD/s into the `prds/` directory to have your project implemented.

When a version of a PRD file is implemented it's copy is placed in the `implemented/` directory. This is used to detect changes in the PRD files and implement the changes in the incremental manner.

Hence you can delete a snapshot from `implemented/` to force re-processing of the PRD file.

## Logging

**Verbose logging.** When `VERBOSE_LOGGING = True` (default), every step writes its
full JSON output to `logs/`. Set to `False` for just the final artifacts.

You can also run the Lamia CLI with the `--verbose` flag to see the Lamia's internal verbose logs.

## Directory structure

| Path | Purpose |
|------|---------|
| `prds/` | Input PRD markdown files |
| `implemented/` | Snapshots of processed PRDs (change detection) |
| `projects/` | Generated project folders with `src/` and `tests/` |
| `team/` | `.hu` agent prompts |
| `logs/` | Per-step JSON outputs (when verbose logging is on) |
| `models.py` | Pydantic models shared by all agents |
| `orchestrator.lm` | Pipeline script |

## Human in the loop

For some actions there is an escalation to the human. This is done by the orchestrator.lm script. The orchestrator.lm script will ask the human for a decision and then proceed with the next step.

For example, you might get messages like this:

  ⛔ Review not resolved after 3 rounds.
     5 open comment(s) remain. Human intervention needed.

You can then review the code and make the necessary changes. Then you can run the Lamia CLI with the `--continue` flag to continue the pipeline.

## Lamia syntax used

- **`.hu` agents as callables**: `product_manager(prd_content=text) -> JSON[TaskBreakdown]`
- **Structured validation**: Lamia validates LLM output against the Pydantic schema
- **Parameter substitution**: `{prd_content}`, `{specs}` in `.hu` templates
- **Python for orchestration**: change detection, file I/O, `py_compile`, control flow
