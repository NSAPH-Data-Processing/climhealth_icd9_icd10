"""Step 4a: unified papers and outcomes from Steps 2 (Dominici) and 3 (Braun), each paper once.

Inputs
  024_fulltext_manifest.json, 034_fulltext_manifest.json   papers in scope (Medicare outcome papers)
  026_icd_codes.json, 036_icd_codes.json                   data source and outcomes per paper
  028_exposures.json, 038_exposures.json                   exposure attributes (full-text papers)
  027/037_crosswalk.json, 028/038_bins.json                paper labels
Papers in both sets are merged by slug (DOI). Where both steps have a record, Step 3 is used
for the manifest (newer run: e.g. Qin 2025 became open access) and for codes/exposure (same
labels, reused). Papers without full text get exposure attributes from their abstract (NO_FULLTEXT
below, hand-labeled) and their outcomes from the Step 2.3/3.3 outcome_names.

Outputs
  040_papers.json    one record per paper: ids, scholar sources, full-text status, data source,
                     exposure attributes, outcome counts
  040_outcomes.json  one record per (paper, outcome): codes_status, flags copied from the paper's
                     exposure, and whether a code set exists
Run: .venv/bin/python 040_build_papers.py
"""
import json
import re

EXPOSURE_KEYS = ["air_pollution", "extreme_heat", "extreme_weather", "long_term", "short_term"]
SCANS = {"10_1038_s41467_021_21777_1", "10_1136_bmj_l6258", "10_1001_jama_2014_15715",
         "10_1016_j_ypmed_2018_02_001"}  # outcome-wide scans (Parks 2021, Wei 2019, Bobb 2014, Hopp 2018)
EXTRA_LABELS = {
    "10_1111_j_1467_9876_2008_00640_x": "Peng 2009 JRSS-C",
    "10_1093_biostatistics_kxr002": "Chang 2011 Biostatistics",
    "10_1093_aje_kwr457": "Levy 2012 AJE",
    "scholar_RSwElNMAAAAJ_j7_hQOaDUrUC": "HEI 2016 report (causal methods, air quality regulations)",
}


def E(ap=False, heat=False, wx=False, lt=False, st=False, other=None, note=""):
    return {"air_pollution": ap, "extreme_heat": heat, "extreme_weather": wx, "long_term": lt,
            "short_term": st, "other_exposure": other, "note": note}


# Papers without full text: exposure read from the title and abstract (Step 2.2/3.2).
NO_FULLTEXT = {
    "10_1001_jama_295_10_1127": E(ap=True, st=True, note="daily PM2.5 time series (MCAPS)"),
    "10_1001_jama_299_18_2172": E(ap=True, st=True, note="daily coarse PM and PM2.5"),
    "10_1111_j_1467_9876_2008_00640_x": E(ap=True, st=True, note="distributed lag model, daily PM"),
    "10_1093_biostatistics_kxr002": E(ap=True, st=True, note="acute effects of coarse PM"),
    "10_1093_aje_kwr457": E(ap=True, st=True, note="PM2.5 constituents, multisite time series"),
    "10_1093_aje_kws267": E(other="smoking bans", lt=True, note="county smoking bans, AMI admissions"),
    "scholar_RSwElNMAAAAJ_j7_hQOaDUrUC": E(ap=True, lt=True, other="air quality policy (regulations)",
                                           note="long-term effects of air quality regulations"),
    "10_1016_j_chest_2019_03_017": E(ap=True, lt=True, note="long-term PM2.5 and ozone"),
    "10_1080_01621459_2020_1722134": E(ap=True, st=True, note="two-day average PM2.5, case-crossover"),
    "10_1016_s2542_5196_21_00168_6": E(ap=True, st=True, note="short-term PM2.5, time series"),
    "10_1016_j_envint_2023_107844": E(other="greenness", lt=True, note="residential greenness"),
    "10_1001_jamainternmed_2024_7719": E(heat=True, st=True, note="daily heat index, case-crossover"),
    "10_1093_aje_kwag087": E(other="none (geography and race)", note="regional and racial variation"),
}


def outcome_id(slug, o):
    """slug::outcome name; Parks CCS groups add their group number (two Parks groups share a printed
    name: CCS 58 is printed as 'Other disorders of stomach and duodenum', like CCS 141)."""
    m = re.match(r"AHRQ (?:multi-level )?CCS level (\d)(?: group|, cause) (\d+)", o.get("classification") or "")
    if m:
        return "%s::ccs-l%s-%s" % (slug, m.group(1), m.group(2))
    return "%s::%s" % (slug, o["outcome_name"])


def load(path):
    return json.load(open(path, encoding="utf-8"))


