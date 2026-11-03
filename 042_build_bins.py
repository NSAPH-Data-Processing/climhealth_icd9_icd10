"""Step 4.2: apply Step 2.8 to the 15 shortlisted papers: classify their code sets into the same bins, with exposures.

Inputs
  038_bins.json        the bin list (Step 2.8 bins plus K6). Sources are not reused from it
  042_labels.json      hand map: outcome -> [bin id, scope]; paper labels
  026_labels.json      reused papers keep their outcome names, and their sources come from the two maps below
  028_bins.json, 038_bins.json   earlier hand maps, used only for the papers with 'reuse' in 042_labels.json
  042_exposures.json, 042_icd_codes.json

Writes 042_bins.json, then runs the build of 038_build_bins.py on it: same bin attributes, support and coverage check.

Output: 042_bins.json, 042_bins_populated.json, 042_bins.csv
Run: .venv/bin/python 042_build_bins.py
"""
import importlib.util
import json

LABELS = "042_labels.json"
EARLIER_BINS = ["028_bins.json", "038_bins.json"]
OUT = "042_bins.json"

_spec = importlib.util.spec_from_file_location("step38_bins", "038_build_bins.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
base.BINS, base.EXPOSURES, base.CODES = OUT, "042_exposures.json", "042_icd_codes.json"
base.OUT_JSON, base.OUT_CSV = "042_bins_populated.json", "042_bins.csv"


def main():
    lab = json.load(open(LABELS, encoding="utf-8"))
    bins = json.load(open("038_bins.json", encoding="utf-8"))["bins"]
    sources = {b["id"]: [] for b in bins}
    for slug, p in lab["papers"].items():
        for o in p.get("outcomes", []):
            for bin_id, scope in o.get("bins", []):
                sources[bin_id].append([slug, o["name"], scope])
    reused = {slug for slug, p in lab["papers"].items() if "reuse" in p}
    for fn in EARLIER_BINS:
        for b in json.load(open(fn, encoding="utf-8"))["bins"]:
            for src in b["sources"]:
                if src[0] in reused and src not in sources[b["id"]]:
                    sources[b["id"]].append(src)
    spec = {"description": "Step 4.2 bins: the Step 2.8 bins with sources from the 15 shortlisted papers only. Built by 042_build_bins.py.",
            "labels": lab["labels"],
            "bins": [{k: b[k] for k in ("id", "group", "name", "origin")} for b in bins]}
    for b in spec["bins"]:
        b["sources"] = sources[b["id"]]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
        f.write("\n")
    base.main()


if __name__ == "__main__":
    main()
