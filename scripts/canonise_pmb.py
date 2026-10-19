#!/usr/bin/env python3
import glob
import re
 
import requests
from acdh_tei_pyutils.tei import TeiReader
 
PMB_BASE = "https://pmb.acdh.oeaw.ac.at/entity/"
PMB_TOKEN_RE = re.compile(r"^#pmb(\d+)$")
EDITIONS = "./data/editions/*.xml"
 
# nominal id -> canonical id, filled on demand (one request per entity)
CANONICAL = {}
 
 
def resolve(nominal_ids):
    """Canonical id for a group of aliases; requests only the first unknown one."""
    for n in nominal_ids:
        if n in CANONICAL:
            return CANONICAL[n]
    n = nominal_ids[0]
    try:
        r = requests.get(f"{PMB_BASE}{n}/?format=json", timeout=30)
        r.raise_for_status()
        canonical = str(r.json()["id"])
    except Exception as e:
        print(f"Could not resolve {n}: {e}")
        canonical = n
    for m in nominal_ids:  # all aliases of this entity share the canonical id
        CANONICAL[m] = canonical
    CANONICAL[canonical] = canonical
    return canonical
 
 
def pmb_ids_in(value):
    """Yield the nominal ids of all #pmbNNN tokens in an attribute value."""
    for token in value.split():
        m = PMB_TOKEN_RE.match(token)
        if m:
            yield m.group(1)
 
 
def canonicalize_value(value):
    """Return the attribute value with every uncanonical #pmbNNN token replaced."""
    out = []
    for token in value.split():
        m = PMB_TOKEN_RE.match(token)
        if m:
            token = f"#pmb{resolve([m.group(1)])}"
        out.append(token)
    return " ".join(out)
 
 
def main():
    files = sorted(glob.glob(EDITIONS))
 
    # 1. replace uncanonical ids in the editions
    for f in files:
        doc = TeiReader(f)
        changed = 0
        for el in doc.any_xpath("//*[@ref[contains(., '#pmb')]]"):
            old = el.attrib["ref"]
            new = canonicalize_value(old)
            if new != " ".join(old.split()):
                print(f"{f}: {old} -> {new}")
                el.attrib["ref"] = new
                changed += 1
        if changed:
            doc.tree_to_file(f)
            print(f"{f}: {changed} ref(s) updated")
 
    n_changed = sum(1 for k, v in CANONICAL.items() if k != v)
    print(f"Done. {len(CANONICAL)} ids known, {n_changed} aliases resolved.")
 
 
if __name__ == "__main__":
    main()