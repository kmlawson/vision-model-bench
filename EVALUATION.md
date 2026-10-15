# Evaluation against corrected text

`corrected/[input-base-name].md` supplies the eight references. The other copied files in `corrected/` are not references. Predictions always come from retained original response JSON; edited model-result Markdown files are never scored as predictions. Reference files are not rewritten.

Rebuild all scores and the offline dashboard with `python3 results/build-index.py`. Run `python3 evaluate.py` for the console ranking. Both regenerate `results/evaluation.json`, containing reference and prediction SHA-256 hashes, the scoring version, every score, mismatch inventories, and ordered comparison details. `evaluate.py` uses only the Python standard library.

## Headline: text content F1

After normalization, content units are Latin words, individual CJK characters, and atomic numeric values. Counts matter: a token repeated three times in the reference requires three matches. Let M be the sum of the intersection of the reference and prediction token-count multisets, R the reference count, and P the prediction count:

- Precision = M / P: how much returned content matches.
- Recall = M / R: how much reference content was recovered.
- F1 = 2M / (R + P): balances omissions and additions.

The model ranking is the arithmetic mean of its eight input F1 scores. Each input has equal weight, preventing a long prose page from dominating the shorter tables. Missing responses receive zero. Gemini High's two failures stay in the denominator.

Token order does not affect this score. Reordered paragraphs, table rows, or columns with the same content get full credit. This also means the score does not establish table-cell placement or correct word order: it measures content recovery, not structural fidelity. Use the ordered diagnostic and comparison viewer to inspect such cases.

## Exact-number F1

The same multiset formula applies only to complete numeric values. A single incorrect digit makes that whole value fail to match. Thousands commas (including the ideographic `、` used as a thousands separator, so `5、158` and `5,158` agree), Unicode width, leading zeros, and trailing decimal zeros are normalized: `1,234.00` and `1234` are equal. Numbers in numeric Asian quantity/date/ordinal contexts are converted, so `二萬`, `2萬`, and `20,000` agree. Proper names such as `三笠山` are preserved. Itinerary clock styles such as `05・23` and `5:23` agree. Repeated numbers must match in count; their row/column association is not established by this metric.

## Ordered diagnostic: character error rate

Exact unit-cost Levenshtein distance over normalized character streams counts the minimum insertions, deletions, and substitutions. CER = distance / reference character count. Lower is better. CER can exceed 100% if output contains much extra content. It is not folded into the headline ranking because layout and reading-order differences can increase it.

The dashboard's diff aligns normalized content tokens with a sequence matcher for readable context. These diff hunks are an inspection aid; they are not the minimal Levenshtein edit decomposition and are not additional score penalties.

## Normalization policy (content-v2)

- Strip HTML/Markdown presentation, table separators, code fences, and hyperlink destinations; retain visible link text.
- Apply Unicode NFKC and case folding. Width, ligature, superscript, and quote styles become comparable. Traditional and modern CJK glyphs remain distinct when NFKC does not equate them.
- Ignore punctuation and layout whitespace. Numeric signs and decimal values remain meaningful. Currency and percent-symbol placement is not scored; textual unit labels remain content.
- Join English words broken by line-end hyphens.
- Normalize numeric representations as described above. Asian numerals inside nonnumeric proper names are not changed. Era `元年` and `1年` agree. The source's `ます〳〵` repetition notation and `ますます` agree.
- Convert `[?]`, `[illegible]`, and `[unreadable]` to an unknown token. They do not match known reference content and are not given wildcard credit.

This is literal transcription scoring, not semantic paraphrase grading. A different spelling or CJK glyph may convey similar meaning and still be a transcription error. No reference values are repaired by arithmetic assumptions or by another LLM.

## Verification

`python3 -m unittest discover -s tests -v` checks formatting invariance, reordered-layout tolerance, numeric aliases, preservation of proper names, wrong digits, unknown text, failed requests, and genuine spelling errors. Exact character distance is cross-checked against an independent dynamic-programming implementation on randomized short strings.

The extraction viewer colors matching content green and surplus/incorrect content red, using the same normalized token counts as the headline score. Exact contextual matches are assigned first, then reordered matches. Source spelling and layout are preserved. Hover or keyboard-focus red spans for nearby normalized ground-truth replacements; these suggestions use text alignment and can be ambiguous when a table is reordered. Missing reference units are listed separately. These display annotations do not change any score. Input thumbnails open embedded full-resolution images and support original-size inspection without a network connection.
