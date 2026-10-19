#!/usr/bin/env python3
import glob
import re

import requests
from acdh_tei_pyutils.tei import TeiReader
from lxml import etree

PMB_BASE = "https://pmb.acdh.oeaw.ac.at/entity/"
PMB_TOKEN_RE = re.compile(r"^#pmb(\d+)$")
EDITIONS = "./data/editions/*.xml"
TEI = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def tei(tag):
    return f"{{{TEI}}}{tag}"


# nominal id -> canonical id, and canonical id -> PMB json; both filled on demand
CANONICAL = {}
ENTITIES = {}


def resolve(nominal_ids):
    # Canonical id for a group of aliases; requests only the first unknown one
    for n in nominal_ids:
        if n in CANONICAL:
            return CANONICAL[n]
    n = nominal_ids[0]
    try:
        r = requests.get(f"{PMB_BASE}{n}/?format=json", timeout=30)
        r.raise_for_status()
        data = r.json()
        canonical = str(data["id"])
        ENTITIES[canonical] = data  # keep the json, it is reused for the entity lists
    except Exception as e:
        print(f"Could not resolve {n}: {e}")
        canonical = n
    for m in nominal_ids:  # all aliases of this entity share the canonical id
        CANONICAL[m] = canonical
    CANONICAL[canonical] = canonical
    return canonical


def get_entity(canonical):
    # PMB json of a canonical id (cached; only requested if resolve() did not get it)
    if canonical not in ENTITIES:
        try:
            r = requests.get(f"{PMB_BASE}{canonical}/?format=json", timeout=30)
            r.raise_for_status()
            ENTITIES[canonical] = r.json()
        except Exception as e:
            print(f"Could not fetch {canonical}: {e}")
            ENTITIES[canonical] = {}
    return ENTITIES[canonical]


def canonicalize_value(value):
    #Return the attribute value with every uncanonical #pmbNNN token replaced
    out = []
    for token in value.split():
        m = PMB_TOKEN_RE.match(token)
        if m:
            token = f"#pmb{resolve([m.group(1)])}"
        out.append(token)
    return " ".join(out)


# --- entity lists -----------------------------------------------------------

# PMB / rs@type value -> (TEI list element, TEI item element)
TYPES = {
    "person": ("listPerson", "person"),
    "place": ("listPlace", "place"),
    "institution": ("listOrg", "org"),
    "org": ("listOrg", "org"),
    "event": ("listEvent", "event"),
    "work": ("listBibl", "bibl"),
}
# fallback if an element is not an <rs type="...">
TYPE_BY_ELEMENT = {
    "author": "person",
    "editor": "person",
    "persName": "person",
    "placeName": "place",
    "orgName": "institution",
}
LIST_ORDER = ["listPerson", "listPlace", "listOrg", "listEvent", "listBibl"]
# element holding the name inside each item
NAME_TAG = {"person": "persName", "place": "placeName", "org": "orgName", "event": "eventName", "bibl": "title"}


def entity_type(el, data):
    # rs@type first, then the element name, then whatever PMB says
    t = (el.get("type") or "").lower()
    if t not in TYPES:
        t = TYPE_BY_ELEMENT.get(etree.QName(el).localname, "")
    if t not in TYPES:
        t = str(data.get("type", "")).lower()
    return t if t in TYPES else None


def entity_label(data, fallback):
    # Best-effort label from the PMB json; adjust the keys to the actual payload
    last, first = data.get("last_name") or data.get("name"), data.get("first_name")
    if last and first and data.get("name") is None:
        return f"{last}, {first}"
    for key in ("label", "name", "title"):
        if isinstance(data.get(key), str) and data[key].strip():
            return data[key].strip()
    return fallback


def build_standoff(entities):
    # entities: {canonical id: (type, fallback label)} -> <standOff> element
    standoff = etree.Element(tei("standOff"))
    lists = {}
    for cid in sorted(entities, key=int):
        etype, fallback = entities[cid]
        list_tag, item_tag = TYPES[etype]
        if list_tag not in lists:
            lists[list_tag] = etree.Element(tei(list_tag))
        item = etree.SubElement(lists[list_tag], tei(item_tag))
        item.set(XML_ID, f"pmb{cid}")
        label = entity_label(get_entity(cid), fallback)
        etree.SubElement(item, tei(NAME_TAG[item_tag])).text = label
        idno = etree.SubElement(item, tei("idno"), type="pmb")
        idno.text = f"{PMB_BASE}{cid}/"
    for tag in LIST_ORDER:
        if tag in lists:
            standoff.append(lists[tag])
    etree.indent(standoff, space="   ", level=1)
    standoff.tail = "\n   "
    return standoff


def update_standoff(root, entities):
    # Replace any existing <standOff> by a freshly generated one; True if it changed
    old = root.findall(tei("standOff"))
    old_xml = b"".join(etree.tostring(o, with_tail=False) for o in old)
    for o in old:
        root.remove(o)
    if not entities:
        return bool(old)
    standoff = build_standoff(entities)
    root.find(tei("text")).addprevious(standoff)
    return etree.tostring(standoff, with_tail=False) != old_xml


def main():
    for f in sorted(glob.glob(EDITIONS)):
        doc = TeiReader(f)
        root = doc.tree.getroot()
        changed = 0
        entities = {}  # canonical id -> (type, fallback label)

        # 1. canonicalise the refs and collect the entities used in this file
        for el in doc.any_xpath("//*[@ref[contains(., '#pmb')]]"):
            if etree.QName(el).localname == "standOff":
                continue
            old = el.attrib["ref"]
            new = canonicalize_value(old)
            if new != " ".join(old.split()):
                print(f"{f}: {old} -> {new}")
                el.attrib["ref"] = new
                changed += 1
            for token in new.split():
                m = PMB_TOKEN_RE.match(token)
                if not m or m.group(1) in entities:
                    continue
                cid = m.group(1)
                etype = entity_type(el, get_entity(cid))
                if etype is None:
                    print(f"{f}: unknown entity type for #pmb{cid}, skipped")
                    continue
                entities[cid] = (etype, " ".join("".join(el.itertext()).split()))

        # 2. (re)generate the entity lists
        if update_standoff(root, entities):
            changed += 1

        if changed:
            doc.tree_to_file(f)
            print(f"{f}: updated ({len(entities)} entities)")

    n_alias = sum(1 for k, v in CANONICAL.items() if k != v)
    print(f"Done. {len(CANONICAL)} ids known, {n_alias} aliases resolved, "
          f"{len(ENTITIES)} entities fetched.")


if __name__ == "__main__":
    main()
