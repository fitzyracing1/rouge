# fitzyracing-rouge

`fitzyracing-rouge` is a drop-in fork of [rouge](https://github.com/pltrdy/rouge) and part of [360 Bench](https://github.com/fitzyracing1/360-bench). It is based on upstream `rouge==1.0.1`, and the API is unchanged. All credit for the original library goes to its authors and contributors.

## What the fork fixes (summary of [README.md](../README.md))

- Whitespace-only sentence segments are no longer counted as a shared empty word, so unrelated texts no longer get inflated scores.
- ROUGE-L no longer crashes with `RecursionError` on long sentences.
- Packaging moved to `pyproject.toml`.

The full details and links to the upstream issues are in [README.md](../README.md).

Pages: [Getting started](getting-started.md) · [Architecture](architecture.md) · [Contributing](contributing.md)

This repo has no CI workflow.

## License

Apache-2.0 (see LICENSE and NOTICE). The original notice is kept: Copyright pltrdy and the rouge contributors.
Modifications: Copyright (c) 2026 Joshua Almeida.
