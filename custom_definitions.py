"""Adds your own dialect and view, in the format of auditfile-spec, reads an audit file and runs the view.

Usage: python custom_definitions.py <file.xaf> [continuation files...]
"""

from __future__ import annotations

import datetime as dt
import sys
from decimal import Decimal
from pathlib import Path

from xml_auditfile import Auditfile, AuditfileSource, MemorySink, TextLanguage, ViewResult
from xml_auditfile.values import to_text

DEFINITIONS = Path(__file__).resolve().parent / "definitions"


def main(files: list[str]) -> int:
    # The definitions sit next to the built-in ones of the package; a file is refused as a whole when anything is wrong.
    # The reader never opens files itself, so read the JSON and hand over the text (or the parsed object).
    # They are added before the arguments are checked, so a run without arguments still checks definitions/.
    dialects = Auditfile.dialects.add("xaf/3.2", (DEFINITIONS / "dialects.json").read_text("utf-8"))
    views = Auditfile.views.add((DEFINITIONS / "views.json").read_text("utf-8"))
    print(f"Added    : dialect {', '.join(d.name for d in dialects)}; view {', '.join(v.name for v in views)}")

    if not files:
        print("Usage: python custom_definitions.py <file.xaf> [continuation files...]")
        return 2

    sink = MemorySink()
    source = AuditfileSource.from_factories(*((Path(p).name, lambda p=p: open(p, "rb")) for p in files))
    report = Auditfile.read(source, sink)

    # An added dialect is recognized like a built-in one: by namespace or by header/softwareDesc.
    schema = report.schema
    print(f"Version  : {schema.version_key if schema else '-'} ({schema.source.value if schema else '-'})")
    print(f"Dialect  : {(schema.dialect if schema else None) or '-'}")
    print(f"Loaded   : {report.loaded}")

    # An added view is found like a built-in one; a view that does not fit the version reports XAF-Q001.
    view = schema.version.find_view("account_activity") if report.loaded and schema and schema.version else None
    if view is not None:
        # Parameters filter the input rows; None leaves a filter out.
        result = sink.run(view, {"period_from": None, "period_to": None}, TextLanguage.ENGLISH)
        print()
        print(f"{(view.label.get(TextLanguage.ENGLISH) if view.label else None) or view.name} ({len(result.rows)} rows)")
        for diagnostic in result.diagnostics:
            print(f"  {diagnostic}")

        print_table(result, 20)

    print()
    for diagnostic in report.diagnostics:
        print(diagnostic)

    print("Valid." if report.is_valid else "Not valid.")
    return 0 if report.is_valid else 1


def print_table(result: ViewResult, max_rows: int) -> None:
    width = 16
    numeric = [any(isinstance(r[i], (Decimal, int)) for r in result.rows) for i in range(len(result.columns))]

    def line(values: list[str]) -> str:
        out = []
        for i, v in enumerate(values):
            v = v if len(v) <= width else v[: width - 1] + "…"
            out.append(v.rjust(width) if numeric[i] else v.ljust(width))
        return "  " + "  ".join(out)

    print(line([(c.label.get(TextLanguage.ENGLISH) if c.label else None) or c.name for c in result.columns]))
    for row in result.rows[:max_rows]:
        print(line([to_text(v.date() if isinstance(v, dt.datetime) else v) for v in row]))

    if len(result.rows) > max_rows:
        print(f"  … {len(result.rows) - max_rows} more")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
