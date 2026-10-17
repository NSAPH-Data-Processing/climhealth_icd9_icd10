"""Step 1.2: build 012_publications.json, a super simple list of the publications cited in
Section 1 of the PDF, derived from 010_icd_mappings.json. One entry per CV number.

Stdlib only.  Run:  python3 012_extract_publications.py
"""
import json
import re

d = json.load(open("010_icd_mappings.json", encoding="utf-8"))
pubs = {}
for m in d["mappings"]:
    for p in m.get("publications", []):
        # citation text before the "(#..." part, minus trailing comma
        text = re.sub(r"\s*\(#.*$", "", p["citation"]).rstrip(",").strip()
        for cv in p["cv_numbers"]:
            e = pubs.setdefault(int(cv), {"cv": int(cv), "citation": text, "mappings": []})
            if len(text) > len(e["citation"]):  # keep the fullest version
                e["citation"] = text
            if m["id"] not in e["mappings"]:
                e["mappings"].append(m["id"])
out = sorted(pubs.values(), key=lambda e: e["cv"])
with open("012_publications.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"wrote 012_publications.json: {len(out)} publications")
