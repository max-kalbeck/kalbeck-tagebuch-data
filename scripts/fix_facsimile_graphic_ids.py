#!/usr/bin/env python
"""Add sequential xml:id values to facsimile graphics.

This script assigns ids of the form ``facs-01``, ``facs-02``, ... to every
``tei:graphic`` element inside ``tei:facsimile`` blocks.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from acdh_tei_pyutils.tei import TeiReader


XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
DEFAULT_INPUT_DIR = Path("data/editions")


def iter_input_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.xml")))
        else:
            files.append(path)
    return files


def fix_file(file_path: Path) -> bool:
    tei = TeiReader(str(file_path))
    tree = tei.tree
    changed = False

    facsimiles = tree.xpath("//tei:facsimile", namespaces=tei.ns_tei)
    for facsimile in facsimiles:
        graphics = facsimile.xpath("./tei:graphic", namespaces=tei.ns_tei)
        for index, graphic in enumerate(graphics, start=1):
            target_id = f"facs-{index:02d}"
            if graphic.get(XML_ID) != target_id:
                graphic.set(XML_ID, target_id)
                changed = True

    if changed:
        tree.write(
            str(file_path),
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
        )

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assign sequential xml:id values to facsimile graphics.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="XML files or directories to process. Defaults to data/editions.",
    )
    args = parser.parse_args()

    input_paths = args.paths or [DEFAULT_INPUT_DIR]
    files = iter_input_files(input_paths)

    if not files:
        raise SystemExit("No XML files found.")

    for file_path in files:
        if fix_file(file_path):
            print(f"Updated {file_path}")
        else:
            print(f"No changes needed for {file_path}")


if __name__ == "__main__":
    main()
