# Step 2.7 — Step 1 check table

**Open `027_step1_check.csv`.** It has one row per Step 1 mapping: the Step 1 codes, a row verdict, and one short line per cited paper. The detail is in `027_step1_check.json`, and the full code lists remain in `026_icd_codes.json`.

## How it works
1. **Crosswalk** (`027_crosswalk.json`, made by hand; CV numbers checked against the CV itself in Step 1.3, `013_cv_check.md`). It maps each of the 47 CV numbers cited in Step 1 to a Step 2.4 paper, matched on author, year and topic. When there is no matching paper, it gives the reason (16 CVs are not in the Step 2.4 set). For each Step 1 row it also chooses which Step 2.6 outcomes of the cited paper to compare. Optionally it lists **context** papers: uncited papers with the same outcome. They are shown in the CSV but never change the verdict.
2. **Comparison** (`027_build_check.py`). The ICD-9 and ICD-10 codes are compared separately, reduced to 3-character categories (e.g. `410–414` → 410…414; `4280` → 428).

| verdict | meaning |
|---|---|
| `match` | same categories (and the same specific codes, when either side gives them) |
| `match_category` | same categories, different specific codes (e.g. ARDS 518.82 vs 518.51–518.82) |
| `differs` | different categories; the CSV lists `missing` (in Step 1 only) and `extra` (in the paper only) |
| `not_comparable` | the paper gives only CCS groups, or Step 1 gives no codes |
| `no_evidence` | no full text, codes in an unfetched supplement, or the paper is not in the set |

- **Paper verdict:** the worse of its ICD-9 and ICD-10 verdicts. A version that the paper doesn't use is skipped (e.g. no ICD-10 before 2015).
- **Row verdict:** the best verdict among the cited papers (`match` → `supported`).
- Section 2 rows (broader literature) are `not_checked`.

Run: `.venv/bin/python 027_build_check.py`. No new packages.

## Results (37 Section 1 rows)
| row verdict | n | rows |
|---|---|---|
| supported | 2 | S1-01 all CVD (Bravo 2017), S1-14 diabetes (Zanobetti 2014) |
| match_category | 2 | S1-12 ARDS (Step 1 518.82 only; Rhee 2020 uses 518.51–518.53 + 518.82), S1-24 heat stroke (992.0 in Wang 2016; Step 1 also lists 992.0–992.9) |
| differs | 14 | see below |
| not_comparable | 3 | S1-26 Bobb 2014 (CCS), S1-29 drought (Step 1 gives no codes, but Berman 2017 lists CVD and respiratory codes), S1-36 Feng 2024 (CCS) |
| no_evidence | 16 | the cited paper has no full text (Dominici 2006, Peng 2008, Barr 2012 …) or is not in the Step 2.4 set |

### Rows that differ (worth checking first)
- **The Step 1 range is broader than the paper's definition:**
  - S1-02 respiratory: Bravo 2017 uses COPD + RTI, not 460–519.
  - S1-13 and S1-30: Yan 2021 uses 390–459 + 464–466, 480–487, 490–493, not 390–519.
  - S1-15 neurological 320–359: Zanobetti 2014 uses 290, 331.0, 332, 340.
  - S1-16 CDBD: Yitshak-Sade 2021 uses 290, 331.0, 332.
  - S1-19 psychiatric 290–319: Qiu 2022 covers depression, schizophrenia and bipolar disorder only.
  - S1-33 and S1-34: the CO and composition papers use the MCAPS five causes / COPD + RTI.
  - S1-35: Kioumourtzoglou 2013 uses 390–429, not 390–459.
  - S1-37 second events: Danesh Yazdi 2025 covers MI and ischemic stroke only.
- **The paper has codes that Step 1 lacks:**
  - S1-08 CO: Bell 2009 also uses 426, 429, 430–438, 440–448, and has no 786.5.
  - S1-17 dementia: Lee 2019 adds 291 and 294.
  - S1-30: Parks 2021's CCS causes include scattered extra codes.
- **Step 1 has codes the paper lacks:**
  - S1-04 MI: ICD-10 I22 is not in Schwartz 2023 (I21 only).
  - S1-18 kidney: Lee 2023 is AKI only (584/N17); CKD 585/N18 comes from Lee 2022, which is not cited.
- **Printed typos show up as extras:** "I163" in Danesh Yazdi 2025 appears as an extra I16.

**Step 1.3 corrections built in:**
- #94 is Peng 2009 EHP, so it is now compared in S1-02 and S1-34.
- #173 (not #175) is the Epidemiology wildfire paper.
- #253 and #339 are papers outside the set; the Spoto 2025 dementia-codes paper is now context only.
- S1-01 cites #323, which is the second-events paper and has no all-CVD outcome. The all-CVD Danesh Yazdi 2025 paper (#332) is shown as context.

### No evidence (16 rows)
- 9 rows cite only papers outside the Step 2.4 set: S1-10, S1-20–S1-23, S1-25, S1-28, S1-31, S1-32.
- 6 rows depend on papers with no full text: S1-03, S1-05, S1-06, S1-07, S1-09 and S1-11 rely on Dominici 2006 / Peng 2008, which are items 1–2 of the Step 2.5 download list.
- 1 row depends on an unfetched supplement: S1-27 (Liu 2017 eAppendix, item 7 of the Step 2.5 list).
- Context papers already show the usual definitions for several of these. For example:
  - IHD 410–414 / I20–I25: Klompmaker 2021 and Wei 2024 match.
  - CBV 430–438 / I60–I69: matches.
  - CHF 428 / I50: matches.
  - COPD 490–492, 494–496: Kioumourtzoglou 2013 matches.

## Caveats
- **Categories are 3 characters.** A verdict of `match` does not mean the 4th and 5th digits agree, unless specific codes were given (then the verdict is `match_category`).
- **The crosswalk and the row → outcome choices are one reader's judgement.** They are listed explicitly in `027_crosswalk.json`.
- Step 1 codes are taken from the parsed `010_icd_mappings.json`. Cells with "Multiple" or "Varies" may parse only partly.

## Outputs
| File | Purpose |
|---|---|
| `027_crosswalk.json` | Hand crosswalk: CV → papers; Step 1 row → 026 outcomes; context papers |
| `027_build_check.py` | Builds the check |
| `027_step1_check.csv` | **The review table** (65 rows; the 28 Section 2 rows are `not_checked`) |
| `027_step1_check.json` | The same with full detail: per-version verdicts, missing/extra codes, and evidence locations |
