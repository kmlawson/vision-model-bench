# Visual text extraction benchmark

This workspace benchmarks how well the visual models of different LLMs extract text and tables from document images. Benchmark inputs are in `files/`. The two PDF inputs have been rendered to PNG at 200 DPI using Poppler, saved with their original base names, and the PDFs removed. `itinerary.png` is converted from `itinerary.heic`, whose original is retained; use the PNG for benchmark runs.

Save outputs under `results/[model-name]/[date]/`, using an ISO date (`YYYY-MM-DD`). Use one Markdown output per input, with the input's base filename: for example, `results/gpt-6-astra-low/2026-10-12/difficult-table.md`. Include run metadata so the model, reasoning effort, prompts, and input preparation are reproducible.

Numbers written with Asian numeral characters should be converted to ordinary Western digits (`0-9`), while the surrounding text remains in its original language.

The reusable task instructions are in [agent-instructions.md](agent-instructions.md). Each task should run independently in a fresh agent, approximating a one-shot API request. Use visual input only; do not use OCR, PDF text layers, external sources, other agents' results, or a reference answer. Preserve raw model responses without editorial correction. PDF rasterization and HEIC-to-PNG conversion are permitted for image viewing.

The initial run uses `gpt-6-astra` with reasoning effort `low`, recorded as `gpt-6-astra-low` in the results directory. This is a fresh-agent approximation of a one-shot API call, not a direct API invocation.

The eight completed text files in `corrected/` are the ground truth. Only those Markdown texts are references; copied run metadata, instructions, and raw files in that directory are excluded. Original model-response snapshots remain the predictions, even when editable result copies differ.

## Running additional models

See the [results index](results/index.md) for the additional model runs and their manifests.

The [interactive dashboard](results/index.html) is a self-contained HTML file with inline JavaScript, styles, metrics, and extraction text. It works offline, with embedded clickable image thumbnails, a full-resolution image viewer, side-by-side colored extraction and reference text, error hover hints, and timing/token/cost charts, input and model filters, a response viewer, failure records, and CSV export. Rebuild it from all saved run manifests with:

```sh
python3 results/build-index.py
```

Agent timing and token counts were not captured and are shown as unavailable. Successful-request timing excludes failed attempts; token charts include failed-request usage when reported. These metrics compare execution resources, not extraction accuracy.

## Ground-truth evaluation

The dashboard shows an overall average F1 chart (the arithmetic mean of text and number F1), text content F1, exact-number F1, independent chart and table sorting, a language/numeral-group comparison, per-input scores, reference text, omissions/additions, and ordered normalized differences. The input groups are English only (1, 3, 6, 8), English plus Asian text with Western numerals (1, 2, 3, 6, 8), and Japanese (4, 5, 7). The middle group includes the English set plus Chinese input 2. Their chart uses equal input weights and offers text, number, or overall average F1; date/family filters apply while the single-input filter does not. Full-group scores are included in the evaluation report and CSV export. Per-input exact 100% scores are light green and scores below 90% are light red. Extraction and ground-truth text use smaller type and flow down the whole page. It also keeps timing and token charts. The date selector defaults to All dates so runs that cross midnight can be compared. Active runs are excluded until finished; pending responses are not scored as failures. Rebuilding the dashboard regenerates `results/evaluation.json` and all scores; no third-party scoring package or model judge is required.

Run `python3 evaluate.py` for a ranked console report and `python3 -m unittest discover -s tests -v` for the scoring checks. See [EVALUATION.md](EVALUATION.md) for the precise normalization rules, formulas, and interpretation. Ground-truth texts are read without modification. SHA-256 hashes identify the exact references and predictions used.

The primary rank uses mean content F1 across all eight inputs with equal weights. Empty/failed extractions score zero. Character error rate is an ordered diagnostic, so layout reordering does not lower the headline score. Content F1 does not verify table-cell placement.

## GitHub Pages

