"""Step 6.2: replace CCW, CCS and CCSR markers with codes from the official lists. Printed codes are not changed.

Input: 061_outcomes.json, official_lists/. Sets with empty ranges stay out, and are listed with the reason.
CCSR categories match any of a code's categories, not only its default one.

Output: 062_outcomes.json, 062_left_out.json
Run: .venv/bin/python 062_resolve_markers.py
"""
import csv
import json
import re

IN = "061_outcomes.json"
OUT = "062_outcomes.json"
OUT_LEFT = "062_left_out.json"
CCW = json.load(open("official_lists/ccw_adrd_27cc_2022.json", encoding="utf-8"))
# the paper's non-respiratory infection list excludes these CCSR categories
CCSR_EXCLUDE = {"nonresp_infection_ccs": {"RSP002", "RSP003", "RSP004", "RSP005", "RSP006"}}
# the paper prints GEN001 (nephritis) for urinary tract infection, which is GEN004 in the CCSR table
CCSR_TYPOS = {"uti_ccs_ccsr": {"CCSR GEN001": "CCSR GEN004"}, "nonresp_infection_ccs": {"CCSR GEN001": "CCSR GEN004"}}
TYPO_NOTE = "typo corrected: the paper prints CCSR GEN001 for urinary tract infection, read as GEN004, since GEN001 is nephritis"


def load_tables():
    ccs, ccsr = {}, {}
    for r in csv.DictReader(open("official_lists/ccs_icd9_2015.csv", encoding="utf-8")):
        ccs.setdefault(int(r["ccs"]), []).append(r["icd9"])
    for r in csv.DictReader(open("official_lists/ccsr_icd10_v2023_1.csv", encoding="utf-8")):
        for c in r["ccsr_categories"].split():
            ccsr.setdefault(c, []).append(r["icd10"])
    return ccs, ccsr


def is_marker(c):
    return c == "CCW" or c.startswith("CCS ") or c.startswith("CCSR ")


def resolve(marker, version, ccs, ccsr):
    if marker == "CCW":
        return CCW[version], CCW["version"]
    if marker.startswith("CCSR "):
        a, _, b = marker[5:].partition("-")
        b = b or a
        prefix = a[:3]
        cats = ["%s%03d" % (prefix, n) for n in range(int(a[3:]), int(b[3:]) + 1)]
        return [c for x in cats for c in ccsr[x]], "HCUP CCSR v2023.1"
    a, _, b = marker[4:].partition("-")
    return [c for n in range(int(a), int(b or a) + 1) for c in ccs.get(n, [])], "HCUP CCS 2015"


def main():
    ccs, ccsr = load_tables()
    out, left = {}, []
    for key, s in json.load(open(IN, encoding="utf-8")).items():
        if not (s["icd9"] or s["icd10"]):
            left.append({"code_set": key, "long_name": s["long_name"], "paper_id": s["paper_id"],
                         "reason": "no ICD codes and no named definition in the paper"})
            continue
        for version in ("icd9", "icd10"):
            codes = s[version]
            s[version + "_source"] = "none" if not codes else "printed"
            if not any(is_marker(c) for c in codes):
                continue
            assert all(is_marker(c) for c in codes), (key, codes)
            found, label = [], None
            fixes = CCSR_TYPOS.get(key, {})
            if version == "icd10" and fixes:
                s["typo_fixes"] = [TYPO_NOTE]
            for m in codes:
                got, label = resolve(fixes.get(m, m), version, ccs, ccsr)
                assert got, (key, m)
                found += got
            if version == "icd10" and key in CCSR_EXCLUDE:
                excluded = {c for x in CCSR_EXCLUDE[key] for c in ccsr.get(x, [])}
                found = [c for c in found if c not in excluded]
            s[version + "_marker"] = codes
            s[version] = sorted(set(found))
            s[version + "_source"] = "official list: " + label
        out[key] = s
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(OUT_LEFT, "w", encoding="utf-8") as f:
        json.dump({"n": len(left), "items": left}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote %s: %d sets; %d left out" % (OUT, len(out), len(left)))
    for k, s in out.items():
        if "icd9_marker" in s or "icd10_marker" in s:
            print("  %-30s ICD-9 %5d  ICD-10 %5d  %s" % (k, len(s["icd9"]), len(s["icd10"]), s.get("icd9_marker")))
    print("  left out:", [i["code_set"] for i in left])


if __name__ == "__main__":
    main()
