# October 2026 OpenRouter cohort

Availability was checked on 2026-10-26 against the public [OpenRouter model catalog](https://openrouter.ai/api/v1/models) and each model's endpoints API. The five configurations below advertise image input and have serving endpoints. The installed llm-openrouter 0.7.1 plugin already recognizes all five; no plugin update is needed.

| Configuration | Exact llm model ID |
|---|---|
| DeepSeek V4.1 Flash 1017 | `openrouter/deepseek/deepseek-v4.1-flash-1017` |
| MiMo V2.6 Pro | `openrouter/xiaomi/mimo-v2.6-pro` |
| MiMo V2.6 Flash | `openrouter/xiaomi/mimo-v2.6-flash` |
| NVIDIA Nemotron 3.5 Super VL | `openrouter/nvidia/nemotron-3.5-super-vl` |
| Meta Muse Spark Open | `openrouter/meta/muse-spark-open` |

Jina OCR v1 was absent from the catalog and is skipped. The newer DeepSeek 1017 checkpoint is selected rather than duplicating its September predecessor. Standard MiMo Pro and Nemotron endpoints are selected; UltraSpeed and free-serving variants are not separate model tests.

Each configuration receives all eight inputs in order, with only one request active at a time across the cohort. Each image starts a fresh llm conversation using the unchanged extraction instruction, including conversion of numeric Asian characters to ordinary digits. Canonical PNGs are attached directly, no tools are supplied, and corrected references are never sent. Reasoning settings remain at provider defaults, which can differ between models. Each request has the same 660-second timeout as the earlier CLI trials; failures remain failures without automatic retries.

Every finished run retains its instructions, input and output hashes, raw response JSON, stderr where returned, elapsed request time, reported usage and charges, CLI/plugin versions, and a public catalog snapshot. Usage not returned by a failed request remains unavailable. Reasoning tokens are not added again to output-token totals. Content-v3 evaluation uses the same eight unchanged ground-truth files and scoring rules as all existing models. Results are rebuilt and published as each configuration finishes.
