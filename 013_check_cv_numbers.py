"""Step 1.3b: do the CV numbers cited in the Step 1 document point to the right CV papers?

Inputs: 010_icd_mappings.json (Step 1 rows and their citations), 013_cv_articles.json (numbered
journal articles of Dominici_CV_updated_10132026.pdf), 024_fulltext_manifest.json (to say whether
the CV paper is one of the Step 2.4 papers, by DOI).

For every (Step 1 row, cited CV number) pair:
  author_ok   the surname in the Step 1 citation is the CV entry's first author
  year_ok     the Step 1 year (or one of "2020/2022") equals the CV year
  journal_ok  the journal named in the Step 1 citation (if any) matches the CV entry (None if none)
  topic       hand judgement in TOPIC below: does the CV paper fit the Step 1 row's outcome?
Also reported: CV numbers sharing a DOI with another CV entry (duplicates in the CV), and CV
entries whose DOI/PMID belong to a different article (ID_ISSUES, checked by hand).

Output: 013_cv_check.json
Run: .venv/bin/python 013_check_cv_numbers.py
"""
import json
import re

OUT = "013_cv_check.json"
JOURNALS = {"JAMA": "Journal of the American Medical Association", "Circulation": "Circulation",
            "AJRCCM": "American Journal of Respiratory and Critical Care Medicine",
            "EHP": "Environmental Health Perspectives", "AJE": "American Journal of Epidemiology",
            "Lancet Planetary Health": "Lancet Planetary Health", "Nature Communications": "Nature Communications",
            "BMJ": "BMJ", "Communications Medicine": "Communications Medicine"}

# Hand judgement of topic fit: (cv, row or None for all rows) -> (verdict, note)
# verdict: ok | partial | mismatch
TOPIC = {
    ("57", None): ("ok", "PM2.5 and CVD/respiratory admissions (MCAPS 2006)"),
    ("61", None): ("ok", "PM2.5 and congestive heart failure hospitalization"),
    ("78", None): ("ok", "Coarse PM and CVD/respiratory admissions"),
    ("89", None): ("ok", "PM2.5 chemical composition and CVD/respiratory admissions"),
    ("92", None): ("ok", "CO and emergency CVD admissions"),
    ("94", None): ("ok", "PM2.5 composition and CVD/respiratory admissions; first author is Peng (Bell is 2nd)"),
    ("125", None): ("ok", "Smoking bans and acute MI"),
    ("132", None): ("ok", "Heat-related respiratory hospitalizations"),
    ("134", None): ("ok", "Primary organic particles and emergency admissions"),
    ("136", None): ("ok", "PM2.5 constituents/sources and admissions"),
    ("148", None): ("ok", "PM2.5, diabetes and neurological disorders"),
    ("153", None): ("ok", "Cause-specific admissions and extreme heat"),
    ("171", None): ("ok", "Heat stroke admissions during heat waves"),
    ("172", None): ("ok", "PM2.5 and CVD/respiratory admissions by urbanicity"),
    ("173", None): ("ok", "Wildfire PM2.5 and admissions (Epidemiology, CV year 2016, vol. 28 2017)"),
    ("175", None): ("ok", "Wildfire PM2.5: who among the elderly is most vulnerable"),
    ("177", None): ("ok", "Snowstorms and cause-specific admissions"),
    ("181", None): ("ok", "Drought and admissions/mortality"),
    ("190", None): ("ok", "Diagnoses of heat-wave admissions"),
    ("202", None): ("ok", "PM2.5/ozone and ARDS"),
    ("212", None): ("ok", "PM2.5 and hospitalization with dementia"),
    ("220", None): ("ok", "PM2.5 and 432 cardiovascular diseases"),
    ("229", None): ("ok", "Construction/manufacturing sites and ARDS"),
    ("238", None): ("ok", "PM2.5 and admissions in chronic debilitating brain disorders"),
    ("240", None): ("ok", "Tropical cyclones and cause-specific hospitalizations"),
    ("242", None): ("ok", "Tropical cyclones and cardiorespiratory admissions"),
    ("244", None): ("ok", "Hurricane Sandy and ED visits by age and cause"),
    ("245", None): ("ok", "Temporal variation of PM2.5-hospitalization associations (CVD, respiratory)"),
    ("250", None): ("ok", "Volcanic SO2 and respiratory morbidity"),
    ("252", None): ("ok", "Volcanic plume and respiratory morbidity"),
    ("253", None): ("ok", "Temporal trends of PM2.5-hospitalization associations by subpopulation"),
    ("268", None): ("ok", "Bayesian multi-outcome analysis of cardiorespiratory hospitalizations"),
    ("270", None): ("ok", "Air pollution, temperature and psychiatric admissions"),
    ("271", None): ("ok", "Air pollutants and asthma hospitalization (Medicaid population)"),
    ("281", None): ("ok", "Tropical cyclones and CVD/respiratory hospitalization in Florida"),
    ("282", "S1-18"): ("partial", "AKI only; the row's 585/N18 (CKD) comes from Lee 2022 BMJ Medicine, not cited"),
    ("284", None): ("ok", "Low-level air pollution and MI admissions"),
    ("293", None): ("ok", "Temperature and alcohol/substance-related disorders"),
    ("303", None): ("ok", "PM2.5 constituents and non-respiratory infection admissions"),
    ("304", None): ("ok", "PM2.5 and natural-cause, CVD and respiratory morbidity (commercial + Medicare Advantage insured, not Medicare FFS)"),
    ("309", None): ("ok", "Same article as #303 (duplicate CV entry)"),
    ("311", None): ("ok", "Methods comparison with first ADRD hospitalization as outcome"),
    ("320", None): ("partial", "ADRD defines the cohort; outcomes are mortality and readmission"),
    ("323", "S1-37"): ("ok", "Second MI / ischemic stroke admissions"),
    ("323", "S1-01"): ("mismatch", "#323 is the second-events paper (MI, ischemic stroke only); the all-CVD (390-459) Danesh Yazdi 2025 paper is #332"),
    ("331", None): ("ok", "Oil/gas boom-bust and psychiatric hospitalizations"),
    ("339", None): ("partial", "Heat and PM2.5 and hospitalization among ADRD patients: ADRD defines the cohort, not the outcome"),
    ("341", None): ("ok", "Temperature and interpersonal / self-directed violence"),
}
# CV entries whose identifiers belong to another article (checked by hand)
ID_ISSUES = {"220": "DOI 10.1097/EDE.0000000000001456 and PMID 35104259 are those of #268 (Thomas 2022, "
                    "Epidemiology); the JASA 2020 article is doi:10.1080/01621459.2020.1722134"}


