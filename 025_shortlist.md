# Step 2.5 — Shortlist of documents to download manually

Input: `024_fulltext_manifest.json`. Run: `.venv/bin/python 025_build_shortlist.py` → `025_shortlist.json`.

## Candidates
There are **30 gaps** from Step 2.4:
- **12 papers with no full text.**
- **18 papers whose referenced supplements could not be fetched.** These are NIH author manuscripts whose supplements are only on the PMC website.

## How they were ranked
The ranking is a hand judgement, recorded in `PRIORITY` in the script. The script fails if a gap is missing from that table.

1. **Tier A: cited in the Step 1 PDF and no full text at all.** Without these, the Step 1 rows they support cannot be checked.
2. **Tier B: cited in the Step 1 PDF, and the fetched text says the ICD codes are in the missing supplement.** For example, "The ICD-9 codes of diagnoses are in eAppendix".
3. **Tier C: optional.** These are outcome-wide papers, papers not cited in Step 1 whose supplement holds the codes, or papers whose main text already gives most of the codes.
4. **Tier D: low value.** Either the main text already lists the codes, or the paper is a methods paper not cited in Step 1.

**Matching to Step 1 citations.** The first author and year were matched against `012_publications.json`, then confirmed by topic. Two author+year matches were rejected because they are different papers:
- Peng 2009 JRSS-C is not Peng 2008 JAMA (#78).
- Lee 2023 Env Int is not Lee 2023 EHP (#282), which was fetched.

## Shortlist (top 10)
Save each file in the listed folder (the folders are already created). Keep the original file name; for an article PDF, `fulltext.pdf` is fine. **Most of these are probably free in a normal browser**: items with a PMC link are author manuscripts on PubMed Central, and #5 is open access. Only #10 probably needs a library account.

| # | Get | Paper | Link | Step 1 | Save to |
|---|---|---|---|---|---|
| 1 | Article PDF + any supplement | Dominici 2006 JAMA, PM2.5 and CVD/respiratory admissions | [PMC3543154](https://pmc.ncbi.nlm.nih.gov/articles/PMC3543154/) | #57 → S1-01/02/03/05/06/07 | `papers/10_1001_jama_295_10_1127/` |
| 2 | Article PDF + any supplement | Peng 2008 JAMA, coarse PM | [PMC3169813](https://pmc.ncbi.nlm.nih.gov/articles/PMC3169813/) | #78 → S1-01/02/09/11 | `papers/10_1001_jama_299_18_2172/` |
| 3 | Article PDF + any supplement | Barr 2012 AJE, smoking bans and AMI | [PMC3530376](https://pmc.ncbi.nlm.nih.gov/articles/PMC3530376/) | #125 → S1-04 | `papers/10_1093_aje_kws267/` |
| 4 | Article PDF + any supplement | Rhee 2019 Chest, PM2.5/ozone and ARDS | [PMC6607425](https://pmc.ncbi.nlm.nih.gov/articles/PMC6607425/) | #202 → S1-12 | `papers/10_1016_j_chest_2019_03_017/` |
| 5 | Article PDF + appendix | Chen 2021 Lancet Planetary Health, temporal variation | [doi](https://doi.org/10.1016/s2542-5196(21)00168-6) (open access) | #245/#253 → S1-01 | `papers/10_1016_s2542_5196_21_00168_6/` |
| 6 | Article PDF + supplementary data | Qin 2024/25 AJE, ADRD methods comparison | [PMC11735961](https://pmc.ncbi.nlm.nih.gov/articles/PMC11735961/) | #311 → S1-17 | `papers/10_1093_aje_kwae133/` |
| 7 | Supplement `NIHMS823701-supplement-Supplemental.docx` (eAppendix) | Liu 2017 Epidemiology, wildfire PM2.5 | [PMC5130603](https://pmc.ncbi.nlm.nih.gov/articles/PMC5130603/) | #175 → S1-27 | `papers/10_1097_ede_0000000000000556/` |
| 8 | Supplement `NIHMS944332-supplement.docx` | Hopp 2018 Prev Med, heat-wave diagnoses | [PMC6040588](https://pmc.ncbi.nlm.nih.gov/articles/PMC6040588/) | #190 → S1-24 | `papers/10_1016_j_ypmed_2018_02_001/` |
| 9 | Supplement `NIHMS657527-supplement-Hospitalizations_and_heat_waves_-_Supplemental_Material.pdf` | Bobb 2014 JAMA, cause-specific heat risk | [PMC4319792](https://pmc.ncbi.nlm.nih.gov/articles/PMC4319792/) | #153 → S1-24/26 | `papers/10_1001_jama_2014_15715/` |
| 10 | Article PDF + supplementary material | Thomas 2020 JASA, 432 cardiovascular diseases | [doi](https://doi.org/10.1080/01621459.2020.1722134) (likely paywalled) | #220/#268 → S1-13 | `papers/10_1080_01621459_2020_1722134/` |

**Why each matters** (the full text is in `why` in the JSON):
- **#1–#6** are the publications the Step 1 PDF cites for those rows, and none of their text is available.
- **#7–#9** are cited papers whose fetched text sends the reader to the supplement for the ICD codes.
- **#10** is outcome-wide. Its value depends on the pending Step 2.6 decision about outcome-wide papers.

## Not shortlisted (ranks 11–30, in `025_shortlist.json`)
- **Optional (11–15):**
  - Thomas 2022 eAppendices (CCS groups already in the main text)
  - Nethery 2021 supplement (codes in Supplement Section 2.2; not cited in Step 1)
  - Yitshak-Sade 2021 supplement (main codes already in the text)
  - Prada 2017 fracture codes
  - Gilstrap 2019 amyloidosis codes (the outcomes of these last two are not in Step 1)
- **Low (16–30):**
  - Supplements of papers whose main text already lists the codes: Bell 2009, Yan 2021, Rhee 2020, Danesh Yazdi 2022, deSouza 2021, Heo 2021, Zigler 2018, Yeh 2012, Wang 2014, Boehm Vock 2015.
  - Uncited methods or other papers: Lee 2023 Env Int, Peng 2009, Chang 2011, Levy 2012, HEI 2016.

## After downloading
Tell me which items you got. I will register the files in the Step 2.4 manifest with source `manual_download` and update each paper's status. Anything not obtained stays a gap, and Step 2.6 will report it as "not found in available text".
