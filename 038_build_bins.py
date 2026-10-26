"""Step 3.8: classify the Step 3.6 code sets (Danielle Braun) into outcome bins, with exposure attributes.

Inputs
  038_bins.json        hand map: bin -> code sets (paper slug, outcome name, scope, ICD-9 filter)
  038_exposures.json   hand classification of each paper's exposure
  036_icd_codes.json   code sets per paper and outcome
  037_crosswalk.json   paper labels (plus 'labels' in 038_bins.json)

Per source (code set in a bin): paper, outcome, scope, codes_status, ICD-9/ICD-10 codes (for a
'broader' source with a filter: only the codes inside the paper's group that start with, or a
range that covers, the filter prefixes; a Parks level-1 cause gets the codes of its level-3
groups), diagnosis position, evidence, and the paper's exposure.

Per bin
  status (best source wins)
    explicit           an 'exact' source lists ICD codes
    explicit_partial   ICD codes only from 'broader' (filtered) or 'narrower' sources
    classification     only CCS/CCSR group numbers (no ICD codes) in the papers
    no_codes           sources exist but their codes are not available (unfetched supplement etc.)
    no_evidence        a reference bin with no source
  exposure attributes  air_pollution, extreme_heat, extreme_weather, long_term, short_term,
                       other_exposure: the union over the papers of its 'exact' and 'narrower'
                       sources ('broader' sources studied a larger group, so they do not count)
  support              papers per exposure x term (e.g. air_pollution_long_term)
  parks_only           every coded source is the Parks 2021 CCS table (ICD-9, CCS-assigned)

Coverage check: every Step 2.6 code set with role 'outcome' and explicit codes (Parks CCS table
excluded) must be in at least one bin; code sets in no bin are listed in the output.

Output: 038_bins_populated.json, 038_bins.csv
Run: .venv/bin/python 038_build_bins.py
"""
import csv
import json
import re

BINS = "038_bins.json"
EXPOSURES = "038_exposures.json"
CODES = "036_icd_codes.json"
CROSSWALK = "037_crosswalk.json"
OUT_JSON = "038_bins_populated.json"
OUT_CSV = "038_bins.csv"

PARKS = "10_1038_s41467_021_21777_1"
RANGE = re.compile(r"^(\d{3})\S*\s*(?:–|-|to)\s*(\d{3})")
ORDER = ["explicit", "explicit_partial", "classification", "no_codes", "no_evidence"]
EXPOSURE_KEYS = ["air_pollution", "extreme_heat", "extreme_weather"]
TERM_KEYS = ["long_term", "short_term"]


def covers(code, prefixes):
    """A code as written (e.g. '4940', '494.1', '490–493') falls under one of the ICD-9 prefixes."""
    c = code.replace(".", "").strip()
    if c.startswith(tuple(prefixes)):
        return True
    m = RANGE.match(code.strip())
    return bool(m) and any(int(m.group(1)) <= int(p[:3]) <= int(m.group(2)) for p in prefixes)


def support_note(support):
    parts = []
    for e in EXPOSURE_KEYS:
        terms = ["%s %d" % (t.replace("_term", "-term"), len(support["%s_%s" % (e, t)]))
                 for t in TERM_KEYS if support["%s_%s" % (e, t)]]
        if terms:
            parts.append("%s (%s)" % (e.replace("_", " "), ", ".join(terms)))
    if support["other_exposure"]:
        parts.append("other exposure %d" % len(support["other_exposure"]))
    return "papers: " + "; ".join(parts) if parts else "no exposure study"


