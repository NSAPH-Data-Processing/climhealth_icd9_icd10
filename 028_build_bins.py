"""Step 2.8: can each reference outcome bin be populated from the Step 2 publications?

Inputs: 028_bins.json (hand map: bin -> Step 2.6 outcome entries, with scope), 026_icd_codes.json
(codes per paper and outcome), 027_crosswalk.json (paper labels).

Per source: the paper, outcome, scope, codes_status, the ICD-9/ICD-10 codes (for a 'broader'
source with a filter: only the codes inside the paper's group that start with, or a range that
covers, the filter prefixes), diagnosis position and evidence location.
Bin status (best source wins):
  explicit           an 'exact' source lists ICD codes
  explicit_partial   ICD codes only from 'broader' (filtered) or 'narrower' sources
  classification     only CCS/CCSR group numbers (no ICD codes) in the papers
  no_codes           sources exist but their codes are not available (unfetched supplement etc.)
  not_found          no source
parks_only is set when every coded source is the Parks 2021 CCS table (ICD-9 only, codes
assigned by CCS, not chosen for the bin by the authors).

Output: 028_bins_populated.json, 028_bins.csv
Run: .venv/bin/python 028_build_bins.py
"""
import csv
import json
import re

PARKS = "10_1038_s41467_021_21777_1"
RANGE = re.compile(r"^(\d{3})\S*\s*(?:–|-|to)\s*(\d{3})")


def covers(code, prefixes):
    """A code as written (e.g. '4940', '494.1', '490–493') falls under one of the ICD-9 prefixes."""
    c = code.replace(".", "").strip()
    if c.startswith(tuple(prefixes)):
        return True
    m = RANGE.match(code.strip())
    return bool(m) and any(int(m.group(1)) <= int(p[:3]) <= int(m.group(2)) for p in prefixes)
ORDER = ["explicit", "explicit_partial", "classification", "no_codes", "not_found"]


def main():
    spec = json.load(open("028_bins.json", encoding="utf-8"))
    papers = {p["slug"]: p for p in json.load(open("026_icd_codes.json", encoding="utf-8"))["papers"]}
    labels = dict(json.load(open("027_crosswalk.json", encoding="utf-8"))["labels"], **spec["labels"])
    out = []
    for b in spec["bins"]:
        sources = []
        for src in b["sources"]:
            slug, name, scope = src[:3]
            prefixes = src[3] if len(src) > 3 else None
            o = {x["outcome_name"]: x for x in papers[slug]["outcomes"]}[name]  # KeyError = map out of sync
            icd9, icd10 = list(o["icd9"]), list(o["icd10"])
            if prefixes:
                icd9 = [c for c in icd9 if covers(c, prefixes)]
                icd10 = []
                assert icd9, "filter %s matches no code in %s / %s" % (prefixes, slug, name)
            coded = bool(icd9 or icd10) and o["codes_status"] == "explicit_codes"
            level = ("explicit" if coded and scope == "exact" else "explicit_partial" if coded
                     else "classification" if o["codes_status"] == "classification_ref" else "no_codes")
            sources.append({"slug": slug, "paper": labels[slug], "outcome_name": name, "scope": scope,
                            "codes_status": o["codes_status"], "classification": o["classification"],
                            "filter": prefixes, "icd9": icd9, "icd10": icd10,
                            "diagnosis_position": o["diagnosis_position"], "evidence": o["evidence"],
                            "level": level})
        status = min((s["level"] for s in sources), key=ORDER.index) if sources else "not_found"
        coded = [s for s in sources if s["level"] in ("explicit", "explicit_partial")]
        out.append({"id": b["id"], "group": b["group"], "name": b["name"], "status": status,
                    "parks_only": bool(coded) and all(s["slug"] == PARKS for s in coded),
                    "n_papers": len({s["slug"] for s in sources}),
                    "icd10_available": any(s["icd10"] for s in coded),
                    "note": b.get("note"), "sources": sources})

    with open("028_bins_populated.json", "w", encoding="utf-8") as f:
        json.dump({"sources": ["028_bins.json", "026_icd_codes.json"], "bins": out}, f, ensure_ascii=False, indent=1)
        f.write("\n")

    def short(s):
        codes = s["icd9"] if len(s["icd9"]) <= 12 else s["icd9"][:10] + ["... (%d codes)" % len(s["icd9"])]
        txt = "%s [%s, %s]" % (s["paper"], s["scope"], s["codes_status"])
        if s["icd9"]:
            txt += " ICD-9 " + ", ".join(codes)
        if s["icd10"]:
            txt += " | ICD-10 " + ", ".join(s["icd10"][:12]) + (" ..." if len(s["icd10"]) > 12 else "")
        if s["classification"] and not (s["icd9"] or s["icd10"]):
            txt += " " + s["classification"]
        return txt

    with open("028_bins.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "group", "bin", "status", "parks_only", "icd10_available", "n_papers", "note", "sources"])
        for b in out:
            w.writerow([b["id"], b["group"], b["name"], b["status"], b["parks_only"], b["icd10_available"],
                        b["n_papers"], b["note"] or "", " || ".join(short(s) for s in b["sources"])])

    counts = {}
    for b in out:
        counts[b["status"]] = counts.get(b["status"], 0) + 1
    print("wrote 028_bins_populated.json and 028_bins.csv: %d bins; %s" % (len(out), counts))
    for b in out:
        print("  %-3s %-55s %-17s parks_only=%-5s icd10=%-5s papers=%d"
              % (b["id"], b["name"][:55], b["status"], b["parks_only"], b["icd10_available"], b["n_papers"]))


if __name__ == "__main__":
    main()
