# Benchmark results: 2026-10-12

Open [the interactive dashboard](index.html) for timing and token charts, filters, failure details, and all saved extraction text. It is self-contained and works offline. Rebuild with `python3 results/build-index.py` from the project root.

The nine new configurations produced 70 saved extractions. Gemini High has six saved outputs and two failures, with no retry at user request. The earlier Astra run adds eight saved extractions to the dashboard. Original responses are retained. Work-in-progress corrected files are excluded from the dashboard until the user says they are done. Extraction accuracy is unscored; no reference answer has been selected.

| Configuration | Backend | Saved outputs | Status | Run details |
|---|---|---:|---|---|
| [gemini-3.8-flash-low](gemini-3.8-flash-low/2026-10-12/) | agy | 8/8 | completed | [Metadata](gemini-3.8-flash-low/2026-10-12/run.json) |
| [gemini-3.8-flash-medium](gemini-3.8-flash-medium/2026-10-12/) | agy | 8/8 | completed | [Metadata](gemini-3.8-flash-medium/2026-10-12/run.json) |
| [gemini-3.8-flash-high](gemini-3.8-flash-high/2026-10-12/) | agy | 6/8 | failed | [Metadata](gemini-3.8-flash-high/2026-10-12/run.json) |
| [claude-opus-5.5](claude-opus-5.5/2026-10-12/) | llm | 8/8 | completed | [Metadata](claude-opus-5.5/2026-10-12/run.json) |
| [claude-haiku-5.5](claude-haiku-5.5/2026-10-12/) | llm | 8/8 | completed | [Metadata](claude-haiku-5.5/2026-10-12/run.json) |
| [claude-sonnet-5.5](claude-sonnet-5.5/2026-10-12/) | llm | 8/8 | completed | [Metadata](claude-sonnet-5.5/2026-10-12/run.json) |
| [gpt-6-luna-low](gpt-6-luna-low/2026-10-12/) | Codex fresh subagents | 8/8 | completed | [Metadata](gpt-6-luna-low/2026-10-12/run.json) |
| [gpt-6-luna-medium](gpt-6-luna-medium/2026-10-12/) | Codex fresh subagents | 8/8 | completed | [Metadata](gpt-6-luna-medium/2026-10-12/run.json) |
| [gpt-6-luna-high](gpt-6-luna-high/2026-10-12/) | Codex fresh subagents | 8/8 | completed | [Metadata](gpt-6-luna-high/2026-10-12/run.json) |

Exact prompts, input hashes, model settings, and status are in each run manifest. CLI runs retain raw responses under `raw/`.

Claude uses provider-default reasoning settings. Its itinerary attachment was losslessly recompressed with identical pixels, and the initial rejected requests are preserved under `raw/attempts/`.

Agent timing and token metrics were not captured and are shown as unavailable. Successful CLI durations exclude failed attempts; token charts include captured failure usage.

The earlier [Astra Low run](gpt-6-astra-low/2026-10-12/) uses earlier prompt revisions, recorded in its manifest. The new runs use `[?]` for unreadable text and convert Asian numeral characters to ordinary digits.
