# Changelog

## 1.0.2 (2026-10-09, fitzyracing-rouge fork)

Based on rouge 1.0.1. Distribution name `fitzyracing-rouge`; the import name is still `rouge` and
the `rouge` command is unchanged.

- Fix phantom overlap from whitespace-only sentence segments (upstream #77, PR #78): in texts such
  as `"cat. "` or `"the cat. . dog"`, the blank segment between or after periods became an empty
  `""` token that every such text shared, so unrelated texts got non-zero ROUGE
  (`"the cat. . dog"` vs `"a bird. . fish"`: rouge-1 f 0.25, now 0). **Score change:** only for
  inputs where a hypothesis or reference contains a whitespace-only segment (whitespace right
  after a period, before the next period or the end of the text) next to real words. Texts made
  only of whitespace and periods are scored exactly as in 1.0.1 (no new "Hypothesis is empty."
  errors).
- Include upstream PR #69 (merged on master in 2024, never released): ROUGE-L no longer hits
  `RecursionError` on long sentences (from roughly 700 to 1,000 words in one sentence, depending on the text); results are otherwise identical.
- Packaging: `pyproject.toml` replaces `setup.py`.
- Tests: add `tests/test_fork_fixes.py`. The three upstream tests in `tests/test_basic.py` already
  fail on 1.0.1 (their 2017 expected scores predate later upstream changes) and are left as is.

## 1.0.1 (2021-07-20) and earlier

See the [upstream history](https://github.com/pltrdy/rouge/commits/master).
