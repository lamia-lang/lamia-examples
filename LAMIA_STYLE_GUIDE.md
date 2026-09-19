# Lamia Style & Migration Guide

A practical guide for writing idiomatic Lamia (`.lm` / `.hu`) scripts in this repo and
turning "Python-with-a-few-prompts" scripts into clean Lamia. It distills the official
style guides and the `lamia inspect` lint rules into concrete, copy-pasteable change
suggestions.

> The two example projects in this repo — [`prd_implementor/`](prd_implementor/) and
> [`pinterest_pin_publisher/`](pinterest_pin_publisher/) — are the **canonical
> reference examples**. When in doubt, mirror their structure and conventions. This
> guide is for every *other* Lamia script you add.

Sources: LSG-1 (`.hu` style), LSG-2 (`.lm` style), LSG-3 (project structure), the
Inspect & Lint reference, and the `.hu`/`.lm`/web-automation user-guide pages at
<https://lamia-lang.github.io/lamia/>.

---

## 1. Core principles

1. **`.lm` files are Python + Lamia — but keep Python to a minimum.** Reach for Python
   only when Lamia syntax cannot express the task. File reads, file writes, LLM calls,
   and web actions should use Lamia syntax, not hand-rolled Python.
2. **`.hu` files are plain text.** No markdown, no HTML, no YAML front matter, no
   emojis. The LLM consumes raw text; visual formatting is noise.
3. **Output shape lives in the type system, not the prompt.** Never describe the output
   schema in a docstring, comment, or prompt. Define a Pydantic model and declare it at
   the call site with `-> Type[Model]`.
4. **`.hu` is the interface, `.lm` is the glue.** A `.hu` file is a single reusable
   prompt; `.lm` files orchestrate one or many `.hu` calls. `.hu` files cannot call
   other `.hu` files.

Why this matters: a scraper that is ~200 lines of Python is ~10-15 lines of Lamia. If a
`.lm` file reads like plain Python, it is usually leaving Lamia's file/LLM/web syntax on
the table.

---

## 2. Writing `.hu` files (prompt templates)

### 2.1 Structure

Lead with context, then the task, then inputs, then constraints:

1. Role / context — who the LLM is and what it knows
2. Task — stated directly, no fluff
3. Input parameters — `{param}` and `{@file}` references
4. Constraints — tone, length, boundaries (output *shape* belongs in the model, not here)

The filename (without `.hu`) becomes the callable function name, so name it to read
naturally at the call site: role-based for agents (`reviewer.hu`, `product_manager.hu`)
or verb-first for utilities (`summarize_article.hu`, `extract_entities.hu`).

### 2.2 Change suggestions (anti-pattern → idiomatic)

| Anti-pattern in a `.hu` file | Idiomatic fix | Rule |
|---|---|---|
| `# Heading`, `## Section` | Plain-text line or a bare label like `Constraints:` | HUW002 |
| `**bold**`, `*italic*`, `~~strike~~` | Plain words | HUW003/4/5 |
| `` `inline code` `` / ` ```fences``` ` | Plain text; move long content to `{@file}` | HUW008/HUW014 |
| `[text](url)`, `![alt](url)` | Bare URL | HUW006/7 |
| `> blockquote`, pipe `\| tables \|`, `---` rules | Plain lines | HUW009/10/11 |
| Emojis (`🚀`, `✅`) | Remove | HUW013 |
| HTML tags | Remove | HUW012 |
| `---` YAML front matter | Remove — `.hu` is not markdown | HUE001 |
| `Output JSON: { ... }` / example output block | Delete it; use `-> Type[Model]` at the call site | HUR018/HUW029 |
| `{userName}`, `{MaxRetries}` | `{user_name}`, `{max_retries}` | HUC020 |
| `{x}`, `{data}` | Descriptive name | HUC023 |
| `{the_full_product_requirements_document}` | Shorter name (< 30 chars) | HUC024 |
| More than 10 `{param}` placeholders | Move large content into `{@file}` references | HUW017 |
| Prompt over ~3000 chars | Split into focused prompts / `{@file}` | HUR027 |
| `ReviewCode.hu`, `generate-report.hu` | `review_code.hu` (snake_case) | HUC025 |
| `agent.hu`, `prompt.hu`, `template.hu` | Role/action name | HUC028 |

