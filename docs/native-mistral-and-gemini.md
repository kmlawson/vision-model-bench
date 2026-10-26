# Native Mistral and Gemini benchmarks

Availability checked on 2026-10-26 using the configured accounts' model-list APIs. Only key names were displayed; secret values are never written to benchmark files or command arguments.

- Mistral's [Large 4 announcement](https://mistral.ai/news/mistral-large-4/) identifies it as its largest and most capable model. It is a public preview with image input. The authenticated Mistral model catalog confirms `mistral-large-4`, vision support, and alias `mistral-large-4-0`. Run `llm -m mistral/mistral-large-4` with llm-mistral 0.16 after `llm mistral refresh`.
- Google's [Argon documentation](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon) identifies `gemini-4-argon` as the flagship reasoning model with image input. The authenticated Gemini catalog lists it with `generateContent` support. `llm-gemini` was absent from the environment, so `llm install -U llm-gemini` installed version 0.35. Existing llm 0.36, llm-openrouter 0.7.1, and llm-mistral 0.16 were unchanged. Run `llm -m gemini/gemini-4-argon`.

These native runs follow the earlier OpenRouter cohort, with no overlapping benchmark requests. Each image gets one fresh CLI invocation, no tools, no corrected references, no retries, the same canonical PNG and prompt, and the same 660-second timeout. Provider-default reasoning is not overridden. Argon's documented default thinking level is medium; the actual submitted options and resolved model versions are recorded.

Original response JSON and stderr, request timing, model metadata, token usage, and hashes are retained. Native APIs may omit charge or reasoning fields; omitted values remain unavailable. Gemini's plugin combines candidate and thought tokens in output totals. Thought and cache details are displayed separately, without double counting. Scoring uses content-v3 and the unchanged eight ground-truth files, with failed requests receiving zero credit.
