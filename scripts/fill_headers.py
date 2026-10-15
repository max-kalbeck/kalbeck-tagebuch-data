#!/usr/bin/env python
from copy import deepcopy
from pathlib import Path

from acdh_tei_pyutils.tei import TeiReader


TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"

HEADER_FILE = Path("data/meta/header_elements.xml")
WORK_DIR = Path("data/work")
EDITION_DIR = Path("data/editions")


def insert_before_revision_desc(tei_header, element):
    """Insert an element immediately before revisionDesc, if present."""
    revision_desc = tei_header.xpath(
        "./tei:revisionDesc",
        namespaces={"tei": TEI_NS},
    )

    index = (
        tei_header.index(revision_desc[0])
        if revision_desc
        else len(tei_header)
    )

    tei_header.insert(index, deepcopy(element))


def merge_hand_notes(target_profile_desc, source_profile_desc):
    """Insert handNotes if missing or empty; otherwise append missing handNotes."""
    source_hand_notes = source_profile_desc.find(
        f"{{{TEI_NS}}}handNotes"
    )

    if source_hand_notes is None:
        return

    target_hand_notes = target_profile_desc.find(
        f"{{{TEI_NS}}}handNotes"
    )

    if target_hand_notes is None or len(target_hand_notes) == 0:
        if target_hand_notes is not None:
            target_profile_desc.remove(target_hand_notes)

        target_profile_desc.append(deepcopy(source_hand_notes))
        return

    existing_ids = {
        note.get(f"{{{XML_NS}}}id")
        for note in target_hand_notes.findall(f"{{{TEI_NS}}}handNote")
    }

    for note in source_hand_notes.findall(f"{{{TEI_NS}}}handNote"):
        note_id = note.get(f"{{{XML_NS}}}id")

        if note_id not in existing_ids:
            target_hand_notes.append(deepcopy(note))
            existing_ids.add(note_id)


def merge_app_info(target_encoding_desc, source_encoding_desc):
    """Replace the complete appInfo element with the template version."""
    source_app_info = source_encoding_desc.find(
        f"{{{TEI_NS}}}appInfo"
    )

    if source_app_info is None:
        return

    target_app_info = target_encoding_desc.find(
        f"{{{TEI_NS}}}appInfo"
    )

    if target_app_info is not None:
        index = target_encoding_desc.index(target_app_info)
        target_encoding_desc.remove(target_app_info)
        target_encoding_desc.insert(index, deepcopy(source_app_info))
    else:
        target_encoding_desc.insert(0, deepcopy(source_app_info))


def merge_tags_decl(target_encoding_desc, source_encoding_desc):
    """Insert tagsDecl if missing or empty; otherwise append missing renditions."""
    source_tags_decl = source_encoding_desc.find(
        f"{{{TEI_NS}}}tagsDecl"
    )

    if source_tags_decl is None:
        return

    target_tags_decl = target_encoding_desc.find(
        f"{{{TEI_NS}}}tagsDecl"
    )

    if target_tags_decl is None or len(target_tags_decl) == 0:
        if target_tags_decl is not None:
            index = target_encoding_desc.index(target_tags_decl)
            target_encoding_desc.remove(target_tags_decl)
        else:
            index = len(target_encoding_desc)

        target_encoding_desc.insert(index, deepcopy(source_tags_decl))
        return

    existing_ids = {
        rendition.get(f"{{{XML_NS}}}id")
        for rendition in target_tags_decl.findall(
            f"{{{TEI_NS}}}rendition"
        )
    }

    for rendition in source_tags_decl.findall(
        f"{{{TEI_NS}}}rendition"
    ):
        rendition_id = rendition.get(f"{{{XML_NS}}}id")

        if rendition_id not in existing_ids:
            target_tags_decl.append(deepcopy(rendition))
            existing_ids.add(rendition_id)


def merge_profile_desc(tei_header, source_profile_desc):
    """Merge the template profileDesc into the document."""
    target_profile_descs = tei_header.xpath(
        "./tei:profileDesc",
        namespaces={"tei": TEI_NS},
    )

    if not target_profile_descs:
        insert_before_revision_desc(tei_header, source_profile_desc)
        return

    merge_hand_notes(target_profile_descs[0], source_profile_desc)


def merge_encoding_desc(tei_header, source_encoding_desc):
    """Merge the template encodingDesc into the document."""
    target_encoding_descs = tei_header.xpath(
        "./tei:encodingDesc",
        namespaces={"tei": TEI_NS},
    )

    if not target_encoding_descs:
        insert_before_revision_desc(tei_header, source_encoding_desc)
        return

    target_encoding_desc = target_encoding_descs[0]

    merge_app_info(target_encoding_desc, source_encoding_desc)
    merge_tags_decl(target_encoding_desc, source_encoding_desc)


def main():
    # Read template elements.
    header = TeiReader(str(HEADER_FILE))

    profile_desc = header.any_xpath("//tei:profileDesc")
    encoding_desc = header.any_xpath("//tei:encodingDesc")

    if not profile_desc:
        raise ValueError(f"No profileDesc found in {HEADER_FILE}")

    if not encoding_desc:
        raise ValueError(f"No encodingDesc found in {HEADER_FILE}")

    source_profile_desc = profile_desc[0]
    source_encoding_desc = encoding_desc[0]

    EDITION_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in sorted(WORK_DIR.glob("*.xml")):
        print(f"Processing {file_path}")
        output_path = EDITION_DIR / file_path.name

        tei = TeiReader(str(file_path))
        tree = tei.tree

        tei_headers = tree.xpath(
            "//tei:teiHeader",
            namespaces=tei.ns_tei,
        )

        if not tei_headers:
            print("  WARNING: no teiHeader found, skipping")
            continue

        tei_header = tei_headers[0]

        merge_encoding_desc(tei_header, source_encoding_desc)
        merge_profile_desc(tei_header, source_profile_desc)

        tree.write(
            str(output_path),
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
        )


if __name__ == "__main__":
    main()