### 2.3 Literal braces must be escaped

`.hu` uses `{name}` for parameters. Any *literal* brace in the prompt text must be
doubled, or it will be parsed as a placeholder:

```
Bad  (parsed as parameters):
  The struct looks like { id: number; name: string }

Good (literal braces):
  The struct looks like {{ id: number; name: string }}
```

This is easy to hit when a prompt shows code samples (`if err != nil {{ return err }}`,
`interface User {{ ... }}`). Rule: HUE019 / character escaping.

### 2.4 Parameters and defaults

```
Write a {tone:professional} email to {recipient} about {topic}.
Keep it under {max_words:200} words.
```

- `{param:default}` — meaningful fallback used when the caller omits it.
- `{param:None}` — truly optional; empty string when omitted.
- No default — required; the caller must pass it, otherwise Lamia raises
  `missing required keyword arguments`.

Prefer `{@file}` over pasting large content into a parameter:

```
Good: Review the code in {@main.py} and suggest improvements.
Bad:  Review the following code: <500 inline lines>
```

`.hu` files are return-type agnostic — the same prompt can be called as `-> HTML`,
`-> JSON[Model]`, or `-> TEXT` from different `.lm` sites.

---

## 3. Writing `.lm` files (orchestration)

### 3.1 Use Lamia for file I/O, not Python

This is the single biggest reason a `.lm` file "looks like pure Python." Replace manual
file handling with Lamia syntax.

**Reading files**

```
# Bad — Python file I/O
from pathlib import Path
text = Path("./prd.md").read_text()
import json
data = json.loads(Path("./users.json").read_text())

# Good — Lamia read (validation is automatic when a type is given)
prd_text = "./prd.md" -> TEXT
data = "./users.json" -> JSON

# Or as a named, reusable function
def load_settings() -> JSON:
    "../config/settings.json"
```

Local reads are detected only for explicit path prefixes: `./`, `../`, `/`, `~/`. Bare
strings (`"config.json"`) are treated as LLM prompts.

**Writing files**

```
# Bad — Python file I/O
Path("out.html").write_text(page)
import shutil; shutil.copy2(src, dst)

# Good — Lamia write, with optional validation and append
"Create a landing page" -> File(HTML, "index.html")
"Generate more rows"    -> File(CSV, "data.csv", append=True)

# Keep the result in memory AND write it in one operation
report = "Generate the report" -> File(Markdown, "report.md")

# Programmatic writes when you already have the content
file.write("out.json", payload)
file.append("run.log", "done\n")
```

Genuinely algorithmic Python (hashing for change detection, `py_compile`, queue math,
control flow) is fine to keep — Lamia has no equivalent for those.

### 3.2 Calling `.hu` functions

```
# Good — keyword arguments only, return type at the call site
review = review_code(language="python") -> JSON[Review]

# Bad — positional args
review = review_code("python") -> JSON[Review]
```

| Anti-pattern | Fix | Rule |
|---|---|---|
| Positional args to a `.hu` call | Keyword args only | LMW006 |
| Missing a required `.hu` parameter | Pass every required param | LME002 |
| Passing a kwarg the `.hu` doesn't accept | Match the `.hu`'s `{params}` | LME014 |
| Output schema in a comment/string | Pydantic model + `-> Type[Model]` | LMR003 |

### 3.3 Return types & validation

Declare a return type whenever you need validated output. Supported: `JSON`, `HTML`,
`YAML`, `XML`, `CSV`, `Markdown`, `TEXT`.

```
def load_config() -> JSON:            # format validation only
    "./config.json"

def generate_page() -> HTML[Landing]: # extract into a Pydantic model
    "Create a login form"
```

Strict vs permissive (for `HTML`, etc.):

- `-> HTML[Model]` — permissive (default): filler around the target content is tolerated.
  Use for **parsing external content** (web pages, API responses).
- `-> HTML[Model, True]` — strict: response must be pure, no drift. Use for **content you
  generate** and fully control.