def main():
    spec = json.load(open(BINS, encoding="utf-8"))
    exposure = json.load(open(EXPOSURES, encoding="utf-8"))["papers"]
    papers = {p["slug"]: p for p in json.load(open(CODES, encoding="utf-8"))["papers"]}
    labels = dict(json.load(open(CROSSWALK, encoding="utf-8"))["labels"], **spec["labels"])
    level3 = {}
    for p in papers.values():
        for x in p["outcomes"]:
            m = re.match(r"AHRQ CCS level 3 group (\d+) ", x.get("classification") or "")
            if m:
                level3.setdefault(p["slug"], {})[m.group(1)] = x
    binned, out = set(), []
    for b in spec["bins"]:
        sources = []
        for src in b["sources"]:
            slug, name, scope = src[:3]
            prefixes = src[3] if len(src) > 3 else None
            o = {x["outcome_name"]: x for x in papers[slug]["outcomes"]}[name]  # KeyError = map out of sync
            binned.add((slug, name))
            icd9, icd10 = list(o["icd9"]), list(o["icd10"])
            for g in o.get("components_ccs_level3") or []:  # Parks level-1 cause: codes of its level-3 groups
                icd9 += level3[slug][g]["icd9"]
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
                            "exposure": exposure[slug], "level": level})
        status = min((s["level"] for s in sources), key=ORDER.index) if sources else "no_evidence"
        coded = [s for s in sources if s["level"] in ("explicit", "explicit_partial")]
        counted = [s for s in sources if s["scope"] in ("exact", "narrower")]
        support = {"%s_%s" % (e, t): sorted({s["paper"] for s in counted
                                             if s["exposure"][e] and s["exposure"][t]})
                   for e in EXPOSURE_KEYS for t in TERM_KEYS}
        support["other_exposure"] = sorted({s["paper"] for s in counted if s["exposure"]["other_exposure"]})
        attrs = {k: any(s["exposure"][k] for s in counted) for k in EXPOSURE_KEYS + TERM_KEYS}
        attrs["other_exposure"] = bool(support["other_exposure"])
        out.append(dict({"id": b["id"], "group": b["group"], "name": b["name"], "origin": b["origin"],
                         "status": status}, **attrs, **{
            "parks_only": bool(coded) and all(s["slug"] == PARKS for s in coded),
            "n_papers": len({s["slug"] for s in sources}),
            "icd10_available": any(s["icd10"] for s in coded),
            "support": support, "support_note": support_note(support) if sources else "no source in this set",
            "note": b.get("note"), "sources": sources}))

    unbinned = [{"slug": p["slug"], "outcome_name": o["outcome_name"], "codes_status": o["codes_status"]}
                for p in papers.values() if p["slug"] != PARKS
                for o in p["outcomes"] if o["role"] == "outcome" and (p["slug"], o["outcome_name"]) not in binned]
    missing_explicit = [u for u in unbinned if u["codes_status"] == "explicit_codes"]
    assert not missing_explicit, "explicit code sets in no bin: %s" % missing_explicit

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"sources": [BINS, EXPOSURES, CODES], "unbinned_code_sets": unbinned, "bins": out},
                  f, ensure_ascii=False, indent=1)
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

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "group", "bin", "origin", "status"] + EXPOSURE_KEYS + TERM_KEYS +
                   ["other_exposure", "support", "parks_only", "icd10_available", "n_papers", "note", "sources"])
        for b in out:
            w.writerow([b["id"], b["group"], b["name"], b["origin"], b["status"]] +
                       [b[k] for k in EXPOSURE_KEYS + TERM_KEYS] +
                       [b["other_exposure"], b["support_note"], b["parks_only"], b["icd10_available"],
                        b["n_papers"], b["note"] or "", " || ".join(short(s) for s in b["sources"])])

    counts = {}
    for b in out:
        counts[b["status"]] = counts.get(b["status"], 0) + 1
    print("wrote %s and %s: %d bins (%d added); %s; %d code sets not binned (none explicit)"
          % (OUT_JSON, OUT_CSV, len(out), sum(b["origin"] == "added" for b in out), counts, len(unbinned)))
    for b in out:
        print("  %-4s %-48s %-16s %s" % (b["id"], b["name"][:48], b["status"], b["support_note"]))


if __name__ == "__main__":
    main()
