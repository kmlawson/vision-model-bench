# Visual text extraction benchmark

This workspace benchmarks how well the visual models of different LLMs extract text and tables from document images. Benchmark inputs are in `files/`. The two PDF inputs have been rendered to PNG at 200 DPI using Poppler, saved with their original base names, and the PDFs removed. `itinerary.png` is converted from `itinerary.heic`, whose original is retained; use the PNG for benchmark runs.

Save outputs under `results/[model-name]/[date]/`, using an ISO date (`YYYY-MM-DD`). Use one Markdown output per input, with the input's base filename: for example, `results/gpt-6-astra-low/2026-10-12/difficult-table.md`. Include run metadata so the model, reasoning effort, prompts, and input preparation are reproducible.

Numbers written with Asian numeral characters should be converted to ordinary Western digits (`0-9`), while the surrounding text remains in its original language.

The reusable task instructions are in [agent-instructions.md](agent-instructions.md). Each task should run independently in a fresh agent, approximating a one-shot API request. Use visual input only; do not use OCR, PDF text layers, external sources, other agents' results, or a reference answer. Preserve raw model responses without editorial correction. PDF rasterization and HEIC-to-PNG conversion are permitted for image viewing.

The initial run uses `gpt-6-astra` with reasoning effort `low`, recorded as `gpt-6-astra-low` in the results directory. This is a fresh-agent approximation of a one-shot API call, not a direct API invocation.

The eight completed text files in `corrected/` are the ground truth. Only those Markdown texts are references; copied run metadata, instructions, and raw files in that directory are excluded. Original model-response snapshots remain the predictions, even when editable result copies differ.

## Running additional models

See the [results index](results/index.md) for the additional model runs and their manifests.

The [interactive dashboard](results/index.html) is a self-contained HTML file with inline JavaScript, styles, metrics, and extraction text. It works offline and includes timing/token charts, input and model filters, a response viewer, failure records, and CSV export. Rebuild it from all saved run manifests with:

```sh
python3 results/build-index.py
```

Agent timing and token counts were not captured and are shown as unavailable. Successful-request timing excludes failed attempts; token charts include failed-request usage when reported. These metrics compare execution resources, not extraction accuracy.

## Ground-truth evaluation

The dashboard now shows text content F1, exact-number F1, per-input scores, reference text, omissions/additions, and ordered normalized differences. It also keeps timing and token charts. Rebuilding the dashboard regenerates `results/evaluation.json` and all scores; no third-party scoring package or model judge is required.

Run `python3 evaluate.py` for a ranked console report and `python3 -m unittest discover -s tests -v` for the scoring checks. See [EVALUATION.md](EVALUATION.md) for the precise normalization rules, formulas, and interpretation. Ground-truth texts are read without modification. SHA-256 hashes identify the exact references and predictions used.

The primary rank uses mean content F1 across all eight inputs with equal weights. Empty/failed extractions score zero. Character error rate is an ordered diagnostic, so layout reordering does not lower the headline score. Content F1 does not verify table-cell placement.

## GitHub Pages

The workflow in `.github/workflows/pages.yml` tests scoring, rebuilds the evaluated dashboard, and publishes only the generated `index.html` at the site root. It does not publish the raw-result directories as website assets. The workflow builds privately but deploys only for a public repository; the current account plan rejected Pages for this private repository. Repository visibility must be approved before enabling public Pages.


Gemini High was stopped at user request after six successful extractions. Its two-column request returned no final text and reported a denied RunCommand action; its wide-table request was cancelled. Both are recorded as failures without retry.

Standalone per-image prompts are saved in `benchmark-prompts/`. They use the current shared instruction, including `[?]` for unreadable text and conversion of Asian numeral characters to ordinary digits.

Run the installed CLIs using:

```sh
python3 run-cli-benchmark.py agy --workers 3
python3 run-cli-benchmark.py llm --workers 3
```

The `agy` run selects `gemini-3.8-flash-low`, `gemini-3.8-flash-medium`, and `gemini-3.8-flash-high`. Each request starts in a separate workspace containing only its input image. The `llm` run selects `anthropic/claude-opus-5-5`, `anthropic/claude-haiku-5-5`, and `anthropic/claude-sonnet-5-5`, supplying the PNG with `-a`. Claude reasoning settings are left at provider defaults. Every CLI task starts a fresh conversation.

GPT-6 Luna runs use independent Codex agents at low, medium, and high reasoning effort, with one fresh agent per input. CLI and agent runs use different execution environments; `run.json` records the exact prompts, model settings, input hashes, backend, and completion status. CLI runs also retain the raw JSON response and stderr under `raw/`.

For Claude, the itinerary PNG needs lossless recompression to fit the provider's encoded image limit. Its prepared attachment is retained under `raw/inputs/`; identical decoded pixels are verified and recorded in the manifest. The canonical input in `files/` stays unchanged. Failed transport attempts are retained under `raw/attempts/`.

The runner resumes completed tasks without overwriting their outputs. Its `--models`, `--tasks`, and `--date` options can select a subset or a new run date.
