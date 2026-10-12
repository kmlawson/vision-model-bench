# Reusable extraction instructions

Run each numbered task separately in a fresh agent or as an independent API request, supplying only its corresponding input and the shared extraction instruction below. For the initial run, use model `gpt-6-astra` with reasoning effort `low`.

## Shared extraction instruction

Extract the requested content from the supplied visual input. Preserve the original language, spelling, numbers, punctuation, headings, notes, and reading order. Convert numbers written with Asian numeral characters to ordinary Western digits (0-9), for example 三 → 3 and 二十三 → 23. Normalize full-width digits to 0-9 as well. Preserve surrounding text and units; do not convert characters used as words rather than numbers. Represent tables in Markdown, preserving the association between headers, rows, and values. Use `[?]` for text you cannot read; do not guess or fill gaps. Return only the requested extraction, without explanations, summaries, translations, or commentary. Do not use OCR, embedded PDF text, external sources, reference answers, or other task outputs.

## Tasks

1. Extract just the table title, data, and table notes from the top of `1931-table-english.png`.
2. Extract the text from `difficult-table.png`.
3. Extract the text from the right page of `english-page.png`.
4. Extract the itinerary number 3 from `itinerary.png`.
5. Extract the table of population statistics from `population-stats-japanese.png`.
6. Extract the table title, data, and notes from `sideways-table.png`.
7. Extract the text and tables from `text-two-columns-plus-tables.png`.
8. Extract the text from `wide-table.png`.

## Local agent execution

Inputs are in `files/`. Save each raw extraction to `results/[model-name]/[date]/[input-base-name].md`, with an ISO date (`YYYY-MM-DD`). An orchestrator may render PDFs and convert HEIC to PNG before supplying the visual input. Keep input preparation consistent across models and record it in run metadata.

To approximate a one-shot request, inspect the supplied image once, then write the extraction without a second visual inspection, correction pass, or collaboration with other agents. Tool calls to load the image and save the response are allowed. Do not perform Git operations. The agent's final status message is separate from the saved extraction.