def main():
    man2 = {p["slug"]: p for p in load("024_fulltext_manifest.json")["papers"]}
    man3 = {p["slug"]: p for p in load("034_fulltext_manifest.json")["papers"]}
    codes = {p["slug"]: p for p in load("026_icd_codes.json")["papers"]}
    codes.update({p["slug"]: p for p in load("036_icd_codes.json")["papers"] if p["fulltext_status"] != "no_fulltext"})
    expo = dict(load("028_exposures.json")["papers"])
    expo.update({s: {k: v for k, v in e.items() if k != "reused_from_step28"}
                 for s, e in load("038_exposures.json")["papers"].items()})
    labels = dict(EXTRA_LABELS)
    for f in ("027_crosswalk.json", "037_crosswalk.json", "028_bins.json", "038_bins.json"):
        labels.update(load(f)["labels"])

    papers, outcomes = [], []
    for slug in sorted(set(man2) | set(man3), key=lambda s: ((man3.get(s) or man2[s])["year"] or 0, s)):
        m = man3.get(slug) or man2[slug]
        c = codes.get(slug) if m["status"] != "no_fulltext" else None
        if c is not None:
            e, e_src = expo[slug], "full text"
        else:
            e, e_src = NO_FULLTEXT[slug], "abstract"
        rec = {"slug": slug, "label": labels[slug], "doi": m["doi"], "pmid": m["pmid"], "pmcid": m["pmcid"],
               "year": m["year"], "title": m["title"],
               "in_dominici_scholar": slug in man2, "in_braun_scholar": slug in man3,
               "fulltext_status": m["status"], "fulltext_source": m["source"],
               "supplements_missing": m["supplements_missing"],
               "medpar_or_ffs": c["medpar_or_ffs"] if c else None,
               "data_source": c["data_source"] if c else "Medicare (from abstract, Step 2.3/3.3)",
               "data_source_evidence": c["data_source_evidence"] if c else None,
               "outcome_wide_scan": slug in SCANS,
               "exposure": dict({k: e[k] for k in EXPOSURE_KEYS}, other_exposure=e["other_exposure"],
                                note=e["note"], source=e_src)}
        if slug in man2 and slug in man3 and man2[slug]["status"] != man3[slug]["status"]:
            rec["fulltext_status_step24"] = man2[slug]["status"]
        flags = dict({k: e[k] for k in EXPOSURE_KEYS}, other_exposure=bool(e["other_exposure"]))
        if c is not None:
            entries = [{"id": outcome_id(slug, o), "outcome_name": o["outcome_name"], "step23_outcome_name": o["step23_outcome_name"],
                        "role": o["role"], "codes_status": o["codes_status"],
                        "classification": o["classification"],
                        "has_icd_codes": bool(o["icd9"] or o["icd10"] or o.get("components_ccs_level3")),
                        "evidence": o["evidence"]} for o in c["outcomes"]]
        else:
            entries = [{"id": "%s::%s" % (slug, n), "outcome_name": n, "step23_outcome_name": n, "role": "outcome",
                        "codes_status": "no_fulltext", "classification": None, "has_icd_codes": False,
                        "evidence": None} for n in m["outcome_names"]]
        for o in entries:
            outcomes.append(dict({"paper": slug, "paper_label": rec["label"]}, **o, flags=flags,
                                 outcome_wide_scan=rec["outcome_wide_scan"]))
        rec["n_outcomes"] = len(entries)
        rec["n_outcomes_with_codes"] = sum(o["has_icd_codes"] for o in entries)
        papers.append(rec)

    assert len({o["id"] for o in outcomes}) == len(outcomes), "duplicate outcome ids"
    meta = {"sources": ["024_fulltext_manifest.json", "034_fulltext_manifest.json", "026_icd_codes.json",
                        "036_icd_codes.json", "028_exposures.json", "038_exposures.json"]}
    json.dump(dict(meta, papers=papers), open("040_papers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(dict(meta, outcomes=outcomes), open("040_outcomes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    both = sum(p["in_dominici_scholar"] and p["in_braun_scholar"] for p in papers)
    print("wrote 040_papers.json: %d papers (%d Dominici only, %d Braun only, %d both); %d with full text"
          % (len(papers), sum(p["in_dominici_scholar"] and not p["in_braun_scholar"] for p in papers),
             sum(p["in_braun_scholar"] and not p["in_dominici_scholar"] for p in papers), both,
             sum(p["fulltext_status"] != "no_fulltext" for p in papers)))
    cnt = {}
    for o in outcomes:
        cnt[o["codes_status"]] = cnt.get(o["codes_status"], 0) + 1
    print("wrote 040_outcomes.json: %d outcomes; %s" % (len(outcomes), cnt))
    for k in EXPOSURE_KEYS + ["other_exposure"]:
        print("  papers with %s: %d" % (k, sum(bool(p["exposure"][k]) for p in papers)))


if __name__ == "__main__":
    main()
