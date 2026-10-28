# auditfile-py-samples

Example programs for [auditfile-py](https://github.com/XML-auditfile/auditfile-py), the streaming reader
for Dutch tax audit files (XAF and related).

The samples use the published PyPI package `xml-auditfile`, pinned in `requirements.txt`. Python 3.10 or later.

> Until the first release of `xml-auditfile` is on PyPI, `pip install -r requirements.txt` fails and CI is red.

| File | Shows |
| ---- | ----- |
| `read_to_memory.py` | Read a file into `MemorySink` and print tables, a row with definitions, the views and the diagnostics |
| `validate.py` | Validate a file (XSD, structure, keys, business rules); exit code 0 when valid |
| `custom_definitions.py` | Add your own dialect and view from `definitions/`, read a file and run the view |

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python read_to_memory.py administratie.xaf
.venv/bin/python validate.py administratie.xaf --en
.venv/bin/python custom_definitions.py administratie.xaf
```

On Windows use `.venv\Scripts\` instead of `.venv/bin/`. To use the package in your own project:

```
pip install xml-auditfile
```

All samples accept continuation files after the first file, e.g. `python validate.py <file.xaf> <continuation.xaf>`.

## Custom dialects and views

`definitions/` holds a dialect and a view in the same format as `dialects.json` and `views/<type>.json` of
[auditfile-spec](https://github.com/XML-auditfile/auditfile-spec): `dialects.json` reads files of a package that writes
XAF 3.2 in a deviating namespace with decimal commas, `views.json` adds the view `account_activity` (lines, debit and
credit per account, optionally over a range of periods). `custom_definitions.py` adds them with
`Auditfile.dialects.add("xaf/3.2", json)` and `Auditfile.views.add(json)`; after that the package uses them like its
built-in dialects and views. Change the files or add your own: a file with an error is refused as a whole, with a
message that names the problem. CI runs the sample without a file, which checks the definitions against the package.

## Package versions

The samples use one released version of the package, pinned exactly in `requirements.txt`. Dependabot
(`.github/dependabot.yml`) opens a pull request for each new release, and CI loads every sample against it before it
is merged, so the samples follow the latest version.

## License

Apache License 2.0.
