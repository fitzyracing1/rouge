# fitzyracing-rouge (rouge)

> Part of **[360 Bench](https://github.com/fitzyracing1/360-bench)**, tested fixes for abandoned PyPI packages.

[![PyPI](https://img.shields.io/pypi/v/fitzyracing-rouge.svg)](https://pypi.org/project/fitzyracing-rouge/)

> **This is a fork of [rouge](https://github.com/pltrdy/rouge) by [pltrdy](https://github.com/pltrdy)**
> and its contributors, published as a drop-in replacement. The upstream package (~640k
> downloads a month, widely used to score summaries and LLM output) has not been released since
> 1.0.1 (July 2021). The import name is still `rouge`, so no code changes are needed. All
> credit for the original library goes to its author and contributors; it remains available
> under the same Apache-2.0 license (see [LICENSE](LICENSE) and [NOTICE](NOTICE)).
>
> If a fixed `rouge` release appears on PyPI, prefer it and switch back.


## What's fixed in this fork

Based on upstream `rouge==1.0.1` (tag [`1.0.1`](https://github.com/pltrdy/rouge/tree/1.0.1)).
The API is unchanged. Scores are identical to 1.0.1 except for the inputs described in the
first item.

- **Unrelated texts no longer share a phantom empty word.** rouge splits each text on periods
  and dropped empty segments *before* collapsing whitespace, so a segment made only of
  whitespace (the `" "` in `"cat. "`, or between the periods in `"the cat. . dog"`) survived
  as an empty sentence and was counted as an empty `""` word. Two texts that both had one
  then "overlapped" on it:

  ```python
  from rouge import Rouge
  Rouge().get_scores("the cat. . dog", "a bird. . fish")[0]["rouge-1"]
  # 1.0.1: {'r': 0.25, 'p': 0.25, 'f': 0.249...}
  # fork:  {'r': 0.0, 'p': 0.0, 'f': 0.0}
  Rouge().get_scores("cat. ", "dog. ")[0]["rouge-1"]
  # 1.0.1: {'r': 0.5, 'p': 0.5, 'f': 0.499...}
  # fork:  {'r': 0.0, 'p': 0.0, 'f': 0.0}
  ```

  The same happened to an empty model output (`" "`) scored against a reference that ends with
  `". "`. Text with a space or newline after its last period is common in LLM output, so this
  quietly inflated ROUGE in evaluations. The fork drops whitespace-only segments.

  **Exactly which scores change:** only pairs where the hypothesis or the reference has a
  whitespace-only segment next to real words, that is whitespace (spaces, tabs, newlines,
  Unicode spaces) directly after a period and followed by another period or the end of the
  text. Those pairs now get exactly the scores they would get without the blank segment
  (`"the cat. . dog"` scores like `"the cat. dog"`, `"cat. "` like `"cat"`). All other inputs
  score exactly as in 1.0.1 (checked against 1.0.1 on 30,000 random text pairs). Texts made
  *only* of whitespace and periods (for example an empty LLM generation `" "`) are scored
  exactly as in 1.0.1 too, rather than raising `ValueError: Hypothesis is empty.` like `""`
  does, so evaluation loops keep running. `return_lengths` values don't change.

  Upstream issue: [#77](https://github.com/pltrdy/rouge/issues/77); unmerged PR:
  [#78](https://github.com/pltrdy/rouge/pull/78). The fork applies #78's core change (filter
  segments by `strip()`), but leaves out its changes to `ignore_empty` (skipping
  whitespace-only pairs, returning `[]` or raising `ValueError` when nothing is left), and keeps
  whitespace-only texts working.

- **ROUGE-L no longer crashes with `RecursionError` on long sentences.** The longest common
  subsequence was rebuilt recursively, one call per word, so a single sentence of roughly
  700 to 1,000 words (for example an LLM answer without periods) exceeded Python's recursion
  limit. This is upstream PR [#69](https://github.com/pltrdy/rouge/pull/69) by
  [@Lppy](https://github.com/Lppy), which the maintainer merged in November 2024 but never
  released; it is included unchanged (commit `4b57032`). It gives identical results (checked
  on 40,000 random cases).

- **Packaging:** `pyproject.toml` replaces `setup.py`. The same modules are installed as
  before, including the `rouge` command. `rouge.__version__` is `"1.0.2"`.

The three upstream tests in `tests/test_basic.py` already fail on 1.0.1 (their expected scores
date from 2017 and predate later upstream changes); they are unchanged.


## Install

```bash
pip install fitzyracing-rouge
```

### Switching from `rouge`

This distribution installs the same `rouge` package and `rouge` command as the original, so
your code keeps doing `from rouge import Rouge`. **Uninstall the original first**, then install
the fork:

```bash
pip uninstall -y rouge
pip install fitzyracing-rouge
```

The order matters. Both distributions own the same files, so if you install the fork first and
uninstall `rouge` afterwards, pip deletes the shared files and the import breaks. If that
happens, run `pip install --force-reinstall --no-deps fitzyracing-rouge`.

In `requirements.txt` / `pyproject.toml`, replace `rouge` with `fitzyracing-rouge`. (This is
`pltrdy/rouge`. Google's `rouge-score` package, imported as `rouge_score`, is a different
project and is not affected.)

### If you get rouge through another package

pip cannot replace a dependency with a differently named package. If a dependency requires
`rouge`, install the fork alongside it and then remove the original's files:

```bash
pip install fitzyracing-rouge
pip uninstall -y rouge
pip install --force-reinstall --no-deps fitzyracing-rouge   # restore the files the uninstall removed
```

Afterwards `pip check` reports `<package> requires rouge, which is not installed`; that is
expected. Repeat the steps if a later install pulls `rouge` back in.

**uv users** can do this properly with an override that drops the original:

```toml
# pyproject.toml
[project]
dependencies = ["fitzyracing-rouge", "...the package that depends on rouge..."]

[tool.uv]
override-dependencies = ["rouge; sys_platform == 'never'"]
```

(or `uv pip install --override overrides.txt ...` with that same line in `overrides.txt`).

### Tests

```bash
pip install -e . pytest
pytest tests/test_fork_fixes.py
```

`tests/test_fork_fixes.py` fails on rouge 1.0.1 and passes on this fork; it also pins scores
that must stay identical to 1.0.1.


## Rouge
*A full Python librarie for the ROUGE metric [(paper)](http://www.aclweb.org/anthology/W04-1013).*

### Disclaimer
This implementation is independant from the "official" ROUGE script (aka. `ROUGE-155`).   
Results may be *slighlty* different, see [discussions in #2](https://github.com/pltrdy/rouge/issues/2).

## Quickstart
#### Clone & Install
```shell
git clone https://github.com/pltrdy/rouge
cd rouge
python setup.py install
# or
pip install -U .
```
or from pip:
```
pip install rouge
```
#### Use it from the shell (JSON Output)
```
$rouge -h
usage: rouge [-h] [-f] [-a] hypothesis reference

Rouge Metric Calculator

positional arguments:
  hypothesis  Text of file path
  reference   Text or file path

optional arguments:
  -h, --help  show this help message and exit
  -f, --file  File mode
  -a, --avg   Average mode

```

e.g. 


```shell
# Single Sentence
rouge "transcript is a written version of each day 's cnn student" \
      "this page includes the show transcript use the transcript to help students with"

# Scoring using two files (line by line)
rouge -f ./tests/hyp.txt ./ref.txt

# Avg scoring - 2 files
rouge -f ./tests/hyp.txt ./ref.txt --avg
```

#### As a library

###### Score 1 sentence

```python
from rouge import Rouge 

hypothesis = "the #### transcript is a written version of each day 's cnn student news program use this transcript to he    lp students with reading comprehension and vocabulary use the weekly newsquiz to test your knowledge of storie s you     saw on cnn student news"

reference = "this page includes the show transcript use the transcript to help students with reading comprehension and     vocabulary at the bottom of the page , comment for a chance to be mentioned on cnn student news . you must be a teac    her or a student age # # or older to request a mention on the cnn student news roll call . the weekly newsquiz tests     students ' knowledge of even ts in the news"

rouge = Rouge()
scores = rouge.get_scores(hypothesis, reference)
```

*Output:*

```json
[
  {
    "rouge-1": {
      "f": 0.4786324739396596,
      "p": 0.6363636363636364,
      "r": 0.3835616438356164
    },
    "rouge-2": {
      "f": 0.2608695605353498,
      "p": 0.3488372093023256,
      "r": 0.20833333333333334
    },
    "rouge-l": {
      "f": 0.44705881864636676,
      "p": 0.5277777777777778,
      "r": 0.3877551020408163
    }
  }
]
```

*Note: "f" stands for f1_score, "p" stands for precision, "r" stands for recall.*

###### Score multiple sentences
```python
import json
from rouge import Rouge

# Load some sentences
with open('./tests/data.json') as f:
  data = json.load(f)

hyps, refs = map(list, zip(*[[d['hyp'], d['ref']] for d in data]))
rouge = Rouge()
scores = rouge.get_scores(hyps, refs)
# or
scores = rouge.get_scores(hyps, refs, avg=True)
```

*Output (`avg=False`)*: a list of `n` dicts:

```
{"rouge-1": {"f": _, "p": _, "r": _}, "rouge-2" : { .. }, "rouge-l": { ... }}
```


*Output (`avg=True`)*: a single dict with average values:

```
{"rouge-1": {"f": _, "p": _, "r": _}, "rouge-2" : { ..     }, "rouge-l": { ... }}
``` 

###### Score two files (line by line)
Given two files `hyp_path`, `ref_path`, with the same number (`n`) of lines, calculate score for each of this lines, or, the average over the whole file. 

```python
from rouge import FilesRouge

files_rouge = FilesRouge()
scores = files_rouge.get_scores(hyp_path, ref_path)
# or
scores = files_rouge.get_scores(hyp_path, ref_path, avg=True)
```

## Documentation

- In-repo docs: [docs/](docs/index.md)
- Wiki: [https://github.com/fitzyracing1/rouge/wiki](https://github.com/fitzyracing1/rouge/wiki)

## Plans

This project is free, and its license stays as is. Support it through [GitHub Sponsors](https://github.com/sponsors/fitzyracing1):

- **Free**: use the code, community support.
- **Pro ($49/month)**: priority issues and support.
- **Team ($199/month)**: priority support for your team plus early access.
