# PRD Implementor

An LLM dev team that implements PRDs end-to-end, built with Lamia `.hu` agents
orchestrated by a `.lm` script. All agent outputs are structured via Pydantic
models and validated by Lamia's `JSON[Model]` syntax.

## Pipeline

```
prds/todo_api.md  →  orchestrator.lm  →  projects/todo_api/{src,tests}/ + logs/
                          │
                          ├── product_manager.hu → JSON[TaskBreakdown]
                          ├── groomer.hu         → JSON[TaskBreakdown]  (refined)
                          ├── developer.hu       → JSON[Implementation] (multi-file)
                          │     ↑ py_compile errors loop back here
                          ├── reviewer.hu        → JSON[Implementation] (with reviews)
                          │     ↑ up to 3 review rounds, then human escalation
                          ├── test_writer.hu     → JSON[Implementation] (test files)
                          ├── qa_analyst.hu      → JSON[QAReport]
                          └── deployer.hu        → str (changelog)
```

## Usage

```bash
lamia playground/prd_implementor/orchestrator.lm
```

Drop a `.md` file into `prds/`, re-run — only new or changed PRDs are processed.
Delete a snapshot from `implemented/` to force re-processing.

## Key design decisions

**Structured output everywhere.** Every agent returns `-> JSON[Model]` (except
deployer which returns free text). Lamia auto-injects the Pydantic schema into the
LLM prompt — agents describe WHAT to do, Lamia handles HOW to format it.

**Multi-file output.** The developer returns a `JSON[Implementation]` containing a
list of `CodeFile` objects (path + content). The orchestrator writes each to disk
under `projects/{prd_name}/`.

**Syntax checking.** After the developer writes files, `py_compile.compile()` runs
on each `.py` file. Compile errors are fed back to the developer before the reviewer
even looks at the code.

**Review cycle.** The reviewer annotates code with `FileReview` objects (line range,
comments, is_addressed flag). If any reviews are unresolved, the code goes back to
the developer. After 3 rounds without resolution, the pipeline stops and flags the
PRD for human intervention.

**Verbose logging.** When `VERBOSE_LOGGING = True` (default), every step writes its
full JSON output to `logs/`. Set to `False` for just the final artifacts.

## Pydantic models

All shared types live in `models.py`:

| Model | Used by | Purpose |
|-------|---------|---------|
| `Task` | PM, Groomer | Single implementation task with acceptance criteria |
| `TaskBreakdown` | PM, Groomer | Ordered task list + risks |
| `CodeFile` | Developer, Reviewer, Test Writer | Source file with path, content, and reviews |
| `Implementation` | Developer, Reviewer, Test Writer | Collection of CodeFiles |
| `FileReview` | Reviewer | Line-range review comment with is_addressed flag |
| `ReviewComment` | Reviewer | Single comment in a review thread |
| `QACriterion` | QA | PASS/FAIL/PARTIAL verdict for one acceptance criterion |
| `QAReport` | QA | Overall verdict + list of issues |

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

## Lamia syntax used

- **`.hu` agents as callables**: `product_manager(prd_content=text) -> JSON[TaskBreakdown]`
- **Structured validation**: Lamia validates LLM output against the Pydantic schema
- **Parameter substitution**: `{prd_content}`, `{specs}` in `.hu` templates
- **Python for orchestration**: change detection, file I/O, `py_compile`, control flow
