# Getting started

## Install

```
pip uninstall -y rouge && pip install fitzyracing-rouge
```

The import name is still `rouge`. It depends on `six`.

## Usage

`from rouge import Rouge; Rouge().get_scores(hyp, ref)`. Console script: `rouge` (`bin.rouge_cmd:main`).

## Develop and test

```
pip install -e . pytest
pytest tests/
```
