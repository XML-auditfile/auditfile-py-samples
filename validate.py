"""Validates an audit file: XSD, structure, keys and business rules.

Usage: python validate.py <file.xaf> [--en] [--unverified] [--force xaf/3.2]
Exit code: 0 valid, 1 not valid, 2 usage error.
"""

from __future__ import annotations

import sys
from pathlib import Path

from xml_auditfile import Auditfile, AuditfileSource, AuditfileVersion, DiagnosticSeverity, ReadMode, ReadOptions, TextLanguage

USAGE = "Usage: python validate.py <file.xaf> [--en] [--unverified] [--force xaf/3.2]"


def main(args: list[str]) -> int:
    force_index = args.index("--force") if "--force" in args else -1
    files = [a for i, a in enumerate(args) if not a.startswith("--") and (force_index < 0 or i != force_index + 1)]
    if not files or force_index == len(args) - 1:
        print(USAGE, file=sys.stderr)
        return 2

    version = None
    if force_index >= 0:
        version = AuditfileVersion.find(args[force_index + 1])
        if version is None:
            known = ", ".join(v.key for v in AuditfileVersion.all())
            print(f"Unknown version '{args[force_index + 1]}'. Known: {known}.", file=sys.stderr)
            return 2

    options = ReadOptions(
        language=TextLanguage.ENGLISH if "--en" in args else TextLanguage.DUTCH,
        mode=ReadMode.UNVERIFIED if "--unverified" in args else ReadMode.VERIFIED,
        version=version,
    )

    # The reader never opens files itself: hand it a stream factory per part.
    source = AuditfileSource.from_factories(*((Path(p).name, lambda p=p: open(p, "rb")) for p in files))

    # Unverified skips the XSD but runs every other check.
    report = Auditfile.validate(source, options)

    for diagnostic in report.diagnostics:
        print(diagnostic)

    # The counts include diagnostics left out of a long list.
    errors = report.count(DiagnosticSeverity.ERROR) + report.count(DiagnosticSeverity.FATAL)
    print(f"{errors} errors, {report.count(DiagnosticSeverity.WARNING)} warnings")
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
