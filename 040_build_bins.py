"""Step 4d: the final outcome bins, from the Step 2.8 and 3.8 bins, keeping only well-represented bins.

Inputs: 028_bins.json, 038_bins.json (hand maps: bin -> [slug, outcome name, scope, ICD-9 filter]),
040_outcomes.json, 040_codesets.json.

1. Union: the two maps are merged by bin id; sources are deduplicated by outcome id. Each source
   carries its code sets: the outcome's own (author_defined / ccs_table) and, if any, its
   ccs_resolved set.
2. Restructure (hand decisions in RESTRUCTURE, MOVES, RENAME, DROP below): merge, split, rename
   or drop bins so that every kept bin is well represented.
3. Representation rule (checked): a kept bin has at least one 'exact' source with a code set that
   has ICD codes, not counting Parks groups that Parks did not analyze on their own
   (parks_analyzed false), and at least one supporting paper with an air pollution, extreme heat
   or extreme weather exposure.
4. Coverage rule (checked): every author-defined code set with role 'outcome' is in a kept bin.

Flags per bin
  air_pollution, extreme_heat, extreme_weather, long_term, short_term, other_exposure
      union over the papers of its 'exact' and 'narrower' sources; 'support' lists the papers
      per exposure x term (e.g. air_pollution_long_term)
  author_defined     >= 1 exact author-defined code set without a 'suspect' note (otherwise the
                     codes come from CCS only, or only from a code set with a likely typo)
  ccs_only           no author-defined code set at all (exact or narrower)
  icd10_available    >= 1 exact or narrower code set with ICD-10 codes
  outcome_wide_only  every supporting paper is an outcome-wide scan (Parks, Wei 2019, Bobb, Hopp)
  in_reference_list  the bin comes from the CLAUDE.md reference list
  n_papers, n_papers_dominici, n_papers_braun, n_exact_codesets, n_author_defined_exact,
  n_suspect_codesets

Outputs: 040_bins.json, 040_bins.csv, and the same bins split by code set type:
  040_bins_author_defined.json   populated only with author-defined code sets
  040_bins_derived.json          populated only with derived code sets (ccs_table, ccs_resolved)
  In the split files, a bin is 'represented' (an exact code set of that type, not an unanalyzed
  Parks group), 'partially_represented' (only narrower/broader sets) or empty; flags are
  recomputed from that type's sources.
Run: .venv/bin/python 040_build_bins.py
"""
import csv
import json
import re

EXPOSURE_KEYS = ["air_pollution", "extreme_heat", "extreme_weather"]
TERM_KEYS = ["long_term", "short_term"]
PARKS = "10_1038_s41467_021_21777_1"

# Bins removed, with the reason.
DROP = {
    "W1": "not an outcome (outcome-wide scans); the scans' groups are in the disease bins",
    "C9": "only inside a broader Parks group (CCS 87, not analyzed on its own); no study of the outcome",
    "I4": "only inside the pneumonia CCS group (136.3 in CCS 122); its codes stay in R4",
    "C14": "no code set (codes in an unfetched supplement) and no environmental exposure study",
}
# Bins merged into another bin: source bin -> target bin (sources move, scope kept unless MOVES says otherwise).
RESTRUCTURE = {"R3": "R2", "C5": "C4", "C7": "N4"}
# Individual sources moved or re-scoped: (from bin, slug, outcome name) -> (to bin, scope).
MOVES = {
    ("C7", "10_1161_circulationaha_120_050252", "ischemic stroke"): ("C15", "exact"),
    ("C7", "10_1016_j_scitotenv_2022_156855", "ischemic stroke"): ("C15", "exact"),
    ("C7", "10_1097_ede_0000000000001265", "ischemic stroke"): ("C15", "exact"),
    ("C7", "10_1016_j_envint_2025_109617", "second admission with ischemic stroke"): ("C15", "exact"),
    ("C7", "10_1016_j_envres_2025_122779", "ischemic stroke"): ("C15", "exact"),
    ("C7", PARKS, "Stroke"): ("N4", "narrower"),
    ("R3", PARKS, "COPD"): ("R2", "exact"),
    ("R3", "10_1136_bmj_l6258", "chronic obstructive pulmonary disease and bronchiectasis (CCS 127)"): ("R2", "exact"),
    ("R3", "10_1186_1476_069x_12_68", "chronic obstructive pulmonary disease"): ("R2", "exact"),
    ("C5", PARKS, "Cardiac arrest and ventricular fibrillation"): ("C4", "narrower"),
    ("C6", PARKS, "Hypertension with complications and secondary hypertension"): ("C6", "exact"),
    ("C6", "10_1136_bmj_2023_076939", "heart failure"): (None, None),  # a heart failure set, not hypertensive disease
    ("X2", "10_1016_j_scitotenv_2020_142524", "hip fractures"): ("X2", "exact"),
    ("X2", PARKS, "Fracture of neck of femur hip"): ("X2", "exact"),
    ("X2", "10_1016_s2542_5196_17_30136_5", "osteoporosis-related bone fracture admissions"): ("X2", "broader"),
}
NEW_BINS = {"C15": {"group": "Cardiovascular and blood-vessel conditions", "name": "Ischemic stroke",
                    "origin": "added", "note": "Split from the reference bin 'Stroke, including ischemic and "
                    "hemorrhagic stroke': hemorrhagic stroke has no code set (only multi-level CCS 7.3.1.1 in "
                    "Thomas 2022); all stroke is in N4."}}