- Do not write `-> HTML[Model, False]`; use `-> HTML[Model]` instead.

### 3.4 Simplified syntax & model selection

```
# One-off, no function needed
data = "./users.json" -> JSON
page = "Create a login form" -> HTML

# Use a def when you need to reuse it, loop it, or pin a model
def analyze(models="openai:gpt-4"):
    "Analyze the data"

def with_fallback(models=["openai:gpt-4", "anthropic:sonnet-4"]):
    "Complex task with fallback"
```

Scripts use the global model chain from `config.yaml`; only override per-function when a
task truly needs a different/cheaper model.

### 3.5 Web automation idioms

Use the `web` object with a valid method and a selector. The supported methods are:

```
navigate, click, type_text, hover, get_text, is_visible, is_enabled,
wait_for, scroll_to, select_option, submit_form, upload_file, screenshot,
get_element, get_elements
```

| Anti-pattern | Fix | Rule |
|---|---|---|
| A method not in the list above (e.g. an "exists" check) | Use `web.is_visible(selector)` or `web.get_element(...)` | LME017 |
| A namespace other than `web`/`http`/`file`/`db`/`email` | Use a valid namespace | LME016 |
| `web.click()` with no selector on the global `web` | Pass a selector: `web.click("button.submit")` | LME020 |
| `el = web.get_element(s); el.click()` used once | Atomic `web.click(s)` | LMW019 |

Selectors can be CSS, XPath, or natural language ("Sign in button") — mix freely.

Sessions persist login across runs; always pass a target URL so Lamia can verify the
saved session:

```
# Good — two-arg form enables reliable session-skip
with session("my_app", "https://example.com/dashboard"):
    web.navigate("https://example.com/login")
    web.type_text("#email", email)
    web.click("button[type='submit']")
```

Missing the target URL is LMW024. `pinterest_pin_publisher/publish_pins.lm` is a good
reference for the session + queue + `web.*` pattern.

### 3.6 File context vs single file

```
# Anti-pattern — files() with a single path (LMW018)
with files("~/Documents/resume.pdf"):
    r = extract(aspect="skills") -> JSON

# Better — pass the path directly
r = extract(doc_path="~/Documents/resume.pdf", aspect="skills") -> JSON

# files() is for directory-based discovery of many files
with files("~/Documents/", "~/projects/"):
    answer = answer_question(question="...")   # uses {@resume.pdf} etc.
```

### 3.7 Other `.lm` conventions

| Topic | Convention | Rule |
|---|---|---|
| Variable names | `snake_case`; `PascalCase` only for Pydantic models | LMC009 |
| Indentation | 4 spaces, never tabs | LMW005 |
| Trailing whitespace / leading blank lines | Remove | LMW008 / LMC011 |
| Filenames | `snake_case`, descriptive (not `main.lm`, `process.lm`) | LMC010 / LMC015 |
| Imports | None needed for Lamia types; import only real Python deps | — |
| Inline Pydantic models | Max ~2 inline; extract shared models to `models/` | LMR012 |
| Script length | Over ~5000 chars → split into pipeline `.lm` files | LMR013 |
| Growth over 2x original | Make minimal, targeted edits | LMW001 |

---

## 4. Project structure

Minimal project:

```
my-project/
  config.yaml       # model chain + web/http config
  main.lm           # entry point
  summarize.hu      # a prompt
```

Larger, multi-agent project (this is the shape `prd_implementor/` follows):

```
my-project/
  config.yaml
  orchestrator.lm            # single entry point that coordinates the workflow
  team/                      # agent .hu files (role-based names)
    product_manager.hu
    developer.hu
    reviewer.hu
  models/                    # shared Pydantic models (schemas.lm or .py)
  data/                      # inputs referenced via {@...}
  output/                    # generated artifacts (gitignored)
```

Key conventions:

- `config.yaml` at the project root, with the model chain on the first lines and at
  least one fallback model. Add `web_config` here for browser/HTTP options instead of
  hard-coding them:

  ```
  models:
    - openai:gpt-4
    - anthropic:sonnet-4      # fallback

  web_config:
    browser_engine: selenium
    browser_options:
      headless: true
      timeout: 10.0
  ```

