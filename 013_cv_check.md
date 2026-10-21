# Step 1.3 — Do the CV numbers in the Step 1 document point to the right CV papers?

Inputs: the Step 1 rows and citations (`010_icd_mappings.json`, Section 1) and the numbered journal articles of `Dominici_CV_updated_10132026.pdf`.

## Method
1. **`013_parse_cv.py`** → `013_cv_articles.json`. It parses the "Journal Articles (peer reviewed)" section of the CV (pdftotext `-layout`): **352 articles, numbered 1–352 with no gaps**. For each it records the authors, year, title, journal, DOI, PMID and page.
   - Most entries are "Authors (year). Title. Journal …". Entries #332–#337 use a "Journal. 2025;…" style, which is parsed separately.
   - DOIs split at a line break are rejoined.
2. **`013_check_cv_numbers.py`** → `013_cv_check.json`. It takes each of the **69 (Step 1 row, CV number) pairs** (47 distinct CV numbers) and checks:
   - `author_ok`: the Step 1 surname is the CV first author.
   - `year_ok`.
   - `journal_ok`: when Step 1 names a journal.
   - **`topic`**: a hand judgement of whether the CV paper fits the row's outcome (`ok` / `partial` / `mismatch`, with a note). It is kept in `TOPIC` in the script.
   - CV duplicates (the same DOI under two numbers), and CV entries whose DOI or PMID belong to another article.

Run: `.venv/bin/python 013_parse_cv.py && .venv/bin/python 013_check_cv_numbers.py`.

## Results
**The numbering is right for nearly all citations.** 57 of 69 pairs are `ok`, 11 are `ok_with_note`, and **1 is a mismatch**. Year, journal and topic agree in every other case.

| Row | CV | Finding |
|---|---|---|
| **S1-01** all CVD | **#323** | **Mismatch.** #323 is Danesh Yazdi 2025 Environ Int, on *second* MI / ischemic stroke admissions (correct for S1-37). The all-CVD paper (ICD-9 390–459, ICD-10 "I…") is **#332**, Danesh Yazdi 2025 Environ Res. S1-01 probably meant #332. |
| S1-02, S1-09, S1-10, S1-34 | #94 | Step 1 says "Bell et al. 2009", but CV #94 is **Peng** 2009 EHP (Bell is second author). The topic fits (PM2.5 composition). #89 is the Bell 2009 AJRCCM paper. |
| S1-13 | #220 | The CV entry is right (Thomas 2020 JASA, 432 CVDs), but it carries the DOI and PMID of #268 (Thomas 2022 Epidemiology). |
| S1-36 | #303, #309 | The same article (Feng 2024 Nat Commun) is listed twice in the CV. |
| S1-17 | #320, #339 | Partial fit. ADRD defines the **cohort**; the outcomes are mortality and readmission (#320) or hospitalization (#339). Neither defines dementia as an outcome. |
| S1-18 | #282 | Partial. Lee 2023 is AKI only (584/N17); the row's CKD codes (585/N18) come from Lee 2022 BMJ Medicine, which isn't cited. |

Other notes:
- #173 and #175 are both Liu wildfire papers. #173 is the Epidemiology paper (CV year 2016, volume 28 2017); #175 is the AJE 2017 vulnerability paper. Step 1 cites them correctly.
- #304 Sun 2024 BMJ fits its row (S1-01), but it uses commercial and Medicare Advantage claims, not Medicare FFS.

### The CV itself (outside the Step 1 citations)
- **23 DOIs appear under two or three CV numbers.** Examples: #137/#158/#256, #139/#258, #192/#196, #303/#309, #345/#348. The full list is in `cv_duplicate_dois_all`. This looks like copy-paste duplication in the CV, mostly around 2021–2022.
- #220 has the identifiers of #268.

## Effect on later steps
I made the Step 2.7 crosswalk (`027_crosswalk.json`) from author and year before this check. It is now corrected to follow the CV:
- #94 → Peng 2009 EHP, which is in the set.
- #173 (not #175) → the Epidemiology wildfire paper.
- #253 and #339 → papers outside the set.
- #323 → the second-events paper only.

The Step 2.7 table was rebuilt. Its verdict counts are unchanged.

## Outputs
| File | Purpose |
|---|---|
| `013_parse_cv.py` | CV PDF → `013_cv_articles.json` |
| `013_cv_articles.json` | 352 numbered CV journal articles |
| `013_check_cv_numbers.py` | Checks the Step 1 citations; hand topic labels are in `TOPIC` |
| `013_cv_check.json` | One record per (row, CV) pair with checks, flags and verdict; plus all duplicate DOIs in the CV |