RENAME = {
    "R2": ("COPD and bronchiectasis", "Merged with the reference bin 'Bronchiectasis' (ICD-9 494 is in CCS 127 "
           "and in the COPD definitions 490-492, 494-496)."),
    "C4": ("Arrhythmias and cardiac arrest", "Merged with the reference bin 'Cardiac arrest' (ICD-9 427.4-427.5 "
           "are inside the arrhythmia range 426-427)."),
    "N4": ("Cerebrovascular disease, including stroke", "Includes all stroke (430-438 / I60-I69); ischemic "
           "stroke also has its own bin C15."),
    "C6": ("Hypertension with complications (hypertensive heart and kidney disease)",
           "Renamed from 'Hypertensive heart disease': the only code set is CCS 99 (402-405)."),
    "X2": ("Hip fracture", "Renamed from 'Fractures': the code sets are hip fracture (820, CCS 226); "
           "osteoporosis-related fractures (Prada 2017) have no fetched codes."),
    "I5": ("Intestinal obstruction", None),
}
GROUP = {"I5": "Digestive conditions", "O1": "Other conditions"}


def covers(code, prefixes):
    c = code.replace(".", "").strip()
    if c.startswith(tuple(prefixes)):
        return True
    m = re.match(r"^(\d{3})\S*\s*(?:–|-|to)\s*(\d{3})", code.strip())
    return bool(m) and any(int(m.group(1)) <= int(p[:3]) <= int(m.group(2)) for p in prefixes)


def split(bins, kind):
    """The same bins, each populated only with code sets of one kind:
    'author_defined' (source_type author_defined) or 'derived' (ccs_table, ccs_resolved).
    Sources without a code set of that kind are left out; flags are recomputed from what remains."""
    out = []
    for b in bins:
        sources = []
        for s in b["sources"]:
            css = [c for c in s["codesets"] if (c["source_type"] == "author_defined") == (kind == "author_defined")
                   and (c["icd9"] or c["icd10"])]
            if css:
                sources.append(dict(s, codesets=css))
        counted = [s for s in sources if s["scope"] in ("exact", "narrower")]
        exact = [c for s in sources if s["scope"] == "exact" for c in s["codesets"] if c["parks_analyzed"] is not False]
        support = {"%s_%s" % (e, t): sorted({s["paper_label"] for s in counted if s["exposure"][e] and s["exposure"][t]})
                   for e in EXPOSURE_KEYS for t in TERM_KEYS}
        support["other_exposure"] = sorted({s["paper_label"] for s in counted if s["exposure"]["other_exposure"]})
        rec = {k: b[k] for k in ("id", "group", "name", "former_name", "in_reference_list", "merged_from", "note")}
        rec.update({k: any(s["exposure"][k] for s in counted) for k in EXPOSURE_KEYS + TERM_KEYS})
        rec["other_exposure"] = bool(support["other_exposure"])
        rec.update({
            "represented": bool(exact),
            "partially_represented": not exact and bool(sources),
            "icd10_available": any(c["icd10"] for s in counted for c in s["codesets"]),
            "outcome_wide_only": bool(counted) and all(s["outcome_wide_scan"] for s in counted),
            "n_papers": len({s["paper"] for s in sources}), "n_exact_codesets": len(exact),
            "n_codesets": sum(len(s["codesets"]) for s in sources),
            "n_suspect_codesets": sum(bool(c["suspect"]) for s in sources for c in s["codesets"]),
            "support": support, "sources": sources})
        out.append(rec)
    return out


