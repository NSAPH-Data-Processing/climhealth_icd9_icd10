"""Step 3.5: build the prioritized download shortlist from the Step 3.4 gaps (Danielle Braun).

Input: 034_fulltext_manifest.json (gaps = status no_fulltext, or supplements_missing non-empty).
The ranking is a hand judgement recorded in PRIORITY below (see 035_shortlist.md; same criteria as Step 2.5);
every gap must appear in PRIORITY, so a new gap after a re-run of Step 3.4 fails loudly.

Output: 035_shortlist.json
Run: .venv/bin/python 035_build_shortlist.py
"""
import json

IN = "034_fulltext_manifest.json"
OUT = "035_shortlist.json"
SHORTLIST_SIZE = 5

# slug -> (rank, step1_cv, document to get, why it matters)
# step1_cv: CV numbers of the Step 1 PDF citation this paper corresponds to (author + year + topic match).
PRIORITY = {
    "10_1001_jamainternmed_2024_7719": (1, [], "Article PDF, plus Supplement 1 (eMethods: ADRD codes)",
        "Heat and first hospitalization with ADRD (Medicare FFS 2000-2018): the ADRD code list (ICD-9 and "
        "ICD-10 years) fills the dementia bin for a heat exposure. Has a PMC page (PMC11791774) that the script could not fetch."),
    "10_1093_aje_kwag087": (2, [], "Article PDF, plus supplementary material (ADRD definition)",
        "ADRD and non-ADRD hospitalizations 2000-2018 (spans the ICD-10 switch): another ADRD code list."),
    "10_1097_ede_0000000000001456": (3, [220, 268], "Supplements: NIHMS1763059-supplement-eAppendix_1..3.pdf",
        "Already Step 2.5 rank 11: eAppendix 1 lists the 57 cardiovascular and 32 respiratory CCS leaves "
        "(Step 1 S1-13)."),
    "10_1097_ede_0000000000001265": (4, [], "Supplement: NIHMS1662172-supplement-Supplemental_Digital_Content.pdf",
        "Already Step 2.5 rank 20 (low): the main text lists the codes."),
    "10_1016_j_envint_2023_107844": (5, [], "Article PDF",
        "Already Step 2.5 rank 26 (low): greenness and kidney disease in Massachusetts; not cited in Step 1."),
}


def link(p):
    out = []
    if p["pmcid"]:
        out.append("https://pmc.ncbi.nlm.nih.gov/articles/%s/" % p["pmcid"])
    if p["doi"]:
        out.append("https://doi.org/%s" % p["doi"])
    if not out and p["pmid"]:
        out.append("https://pubmed.ncbi.nlm.nih.gov/%s/" % p["pmid"])
    return out


def main():
    papers = json.load(open(IN, encoding="utf-8"))["papers"]
    gaps = [p for p in papers if p["status"] == "no_fulltext" or p["supplements_missing"]]
    missing = [p["slug"] for p in gaps if p["slug"] not in PRIORITY]
    extra = [s for s in PRIORITY if s not in {p["slug"] for p in gaps}]
    assert not missing and not extra, "PRIORITY out of sync: missing %s, extra %s" % (missing, extra)

    items = []
    for p in gaps:
        rank, cv, doc, why = PRIORITY[p["slug"]]
        items.append({
            "rank": rank, "shortlist": rank <= SHORTLIST_SIZE,
            "gap": "no_fulltext" if p["status"] == "no_fulltext" else "supplements_missing",
            "year": p["year"], "title": p["title"], "doi": p["doi"], "pmid": p["pmid"], "pmcid": p["pmcid"],
            "step1_cv": cv, "document": doc, "links": link(p), "why": why,
            "save_to": "papers/%s/" % p["slug"],
        })
    items.sort(key=lambda x: x["rank"])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"source": IN, "shortlist_size": SHORTLIST_SIZE, "n_gaps": len(items), "items": items},
                  f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s: %d gaps, %d shortlisted" % (OUT, len(items), sum(i["shortlist"] for i in items)))


if __name__ == "__main__":
    main()
