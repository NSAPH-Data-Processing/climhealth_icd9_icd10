"""Step 4.2: Step 2.6 records (data source, outcomes, ICD codes) for the 15 shortlisted papers, using the downloaded files.

Inputs
  041_status.json              the shortlisted papers
  026_icd_codes.json, 036_icd_codes.json   paper ids and Step 2.3 outcome names
  042_labels.json              hand labels; 'reuse' takes a paper's outcomes from 026_labels.json
  papers/<slug>/text/*.txt     extracted text (042_extract_text.py)

Uses the quote search and record format of 036_build_icd_codes.py: a quote that is not found stops the build.
Adds group_based to each outcome: true for outcome-wide group entries, whose ICD codes are handled separately.

Output: 042_icd_codes.json
Run: .venv/bin/python 042_build_icd_codes.py
"""
import importlib.util
import json

STATUS = "041_status.json"
EARLIER = ["026_icd_codes.json", "036_icd_codes.json"]
LABELS = "042_labels.json"
OUT = "042_icd_codes.json"

_spec = importlib.util.spec_from_file_location("step36_build", "036_build_icd_codes.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def main():
    earlier = {}
    for fn in EARLIER:  # the later step wins, for the outcome names of papers on both lists
        earlier.update({p["slug"]: p for p in json.load(open(fn, encoding="utf-8"))["papers"]})
    labels = json.load(open(LABELS, encoding="utf-8"))["papers"]
    out = []
    for item in json.load(open(STATUS, encoding="utf-8"))["items"]:
        slug = item["folder"].rstrip("/").split("/")[-1]
        p, lab = earlier[slug], labels[slug]
        reused = json.load(open(lab["reuse"], encoding="utf-8"))["papers"][slug] if "reuse" in lab else None
        full = dict(reused, **lab) if reused else lab
        assert full["medpar_ffs"] in ("stated", "implied"), slug
        names = p["step23_outcome_names"]
        outs = []
        for o in full["outcomes"]:
            assert o["step23"] in names + [None], "%s: %r" % (slug, o["step23"])
            outs.append(dict(base.outcome_record(slug, o), group_based=bool(o.get("group_based") or lab.get("group_based"))))
        out.append({"unified_rank": item["unified_rank"], "slug": slug, "doi": p["doi"], "pmid": p["pmid"], "pmcid": p["pmcid"],
                    "year": p["year"], "title": p["title"], "step23_outcome_names": names,
                    "medpar_or_ffs": full["medpar_ffs"], "data_source": full["source"],
                    "data_source_evidence": base.locate(slug, full["ev"]), "outcome_wide": full.get("outcome_wide"),
                    "reused_labels": lab.get("reuse"), "note": lab.get("note"), "outcomes": outs})
    assert not set(labels) - {r["slug"] for r in out}
    if base._missing:
        raise SystemExit("\n".join(base._missing))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"sources": [STATUS, LABELS], "papers": out}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    entries = [o for r in out for o in r["outcomes"]]
    print("wrote %s: %d papers, %d outcome entries, %d group-based" % (OUT, len(out), len(entries), sum(o["group_based"] for o in entries)))
    print("  codes_status:", {s: sum(o["codes_status"] == s for o in entries) for s in sorted({o["codes_status"] for o in entries})})
    print("  role:", {s: sum(o["role"] == s for o in entries) for s in sorted({o["role"] for o in entries})})


if __name__ == "__main__":
    main()
