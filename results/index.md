# Benchmark results

Open [the interactive dashboard](index.html) or [the live site](https://kmlawson.github.io/vision-model-bench/). The dashboard is a single offline HTML file with embedded input images, accuracy scores, colored extraction review, timing, tokens, and reported costs.

26 finished configurations, 194 saved extractions out of 208 tasks. Active runs are excluded until finished. Failed or missing final responses score zero; the eight corrected Markdown files are ground truth.

| Configuration | Date | Backend | Saved | Content F1 | Number F1 | Status | Details |
|---|---|---|---:|---:|---:|---|---|
| [claude-opus-5.5](claude-opus-5.5/2026-10-12/) | 2026-10-12 | llm | 8/8 | 97.94% | 94.17% | completed | [Metadata](claude-opus-5.5/2026-10-12/run.json) |
| [gpt-6-astra-low-cli](gpt-6-astra-low-cli/2026-10-13/) | 2026-10-13 | codex | 8/8 | 95.98% | 87.00% | completed | [Metadata](gpt-6-astra-low-cli/2026-10-13/run.json) |
| [gpt-6-astra-low](gpt-6-astra-low/2026-10-12/) | 2026-10-12 | Codex fresh subagents | 8/8 | 95.85% | 87.75% | completed | [Metadata](gpt-6-astra-low/2026-10-12/run.json) |
| [gpt-6.1-sol-low](gpt-6.1-sol-low/2026-10-12/) | 2026-10-12 | codex | 8/8 | 95.61% | 87.91% | completed | [Metadata](gpt-6.1-sol-low/2026-10-12/run.json) |
| [gpt-6.1-sol-medium](gpt-6.1-sol-medium/2026-10-12/) | 2026-10-12 | codex | 8/8 | 95.49% | 86.14% | completed | [Metadata](gpt-6.1-sol-medium/2026-10-12/run.json) |
| [gpt-6.1-sol-high](gpt-6.1-sol-high/2026-10-12/) | 2026-10-12 | codex | 8/8 | 95.13% | 86.90% | completed | [Metadata](gpt-6.1-sol-high/2026-10-12/run.json) |
| [gemini-3.8-flash-low](gemini-3.8-flash-low/2026-10-12/) | 2026-10-12 | agy | 8/8 | 94.79% | 89.47% | completed | [Metadata](gemini-3.8-flash-low/2026-10-12/run.json) |
| [gemini-3.8-flash-medium](gemini-3.8-flash-medium/2026-10-12/) | 2026-10-12 | agy | 8/8 | 94.20% | 87.26% | completed | [Metadata](gemini-3.8-flash-medium/2026-10-12/run.json) |
| [claude-sonnet-5.5](claude-sonnet-5.5/2026-10-12/) | 2026-10-12 | llm | 8/8 | 93.92% | 86.05% | completed | [Metadata](claude-sonnet-5.5/2026-10-12/run.json) |
| [muse-spark-open](muse-spark-open/2026-10-26/) | 2026-10-26 | llm | 8/8 | 91.15% | 77.97% | completed | [Metadata](muse-spark-open/2026-10-26/run.json) |
| [qwen3.5-35b-a3b](qwen3.5-35b-a3b/2026-10-12/) | 2026-10-12 | llm | 8/8 | 86.93% | 71.33% | completed | [Metadata](qwen3.5-35b-a3b/2026-10-12/run.json) |
| [nemotron-3.5-super-vl](nemotron-3.5-super-vl/2026-10-26/) | 2026-10-26 | llm | 8/8 | 83.73% | 71.41% | completed | [Metadata](nemotron-3.5-super-vl/2026-10-26/run.json) |
| [deepseek-v4.1-flash-1017](deepseek-v4.1-flash-1017/2026-10-26/) | 2026-10-26 | llm | 8/8 | 83.56% | 71.37% | completed | [Metadata](deepseek-v4.1-flash-1017/2026-10-26/run.json) |
| [gpt-6-luna-high-cli](gpt-6-luna-high-cli/2026-10-13/) | 2026-10-13 | codex | 8/8 | 80.75% | 71.66% | completed | [Metadata](gpt-6-luna-high-cli/2026-10-13/run.json) |
| [claude-haiku-5.5](claude-haiku-5.5/2026-10-12/) | 2026-10-12 | llm | 8/8 | 80.64% | 75.34% | completed | [Metadata](claude-haiku-5.5/2026-10-12/run.json) |
| [gpt-6-luna-low](gpt-6-luna-low/2026-10-12/) | 2026-10-12 | Codex fresh subagents | 8/8 | 80.09% | 68.19% | completed | [Metadata](gpt-6-luna-low/2026-10-12/run.json) |
| [gpt-6-luna-medium](gpt-6-luna-medium/2026-10-12/) | 2026-10-12 | Codex fresh subagents | 8/8 | 79.52% | 66.57% | completed | [Metadata](gpt-6-luna-medium/2026-10-12/run.json) |
| [gpt-6-luna-low-cli](gpt-6-luna-low-cli/2026-10-13/) | 2026-10-13 | codex | 8/8 | 79.37% | 68.66% | completed | [Metadata](gpt-6-luna-low-cli/2026-10-13/run.json) |
| [gpt-6-luna-high](gpt-6-luna-high/2026-10-12/) | 2026-10-12 | Codex fresh subagents | 8/8 | 79.30% | 68.65% | completed | [Metadata](gpt-6-luna-high/2026-10-12/run.json) |
| [mimo-v2.6-flash](mimo-v2.6-flash/2026-10-26/) | 2026-10-26 | llm | 7/8 | 75.45% | 68.26% | incomplete | [Metadata](mimo-v2.6-flash/2026-10-26/run.json) |
| [gpt-6-luna-medium-cli](gpt-6-luna-medium-cli/2026-10-13/) | 2026-10-13 | codex | 8/8 | 75.04% | 69.71% | completed | [Metadata](gpt-6-luna-medium-cli/2026-10-13/run.json) |
| [qwen3.8-flash](qwen3.8-flash/2026-10-12/) | 2026-10-12 | llm | 6/8 | 71.43% | 68.68% | incomplete | [Metadata](qwen3.8-flash/2026-10-12/run.json) |
| [gemini-3.8-flash-high](gemini-3.8-flash-high/2026-10-12/) | 2026-10-12 | agy | 6/8 | 71.12% | 66.44% | failed | [Metadata](gemini-3.8-flash-high/2026-10-12/run.json) |
| [mimo-v2.6-pro](mimo-v2.6-pro/2026-10-26/) | 2026-10-26 | llm | 7/8 | 59.48% | 57.80% | incomplete | [Metadata](mimo-v2.6-pro/2026-10-26/run.json) |
| [kimi-k3.1-pro](kimi-k3.1-pro/2026-10-26/) | 2026-10-26 | llm | 4/8 | 49.70% | 49.43% | incomplete | [Metadata](kimi-k3.1-pro/2026-10-26/run.json) |
| [qwen3.7-flash](qwen3.7-flash/2026-10-12/) | 2026-10-12 | llm | 4/8 | 48.31% | 48.23% | incomplete | [Metadata](qwen3.7-flash/2026-10-12/run.json) |

Exact prompts, input hashes, model settings, original responses, and failure details are retained in each run directory. Scores always use original responses, preserving any user-edited copies.

The earlier Astra agent run uses earlier prompt revisions. CLI reruns have names ending in `-cli`; the original agent runs remain available. Agent time and token counts were not captured and remain unavailable. CLI timing includes startup; task totals sum request durations. Provider-reported charges are shown where available. Claude itinerary attachments were losslessly recompressed with identical decoded pixels.

Rebuild this index, the HTML dashboard, and the evaluation report with `python3 results/build-index.py`. Completed model runs are committed and pushed as they finish.
