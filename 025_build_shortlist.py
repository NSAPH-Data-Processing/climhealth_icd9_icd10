"""Step 2.5: build the prioritized download shortlist from the Step 2.4 gaps.

Input: 024_fulltext_manifest.json (gaps = status no_fulltext, or supplements_missing non-empty).
The ranking is a hand judgement recorded in PRIORITY below (see 025_shortlist.md for criteria);
every gap must appear in PRIORITY, so a new gap after a re-run of Step 2.4 fails loudly.

Output: 025_shortlist.json
Run: .venv/bin/python 025_build_shortlist.py
"""
import json

IN = "024_fulltext_manifest.json"
OUT = "025_shortlist.json"
SHORTLIST_SIZE = 10

# slug -> (rank, step1_cv, document to get, why it matters)
# step1_cv: CV numbers of the Step 1 PDF citation this paper corresponds to (author + year + topic match).
PRIORITY = {
    # --- Tier A: cited in the Step 1 PDF, no full text at all ---
    "10_1001_jama_295_10_1127": (1, [57], "Article PDF, plus any online supplement (eTables)",
        "Dominici 2006 JAMA is the source cited for 6 Step 1 rows (S1-01/02/03/05/06/07: CVD, respiratory, "
        "IHD, CHF, arrhythmia, cerebrovascular). Its cause-specific ICD-9 definitions are the reference set."),
    "10_1001_jama_299_18_2172": (2, [78], "Article PDF, plus any online supplement",
        "Peng 2008 JAMA is cited for S1-01/02/09/11 (CVD, respiratory, COPD, pneumonia/RTI)."),
    "10_1093_aje_kws267": (3, [125], "Article PDF, plus any online supplement",
        "Barr 2012 (smoking bans) is the source for S1-04, acute MI (ICD-9 410)."),
    "10_1016_j_chest_2019_03_017": (4, [202], "Article PDF, plus any online supplement",
        "Rhee 2019 is cited for S1-12 (ARDS, ICD-9 518.82). The 2020 Rhee paper (fetched) lists "
        "518.51-518.53 too, so checking the 2019 definition matters."),
    "10_1016_s2542_5196_21_00168_6": (5, [245, 253], "Article PDF (open-access journal), plus appendix",
        "Chen 2021 is cited for S1-01 (CVD all-cause). Gold open access, so it should download without an account."),
    "10_1093_aje_kwae133": (6, [311], "Article PDF, plus supplementary data",
        "Qin 2024/25 is cited for S1-17 (dementia/Alzheimer's: 290.0, 331.0 / F01-F03, G30)."),
    # --- Tier B: cited in the Step 1 PDF; the fetched text says the ICD codes are in the missing supplement ---
    "10_1097_ede_0000000000000556": (7, [175], "Supplement: NIHMS823701-supplement-Supplemental.docx (eAppendix)",
        "Liu 2017 wildfire paper (S1-27). The main text says 'The ICD-9 codes of diagnoses are in eAppendix'."),
    "10_1016_j_ypmed_2018_02_001": (8, [190], "Supplement: NIHMS944332-supplement.docx",
        "Hopp 2018 (S1-24 heat stroke / heat illness). The supplement lists the ~50 heat-related ICD-9 "
        "diagnoses; the main text names only the CCS groups."),
    "10_1001_jama_2014_15715": (9, [153], "Supplement: NIHMS657527-supplement-Hospitalizations_and_heat_waves_-_Supplemental_Material.pdf",
        "Bobb 2014 JAMA (S1-24, S1-26 heat multi-cause). The main text uses 283 CCS groups; the supplement "
        "should show the categories and codes behind the heat-sensitive outcomes."),
    "10_1080_01621459_2020_1722134": (10, [220, 268], "Article PDF, plus supplementary material (likely paywalled: JASA)",
        "Thomas 2020 is cited for S1-13 (cardiorespiratory). Outcome-wide study (432 ICD-9 CVD codes), so its "
        "value depends on the pending 2.6 decision on outcome-wide papers. Probably needs a library account."),
    # --- Tier C: optional ---
    "10_1097_ede_0000000000001456": (11, [220, 268], "Supplements: NIHMS1763059-supplement-eAppendix_1..3.pdf",
        "Thomas 2022 (S1-13). The main text already defines outcomes as CCS groups 7.x/8.x; the eAppendix "
        "adds the diagnosis list. Outcome-wide."),
    "10_1080_01621459_2020_1803883": (12, [], "Supplement: NIHMS1632056-supplement-Sup23/26/29.pdf (Supplementary Materials, Section 2.2)",
        "Nethery 2021, Clean Air Act (CVD, dementia). The main text says the ICD-9 codes are in Supplement "
        "Section 2.2. Not cited in Step 1. Most other supplement files are code (.r/.md)."),
    "10_1016_j_scitotenv_2020_142524": (13, [238], "Supplements: NIHMS1634916-supplement-1.pdf, -2.docx",
        "Yitshak-Sade 2021 (S1-16). The main text already gives the cohort and main cause codes (332, 3310, 290, 486, ...)."),
    "10_1016_s2542_5196_17_30136_5": (14, [], "Supplement: NIHMS921603-supplement.docx (Supplementary Table 1)",
        "Prada 2017, fracture codes (in Supplementary Table 1). The outcome is not in the Step 1 PDF."),
    "10_1161_circheartfailure_118_005407": (15, [], "Supplement: NIHMS1528632-supplement-Supplemental_Material.pdf (Appendix)",
        "Gilstrap 2019, amyloidosis + HF codes (in the Appendix). The outcome is not in the Step 1 PDF."),
    # --- Tier D: low value (codes already in the fetched main text, or not cited and not code-bearing) ---
    "10_1161_circulationaha_109_851113": (16, [92], "Supplement: NIHMS139389-supplement-1.pdf",
        "Bell 2009 (S1-08, S1-33). Codes are already in the main text (428, 426-427, 430-438, 410-414, 429, ...)."),
    "10_1097_ede_0000000000001337": (17, [242], "Supplement: NIHMS1667651-supplement-Supplemental_Digital_Content.pdf",
        "Yan 2021 (S1-13, S1-30). Codes are already in the main text (390-459; 464-466, 480-487, 490-493)."),
    "10_1097_ede_0000000000001195": (18, [229], "Supplement: NIHMS1650996-supplement-supplemental_material.docx",
        "Rhee 2020 (S1-12). Codes are already in the main text (518.51, 518.52, 518.53, 518.82)."),
    "10_1016_j_scitotenv_2022_156855": (19, [], "Supplement: NIHMS1849786-supplement-supplement.docx",
        "Danesh Yazdi 2022. ICD-9 and ICD-10 codes are already in the main text."),
    "10_1097_ede_0000000000001265": (20, [], "Supplement: NIHMS1662172-supplement-Supplemental_Digital_Content.pdf",
        "deSouza 2021. Codes are already in the main text."),
    "10_1016_j_envint_2021_106737": (21, [], "Supplement: NIHMS1722949-supplement-1.docx",
        "Heo 2021. Codes are already in the main text (CVD ranges, 992.0)."),
    "10_1097_ede_0000000000000777": (22, [], "Supplement: NIHMS916569-supplement-Supplemental_Digital_Content.pdf",
        "Zigler 2018. Codes are already in the main text (490-492, ...)."),
    "10_1161_circoutcomes_111_962456": (23, [], "Supplement: NIHMS353706-supplement-1.pdf",
        "Yeh 2012. MI codes are already in the main text (410.xx except 410.x2)."),
    "10_1002_cncr_28537": (24, [], "Supplement: NIHMS578201-supplement-Supp_appendix_S1.doc",
        "Wang 2014, pancreatic cancer (157.xx in the main text). Not in the Step 1 PDF."),
    "10_1111_biom_12254": (25, [], "Supplement: NIHMS635368-supplement-1.pdf",
        "Boehm Vock 2015, a methods paper. CVD codes are referenced in the main text."),
    "10_1016_j_envint_2023_107844": (26, [], "Article PDF",
        "Lee 2023 Env Int, greenness and kidney disease. Not the EHP paper cited for S1-18 (that one, "
        "ehp10729, was fetched). The kidney codes probably match the EHP paper."),
    "10_1111_j_1467_9876_2008_00640_x": (27, [], "Article PDF",
        "Peng 2009 JRSS-C, a methods paper (IHD, COPD). Not the JAMA 2008 paper cited in Step 1."),
    "10_1093_biostatistics_kxr002": (28, [], "Article PDF",
        "Chang 2011, a methods paper (cardiovascular). Not cited in Step 1."),
    "10_1093_aje_kwr457": (29, [], "Article PDF",
        "Levy 2012 meta-analysis (cardiovascular). Not cited in Step 1."),
    "scholar_RSwElNMAAAAJ_j7_hQOaDUrUC": (30, [], "HEI Research Report PDF",
        "HEI 2016 report on causal methods (respiratory). Not cited in Step 1; no DOI."),
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