def topic(cv, row):
    return TOPIC.get((cv, row)) or TOPIC[(cv, None)]


def main():
    rows = [r for r in json.load(open("010_icd_mappings.json", encoding="utf-8"))["mappings"] if r["section"] == 1]
    arts = {str(a["n"]): a for a in json.load(open("013_cv_articles.json", encoding="utf-8"))["articles"]}
    manifest = json.load(open("024_fulltext_manifest.json", encoding="utf-8"))["papers"]
    by_doi = {p["doi"].lower(): p["slug"] for p in manifest if p["doi"]}
    dups = {}
    for n, a in arts.items():
        if a["doi"]:
            dups.setdefault(a["doi"], []).append(n)

    checks = []
    for r in rows:
        for pub in r["publications"]:
            cit = pub["citation"]
            surname = re.match(r"\s*([A-Z][\w'-]+)", cit).group(1)
            years = [int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", cit)]
            years += [int(cit[m.start() - 4:m.start()][:2] + y) for m in re.finditer(r"(?<=\d{4})/(\d{2,4})", cit)
                      for y in [m.group(1)[-2:]]]
            jname = next((full for short, full in JOURNALS.items() if re.search(r"\b%s\b" % re.escape(short), cit)), None)
            for cv in pub["cv_numbers"]:
                a = arts[cv]
                t_verdict, t_note = topic(cv, r["id"])
                slug = by_doi.get(a["doi"]) if a["doi"] else None
                if cv in ID_ISSUES:
                    slug = None
                checks.append({
                    "row": r["id"], "row_outcome": r["outcome"], "cv": cv, "step1_citation": cit,
                    "cv_entry": {"first_author": a["first_author"], "year": a["year"], "title": a["title"],
                                 "journal_etc": a["journal_etc"][:120], "doi": a["doi"], "page": a["page"]},
                    "author_ok": surname.lower() in a["authors"].split(",")[0].lower(),
                    "year_ok": a["year"] in years,
                    "journal_ok": (jname.lower() in a["text"].lower()) if jname else None,
                    "topic": t_verdict, "topic_note": t_note,
                    "cv_duplicates": [n for n in dups.get(a["doi"], []) if n != cv],
                    "cv_id_issue": ID_ISSUES.get(cv),
                    "step24_slug_by_doi": slug,
                })
    cited = {c["cv"] for c in checks}
    assert all((cv, None) in TOPIC or any(k[0] == cv for k in TOPIC) for cv in cited)
    for c in checks:
        flags = [k for k in ("author_ok", "year_ok") if not c[k]] + (["journal_ok"] if c["journal_ok"] is False else [])
        flags += ["topic_" + c["topic"]] if c["topic"] != "ok" else []
        flags += ["cv_duplicate"] if c["cv_duplicates"] else []
        flags += ["cv_id_issue"] if c["cv_id_issue"] else []
        c["flags"] = flags
        c["verdict"] = ("mismatch" if c["topic"] == "mismatch" or not c["author_ok"] and not c["year_ok"]
                        else "ok" if not flags else "ok_with_note")

    dup_all = {d: ns for d, ns in dups.items() if len(ns) > 1}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"sources": ["010_icd_mappings.json", "013_cv_articles.json", "024_fulltext_manifest.json"],
                   "checks": checks,
                   "cv_duplicate_dois_all": [{"doi": d, "cv_numbers": ns} for d, ns in sorted(dup_all.items(), key=lambda kv: int(kv[1][0]))]},
                  f, ensure_ascii=False, indent=1)
        f.write("\n")
    counts = {}
    for c in checks:
        counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1
    print("wrote %s: %d (row, CV) pairs, %d distinct CV numbers; %s; %d duplicated DOIs in the CV"
          % (OUT, len(checks), len(cited), counts, len(dup_all)))
    for c in checks:
        if c["verdict"] != "ok":
            print("  %s #%s %-8s %s | %s" % (c["row"], c["cv"], c["verdict"], ",".join(c["flags"]), c["topic_note"][:90]))


if __name__ == "__main__":
    main()