The public dashboard is at [kmlawson.github.io/vision-model-bench](https://kmlawson.github.io/vision-model-bench/). The repository was made public with approval to enable Pages. The workflow in `.github/workflows/pages.yml` tests scoring, rebuilds the evaluated dashboard, and publishes the generated `index.html` at the site root after each push to `main`.


Gemini High was stopped at user request after six successful extractions. Its two-column request returned no final text and reported a denied RunCommand action; its wide-table request was cancelled. Both are recorded as failures without retry.

Standalone per-image prompts are saved in `benchmark-prompts/`. They use the current shared instruction, including `[?]` for unreadable text and conversion of Asian numeral characters to ordinary digits.

Run the installed CLIs using:

```sh
python3 run-cli-benchmark.py agy --workers 3
python3 run-cli-benchmark.py llm --models claude-opus-5.5 claude-haiku-5.5 claude-sonnet-5.5 --workers 3
python3 run-cli-benchmark.py codex --models gpt-6.1-sol-low gpt-6.1-sol-medium gpt-6.1-sol-high --workers 3
python3 run-cli-benchmark.py codex --models gpt-6-astra-low-cli gpt-6-luna-low-cli gpt-6-luna-medium-cli gpt-6-luna-high-cli --workers 1
python3 run-cli-benchmark.py llm --models qwen3.5-35b-a3b qwen3.7-flash qwen3.8-flash --workers 1
```

The `agy` run selects `gemini-3.8-flash-low`, `gemini-3.8-flash-medium`, and `gemini-3.8-flash-high`. Each request starts in a separate workspace containing only its input image. The Claude `llm` command selects `anthropic/claude-opus-5-5`, `anthropic/claude-haiku-5-5`, and `anthropic/claude-sonnet-5-5`, supplying the PNG with `-a`. Claude reasoning settings are left at provider defaults. Every CLI task starts a fresh conversation.

GPT-6 Luna runs use independent Codex agents at low, medium, and high reasoning effort, with one fresh agent per input. CLI and agent runs use different execution environments; `run.json` records the exact prompts, model settings, input hashes, backend, and completion status. CLI runs also retain the raw JSON response and stderr under `raw/`.

CLI reruns of Astra Low and Luna Low/Medium/High use directories ending in `-cli`, preserving the earlier fresh-agent outputs. They run consecutively with timing and reported token usage captured.

GPT-6.1 Sol runs use the installed Codex CLI at low, medium, and high effort. In this CLI, `-p` selects a configuration profile; `codex exec` is the noninteractive command. Each image is attached with `--image` in a fresh temporary workspace, using explicit `model_reasoning_effort`, a read-only sandbox, ephemeral sessions, and no user configuration. The shared extraction prompt is followed by an instruction to return only the extraction without using tools. Raw JSONL events and stderr are retained. `stdout.json` is a normalized wrapper around the original final message and reported turn usage; reported reasoning tokens are shown without adding them again to output-token totals.

Qwen runs use `openrouter/qwen/qwen3.5-35b-a3b`, `openrouter/qwen/qwen3.7-flash`, and `openrouter/qwen/qwen3.8-flash` through the installed `llm-openrouter` plugin. These models run consecutively with `--workers 1`, with one fresh request per image and provider-default reasoning settings. Canonical input images are attached directly. The dashboard includes reasoning tokens, cached tokens, and provider-reported charges from the raw OpenRouter usage object. These are recorded charges, rather than estimates from a pricing table. See [OpenRouter usage accounting](https://github.com/OpenRouterTeam/docs/blob/main/cookbook/administration/usage-accounting.mdx) for the reported fields.

For Claude, the itinerary PNG needs lossless recompression to fit the provider's encoded image limit. Its prepared attachment is retained under `raw/inputs/`; identical decoded pixels are verified and recorded in the manifest. The canonical input in `files/` stays unchanged. Failed transport attempts are retained under `raw/attempts/`.

The runner resumes completed tasks without overwriting their outputs. Its `--models`, `--tasks`, and `--date` options can select a subset or a new run date.

## Future blind-with-analysis category

The [proposed benchmark plan](docs/blind-with-analysis-benchmarks.md) describes isolated analysis tools, ground-truth access restrictions, leakage checks, measurement, and a separate OCR category. It is saved for later implementation; no tools-enabled cohort has been started.
