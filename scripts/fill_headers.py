#!/usr/bin/env python
from copy import deepcopy
from pathlib import Path

from acdh_tei_pyutils.tei import TeiReader


HEADER_FILE = Path("data/meta/header_elements.xml")
EDITION_DIR = Path("data/editions")


def main():
    # Read template elements
    header = TeiReader(str(HEADER_FILE))

    profile_desc = header.any_xpath("//tei:profileDesc")
    encoding_desc = header.any_xpath("//tei:encodingDesc")

    if not profile_desc:
        raise ValueError(f"No profileDesc found in {HEADER_FILE}")

    if not encoding_desc:
        raise ValueError(f"No encodingDesc found in {HEADER_FILE}")

    profile_desc = profile_desc[0]
    encoding_desc = encoding_desc[0]

    for file_path in sorted(EDITION_DIR.glob("*.xml")):
        print(f"Processing {file_path}")

        tei = TeiReader(str(file_path))
        tree = tei.tree

        tei_header = tree.xpath(
            "//tei:teiHeader",
            namespaces=tei.ns_tei,
        )

        if not tei_header:
            print("  WARNING: no teiHeader found, skipping")
            continue

        tei_header = tei_header[0]

        # Remove existing elements first
        for element in tei_header.xpath(
            "./tei:encodingDesc | ./tei:profileDesc",
            namespaces=tei.ns_tei,
        ):
            tei_header.remove(element)

        # Find revisionDesc, if present
        revision_desc = tei_header.xpath(
            "./tei:revisionDesc",
            namespaces=tei.ns_tei,
        )

        # Insert the elements immediately before revisionDesc.
        # This guarantees:
        #   fileDesc
        #   encodingDesc
        #   profileDesc
        #   revisionDesc
        if revision_desc:
            index = tei_header.index(revision_desc[0])
        else:
            index = len(tei_header)

        tei_header.insert(index, deepcopy(encoding_desc))
        tei_header.insert(index + 1, deepcopy(profile_desc))

        # Write the modified document
        tree.write(
            str(file_path),
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
        )


if __name__ == "__main__":
    main()