def main():
    outcomes = json.load(open("040_outcomes.json", encoding="utf-8"))["outcomes"]
    by_name = {}
    for o in outcomes:
        by_name.setdefault((o["paper"], o["outcome_name"]), []).append(o)
    sets = json.load(open("040_codesets.json", encoding="utf-8"))["codesets"]
    sets_by_outcome = {}
    for s in sets:
        sets_by_outcome.setdefault(s["outcome_id"], []).append(s)
    papers = {p["slug"]: p for p in json.load(open("040_papers.json", encoding="utf-8"))["papers"]}

    # 1. union of the Step 2.8 and 3.8 maps
    bins, order = {}, []
    for f in ("028_bins.json", "038_bins.json"):
        for b in json.load(open(f, encoding="utf-8"))["bins"]:
            if b["id"] not in bins:
                bins[b["id"]] = {k: b.get(k) for k in ("id", "group", "name", "origin", "note")}
                bins[b["id"]]["sources"], bins[b["id"]]["merged_from"] = [], []
                order.append(b["id"])
            for src in b["sources"]:
                bins[b["id"]]["sources"].append((src[0], src[1], src[2], src[3] if len(src) > 3 else None, b["id"]))
    for i, nb in NEW_BINS.items():
        bins[i] = dict(nb, id=i, sources=[], merged_from=[])
        order.insert(order.index("C7") + 1, i)

    # 2. restructure
    moved = []
    for bid in list(order):
        keep = []
        for slug, name, scope, filt, origin in bins[bid]["sources"]:
            key = (bid, slug, name)
            if key in MOVES:
                to, sc = MOVES[key]
                if to is not None:
                    moved.append((to, (slug, name, sc, None if sc == "exact" else filt, bid)))
            elif bid in RESTRUCTURE:
                moved.append((RESTRUCTURE[bid], (slug, name, scope, filt, bid)))
            else:
                keep.append((slug, name, scope, filt, origin))
        bins[bid]["sources"] = keep
    for to, src in moved:
        bins[to]["sources"].append(src)
    for src_bin, to in RESTRUCTURE.items():
        bins[to]["merged_from"].append("%s (%s)" % (src_bin, bins[src_bin]["name"]))
    removed = [{"id": b, "name": bins[b]["name"], "reason": DROP[b]} for b in DROP]
    removed += [{"id": b, "name": bins[b]["name"], "reason": "merged into %s" % t} for b, t in RESTRUCTURE.items()]
    kept_ids = [b for b in order if b not in DROP and b not in RESTRUCTURE]
    for b, (name, note) in RENAME.items():
        bins[b]["former_name"], bins[b]["name"] = bins[b]["name"], name
        if note:
            bins[b]["note"] = note
    for b, g in GROUP.items():
        bins[b]["group"] = g

    # 3. resolve sources, flags, representation
    out, problems = [], []
    for bid in kept_ids:
        b = bins[bid]
        seen, sources = set(), []
        for slug, name, scope, filt, origin in b["sources"]:
            cands = by_name[(slug, name)]
            assert len(cands) == 1, (slug, name)
            o = cands[0]
            if (o["id"], scope) in seen:
                continue
            seen.add((o["id"], scope))
            css = []
            for s in sets_by_outcome.get(o["id"], []):
                icd9 = [c for c in s["icd9"] if covers(c, filt)] if filt else s["icd9"]
                css.append({"codeset_id": s["id"], "source_type": s["source_type"], "ccs": s["ccs"],
                            "ccs_groups": s["ccs_groups"], "parks_analyzed": s["parks_analyzed"],
                            "icd9": icd9, "icd10": [] if filt else s["icd10"], "suspect": s["suspect"]})
            sources.append({"outcome_id": o["id"], "paper": o["paper"], "paper_label": o["paper_label"],
                            "outcome_name": o["outcome_name"], "scope": scope, "filter": filt,
                            "codes_status": o["codes_status"], "outcome_wide_scan": o["outcome_wide_scan"],
                            "exposure": papers[o["paper"]]["exposure"], "codesets": css})
        counted = [s for s in sources if s["scope"] in ("exact", "narrower")]
        exact_sets = [c for s in sources if s["scope"] == "exact" for c in s["codesets"]
                      if (c["icd9"] or c["icd10"]) and c["parks_analyzed"] is not False]
        support = {"%s_%s" % (e, t): sorted({s["paper_label"] for s in counted
                                             if s["exposure"][e] and s["exposure"][t]})
                   for e in EXPOSURE_KEYS for t in TERM_KEYS}
        support["other_exposure"] = sorted({s["paper_label"] for s in counted if s["exposure"]["other_exposure"]})
        rec = {"id": bid, "group": b["group"], "name": b["name"], "former_name": b.get("former_name"),
               "in_reference_list": b["origin"] == "reference", "merged_from": b["merged_from"], "note": b["note"]}
        rec.update({k: any(s["exposure"][k] for s in counted) for k in EXPOSURE_KEYS + TERM_KEYS})
        rec["other_exposure"] = bool(support["other_exposure"])
        exposed = [s for s in counted if any(s["exposure"][k] for k in EXPOSURE_KEYS)]
        rec.update({
            "author_defined": any(c["source_type"] == "author_defined" and not c["suspect"] for c in exact_sets),
            "ccs_only": not any(c["source_type"] == "author_defined" for s in counted for c in s["codesets"]),
            "icd10_available": any(c["icd10"] for s in counted for c in s["codesets"]),
            "outcome_wide_only": bool(exposed) and all(s["outcome_wide_scan"] for s in exposed),
            "n_papers": len({s["paper"] for s in sources}),
            "n_papers_dominici": len({s["paper"] for s in sources if papers[s["paper"]]["in_dominici_scholar"]}),
            "n_papers_braun": len({s["paper"] for s in sources if papers[s["paper"]]["in_braun_scholar"]}),
            "n_exact_codesets": len(exact_sets),
            "n_author_defined_exact": sum(c["source_type"] == "author_defined" for c in exact_sets),
            "n_suspect_codesets": sum(bool(c["suspect"]) for s in sources for c in s["codesets"]),
            "support": support, "sources": sources})
        if not exact_sets:
            problems.append("%s %s: no exact code set" % (bid, b["name"]))
        if not exposed:
            problems.append("%s %s: no air pollution / heat / weather paper" % (bid, b["name"]))
        out.append(rec)

    # 4. coverage of author-defined code sets
    in_bins = {s["outcome_id"] for b in out for s in b["sources"]}
    uncovered = [s["id"] for s in sets if s["source_type"] == "author_defined" and s["role"] == "outcome"
                 and s["outcome_id"] not in in_bins]
    if uncovered:
        problems.append("author-defined code sets in no bin: %s" % uncovered)
    if problems:
        raise SystemExit("\n".join(problems))

    with open("040_bins.json", "w", encoding="utf-8") as f:
        json.dump({"sources": ["028_bins.json", "038_bins.json", "040_outcomes.json", "040_codesets.json"],
                   "removed_bins": removed, "bins": out}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for kind in ("author_defined", "derived"):
        sb = split(out, kind)
        with open("040_bins_%s.json" % kind, "w", encoding="utf-8") as f:
            json.dump({"sources": ["040_bins.json"], "kind": kind,
                       "codeset_types": ["author_defined"] if kind == "author_defined" else ["ccs_table", "ccs_resolved"],
                       "bins": sb}, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("wrote 040_bins_%s.json: %d bins, %d represented, %d partially, %d empty"
              % (kind, len(sb), sum(b["represented"] for b in sb), sum(b["partially_represented"] for b in sb),
                 sum(not b["sources"] for b in sb)))

    with open("040_bins.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        flags = EXPOSURE_KEYS + TERM_KEYS + ["other_exposure", "author_defined", "ccs_only", "icd10_available",
                                             "outcome_wide_only", "in_reference_list"]
        w.writerow(["id", "group", "bin"] + flags + ["n_papers", "n_papers_dominici", "n_papers_braun",
                                                    "n_exact_codesets", "n_author_defined_exact", "support", "papers"])
        for b in out:
            sup = "; ".join("%s: %s" % (k, ", ".join(v)) for k, v in b["support"].items() if v)
            pap = "; ".join(sorted({"%s [%s]" % (s["paper_label"], s["scope"]) for s in b["sources"]}))
            w.writerow([b["id"], b["group"], b["name"]] + [b[k] for k in flags] +
                       [b["n_papers"], b["n_papers_dominici"], b["n_papers_braun"], b["n_exact_codesets"],
                        b["n_author_defined_exact"], sup, pap])
    print("wrote 040_bins.json and 040_bins.csv: %d bins kept, %d removed (dropped or merged)" % (len(out), len(removed)))
    print("  author_defined %d, ccs_only %d, icd10_available %d, outcome_wide_only %d, in reference list %d"
          % tuple(sum(b[k] for b in out) for k in ("author_defined", "ccs_only", "icd10_available",
                                                    "outcome_wide_only", "in_reference_list")))
    for b in out:
        print("  %-4s %-58s AP=%d heat=%d wx=%d LT=%d ST=%d auth=%d icd10=%d scan_only=%d papers=%d"
              % (b["id"], b["name"][:58], b["air_pollution"], b["extreme_heat"], b["extreme_weather"],
                 b["long_term"], b["short_term"], b["author_defined"], b["icd10_available"],
                 b["outcome_wide_only"], b["n_papers"]))


if __name__ == "__main__":
    main()