- `orchestrator.lm` is the one place the whole workflow is visible. Agents (`.hu`) never
  call each other; all composition flows through `.lm`. Functions in neighboring `.lm`
  files are auto-discovered — call them directly, no imports.
- Keep the tree shallow (2-3 levels). Avoid `.hu` files loose in the root mixed with
  `.lm`; group them under `team/` or a descriptive directory.
- Put generated output in a gitignored directory (`output/`, or the
  `projects/`, `logs/`, `implemented/` that `prd_implementor` already ignores).
- Names must be unique across the project: a `.hu` filename and a `.lm` `def` cannot
  collide.

Secrets (credentials, API keys) belong in `config.yaml`/environment, not inline in a
`.lm` file.

---

## 5. Migration checklist

Use this to convert a "pure-Python-looking" `.lm` into idiomatic Lamia:

1. Replace `open()/Path.read_text()/json.loads(...)` reads with `"path" -> JSON/TEXT`
   (or a `def ... -> JSON:` function).
2. Replace `Path.write_text()/shutil.copy*` writes with `-> File(Type, "path")` or
   `file.write(...)`.
3. Move any output-shape description out of prompts/comments into a Pydantic model and
   `-> Type[Model]` at the call site.
4. Convert positional `.hu` calls to keyword-only; verify each required param is passed.
5. Ensure every `web.*` call uses a real method + selector; add a target URL to every
   `session(...)`.
6. Extract shared Pydantic models to `models/`; keep at most ~2 inline.
7. Rename files/vars to `snake_case`; give scripts descriptive names.
8. Run `lamia inspect` (below) and drive the diagnostics to zero.

---

## 6. Enforcement with `lamia inspect`

`lamia inspect` runs three passes — syntax, semantic (checks `.hu` calls, duplicate/
colliding names, inline placeholders), and lint — and powers IDE squiggles.

```
lamia inspect script.lm            # single file
lamia inspect **/*.lm              # batch
lamia inspect script.lm --json     # machine-readable (CI / IDE)
```

Severities: **Error** (must fix — will fail or produce wrong results), **Warning**
(likely a bug), **Convention** (style), **Refactor** (structure). A non-zero exit on
syntax errors makes it a good CI gate:

```
- run: lamia inspect **/*.lm --json
```

Treat the rule codes referenced throughout this guide (e.g. `LMW006`, `HUW002`,
`HUR018`) as the checklist: if `inspect` is clean, the script is idiomatic.

---

## Appendix A: Why the docs site shows 404 on top-level directories

Opening a *section root* such as
`https://lamia-lang.github.io/lamia/user-guide/` returns **404**, while a *leaf page*
like `https://lamia-lang.github.io/lamia/user-guide/hu-syntax/` loads fine. The same is
true for other section roots (`/style-guides/`, `/advanced/`).

**Cause.** The docs are built with MkDocs (Material) using directory-style URLs
(`use_directory_urls`). MkDocs only generates an `index.html` for a directory when that
section has its own page (an `index.md`) *and* the theme is told to render section index
pages. Here the navigation links point straight at leaf pages (e.g. the "Guide to the
Hybrid Syntax" entry links to `.../lm-syntax/`), and there is no `index.md` for the
section, so no `user-guide/index.html` is produced. GitHub Pages then has nothing to
serve at the bare directory URL and returns its 404.

**Fix (lives in the separate `lamia-lang/lamia` docs repo, not this examples repo).**
In `mkdocs.yml`, enable section index pages and give each section a landing page:

```yaml
theme:
  name: material
  features:
    - navigation.indexes      # lets a section have its own index page

nav:
  - User Guide:
      - user-guide/index.md   # add this file as the section landing page
      - .hu Syntax: user-guide/hu-syntax.md
      - .lm Syntax: user-guide/lm-syntax.md
```

Then add `docs/user-guide/index.md` (and equivalents for `style-guides/`, `advanced/`).
Alternatively, keep leaf-only navigation and accept that bare directory URLs 404 — but
adding section index pages is the usual, link-friendly fix.

This change cannot be made from `lamia-examples`; it belongs to the documentation
repository.
