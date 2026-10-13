# Blind-with-analysis benchmark plan

This is a proposal for a future benchmark category. It does not enable tools, launch model requests, or replace the existing results.

The purpose is to measure how accurately models extract the same eight inputs when they can analyze the supplied image with tools, while remaining unable to obtain corrected answers or other models' outputs. Keep this category separate from the existing visual-extraction trials.

## Current baseline

The existing prompts prohibit OCR, external sources, reference answers, and other task outputs. The Codex CLI trials were verified to have zero tool calls. Earlier fresh agents used tools to view images and save their extractions; agy also uses an agent environment for visual inspection. Thus, the existing trials are visual extraction with further analysis prohibited, rather than a universally tool-free execution environment.

## The isolation boundary

Prompt instructions are useful but are not an access-control mechanism. A temporary working directory does not prevent a shell from reading other absolute paths. A read-only filesystem setting prevents changes but does not, by itself, hide readable answers.

Keep the evaluator and its `corrected/` files outside the model's tool environment. Only the supplied input and artifacts produced during that one request should be accessible to tools.

Prefer a common tool broker shared across providers:

- Address the source image by an opaque input ID, not an arbitrary filesystem path.
- Expose a small, explicit set of image operations. The broker validates every argument and only operates on that input or its derived images.
- Return image crops and other permitted outputs to the model. Do not expose general file reading, directory listing, Git, browser, search, or shell tools in the initial category.
- Keep API credentials, provider clients, scoring, and corrected text in the trusted orchestration process, outside the tool worker.

If general Python or shell analysis is needed, execute it inside a fresh container or VM. Mount only the current image read-only and a fresh output directory writable. Do not mount the repository, `.git`, `corrected/`, previous results, the host home directory, host configuration, or a container-management socket. Give workers a minimal environment without inherited API keys or host environment variables. Resolve source paths within the allowlist and reject traversal and symlink escapes.

Tool workers should have no outbound network access. The trusted orchestration process can make model API calls separately. Disable provider-hosted browsing/search tools too: they would not be governed by the local worker's network controls. This is particularly important because this repository is public: unrestricted web, GitHub, or Git tools could retrieve `corrected/` directly. Allowing unrestricted web tools would defeat the intended blindness.

## Initial tool set and separate OCR category

Start with deterministic visual-analysis tools:

1. Inspect the supplied image at the available resolution.
2. Crop a specified rectangular region.
3. Rotate the source or a derived crop.
4. Enlarge or zoom into a region.
5. Optionally adjust contrast or perform other agreed image transformations, preserving the original input and logging each operation.

Use the same tool names, parameter schemas, implementation versions, and image-processing defaults for every model. Save derived images with their parent input IDs and transformation parameters.

OCR should be a separate, clearly named subcategory, such as `blind-with-analysis-and-ocr`. Give every model the same OCR engine and version. Otherwise, a comparison may primarily measure different OCR services instead of how the models inspect images and use analysis tools.

General calculations may be useful for examining a transcription, but inferred values must not be silently substituted for unreadable source text. Preserve the benchmark instruction to use `[?]` rather than inventing content.

## Request protocol

- Reuse the eight extraction targets and canonical images from `files/`.
- Create a separate prompt revision that permits the chosen analysis tools and repeated visual inspection. The existing one-inspection instruction must be revised for this category.
- Preserve the existing language, spelling, numeral-conversion, table-association, and unknown-text rules.
- Start a fresh model conversation and tool workspace for every image. Do not share previous outputs or artifacts between requests.
- Fix a common tool-call limit, elapsed-time limit, and output/token budget before starting the cohort. Record actual provider settings and any unsupported options.
- Capture the final extraction without a human correction pass. Do not provide scoring feedback during the request.
- Stop and remove access to the tool worker before evaluation begins. The evaluator then reads the final response and the ground truth in its separate environment.
- Run models and inputs consecutively unless a different execution policy is explicitly agreed.

## Verify blindness before spending benchmark calls

Test the worker or broker directly, using a harmless test harness rather than a model extraction request. Confirm that these operations fail:

- Reading `corrected/`, an absolute host path, another input, or a previous model output.
- Traversing outside the allowed input/output directories, including through symlinks.
- Accessing Git history, repository metadata, host caches, configuration, or credentials.
- Fetching the public repository or its raw corrected files over the network.

Also confirm that the intended crop, rotation, zoom, and output operations succeed. An inaccessible canary outside the worker can supplement these checks, but should not replace the actual isolation boundary.

Log all tool requests, their validated arguments, execution status, and returned artifact IDs. Preserve blocked access attempts as protocol violations. Do not silently mix a trial that accessed forbidden material into valid benchmark results.

## Results and measurement

Use a separate result configuration name, retaining the existing layout:

`results/[model-name]-blind-with-analysis-[effort]/[YYYY-MM-DD]/`

For an OCR-enabled cohort, include `and-ocr` in the configuration name. Never overwrite the earlier agent or CLI trials.

Save the extraction, original provider responses/events, full submitted prompts, tool trace, derived images, input hashes, model identifier, reasoning effort, tool versions, budgets, timestamps, elapsed time, and reported input/output/cached/reasoning tokens. Capture provider-reported charges where available; leave unreported measurements unavailable.

Record failures, timeouts, and protocol violations explicitly. Preserve the initial attempt; any authorized retry should be a distinct recorded attempt or trial.

Evaluate with the existing formatting-tolerant text and exact-number F1 rules. Keep equal weighting per input and failure scores of zero. Report the arithmetic mean of text and number F1 as the existing overall-average view, while retaining both components and the ordered diagnostic differences.

Add a dashboard category filter so visual-extraction, blind-with-analysis, and blind-with-analysis-and-ocr can be compared separately or together. Display tool-call counts, tool time, and violations alongside the current accuracy, latency, tokens, and costs.

## Implementation sequence when authorized

1. Agree on the initial tool menu and common budgets.
2. Build the broker and isolated worker, without adding ground truth to the worker.
3. Implement and pass the access-denial checks above.
4. Prepare and save the new prompt revision and result metadata schema.
5. Run one model/input pilot and inspect its trace, isolation, output, and measurements.
6. Run the agreed cohort, evaluate only after each worker stops, and publish results with their category clearly identified.

Keep `corrected/` unchanged throughout. This plan requires a later instruction to implement or run it.
