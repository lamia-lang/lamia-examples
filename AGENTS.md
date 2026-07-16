# AGENTS.md

## Cursor Cloud specific instructions

This repo is a collection of **Lamia** examples (AI-powered scripts written in plain
English `.lm` / `.hu` files). The runtime is the `lamia` CLI from the `lamia-lang`
PyPI package. There is no build step and no repo-level dependency manifest; the only
hard dependency is `lamia-lang` (installed by the startup update script into
`~/.local/bin`, which is on `PATH` via `~/.bashrc`).

Standard usage for each example is documented in its own `README.md`
(`prd_implementor/README.md`, `pinterest_pin_publisher/README.md`). Notes below are
only the non-obvious, environment-specific caveats.

### LLM backend (required to actually run any example)
Every example needs an LLM provider. Options:
- **API keys** — set `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` as secrets and enable the
  provider in a `config.yaml` (`providers.<name>.enabled: true`). This is the most
  reliable way to run the examples as designed.
- **`prd_implementor/config.yaml` default** uses `claude-max`, which needs a local
  `anthropic-max-router` proxy + Claude OAuth (see
  `prd_implementor/extensions/adapters/claude_max.py`). Not available out of the box.
- **Local Ollama** — good for quick smoke tests only (no API key needed).

### Ollama caveats (important)
- Ollama runs as a manual process here (systemd is not available). Start it with
  `ollama serve` in the background before running scripts; verify with
  `curl -s http://127.0.0.1:11434/api/version`.
- The **latest Ollama (0.32.x) segfaults** during model warmup in this VM
  (`llama-server ... signal: segmentation fault`). Use **Ollama 0.6.8**, which works:
  `curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.6.8 sh`.
- Small local models (`llama3.2:1b`, `llama3.2:3b`) are slow on CPU (minutes per
  agent call) and **cannot reliably satisfy the strict Pydantic schemas** used by
  `prd_implementor` (they omit optional fields like `risks` and fail validation).
  Use a capable model (Claude Sonnet/Opus, GPT-4-class) for real pipeline runs.
- To point an example at Ollama, pass a config override:
  `lamia --file orchestrator.lm --config <your_ollama_config>.yaml`.

### Quick environment sanity check
A minimal `.lm` that exercises the core flow (LLM call + schema-validated output):
define a `def` with a docstring prompt and a `-> JSON[Model]` return type, then run
`lamia --file <script>.lm --config <config>.yaml`.

### prd_implementor
- Run: `lamia orchestrator.lm` (add `--config <yaml>` to override the model chain).
- Generates into gitignored `projects/`, `logs/`, `implemented/`. Delete a snapshot
  from `implemented/` to force re-processing a PRD.
- Note: step 7 calls a `deployer(...)` agent but `team/` has no `deployer.hu`; the
  pipeline only reaches that step after all earlier stages pass with a capable model.

### pinterest_pin_publisher
- Requires **real Pinterest credentials** (hard-coded in `publish_pins.lm` /
  `tests/check_selectors.lm`) and performs **live login and pin publishing** via
  Selenium. `google-chrome` and `selenium` are installed, but do **not** run it in
  setup/CI — it takes real actions on a live account. Set credentials + board first.
