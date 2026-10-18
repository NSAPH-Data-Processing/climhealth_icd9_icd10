# Step 2.6 — Data source and ICD codes per outcome, from the full texts

Input: the 63 papers in `024_fulltext_manifest.json`. **51 have full text** and were read. The other 12 (`no_fulltext`) are kept with no outcomes; Step 2.5 lists them for manual download. Run on **2026-10-18**.

`papers/` did not exist on this machine (Step 2.4 ran elsewhere). It was rebuilt with `.venv/bin/python 024_fetch_fulltext.py`, which produced a byte-identical manifest. No manually downloaded files (Step 2.5) were present, so none are used here.

## Method
1. **`026_extract_text.py`** turns every full text and supplement into `papers/<slug>/text/<file>.txt` (git-ignored), with location markers:
   - PDF: `=== page N ===`. It uses poppler's `pdftotext` when it is on the PATH, because pdfplumber interleaves the two columns of journal PDFs.
   - JATS XML: `=== section: A > B ===`, `=== table: … ===` (including tables in `<floats-group>`), and `=== abstract ===`.
   - DOCX: `=== table N ===`. XLSX: `=== sheet: … ===`.
   - The two zip supplements are not extracted. They hold R code and figure data.
2. **Claude read the methods and supplements of all 51 papers.** A scratch search script (not committed) pulled the relevant passages: MedPAR, FFS, Part A, claims, ICD, CCS/CCW, principal/primary diagnosis, code patterns, and eAppendix/supplement pointers. The hand labels are in **`026_labels.json`**: the data source, each outcome, its codes **as written**, the ICD version, the diagnosis position, and a verbatim quote with its file.
3. **`026_parse_ccs_tables.py`** → `026_ccs_tables.json` parses the outcome-wide code table of **Parks 2021** (Nat Commun, tropical cyclones), Supplementary Table 2. It covers 214 CCS level-3 groups and 11,068 ICD-9-CM codes, grouped under 13 level-1 causes. The parser reads table cells from their rectangle borders and joins rows split by page breaks. Gray text marks the 106 groups that were not used in the level-3 analyses.
4. **`026_build_icd_codes.py`** → **`026_icd_codes.json`**. It finds every quote in the extracted text (ignoring case, spaces and punctuation) and records its location (page, section or table). A missing quote stops the build. **All quotes were found.**

Run: `.venv/bin/python 026_extract_text.py && .venv/bin/python 026_parse_ccs_tables.py && .venv/bin/python 026_build_icd_codes.py`. New packages (`requirements.txt`): pdfplumber 0.6.0, python-docx 0.8.11 and openpyxl 3.0.10, which are the last versions for Python 3.6. Pip was upgraded to 21.3.1 inside `.venv` so it could install the `cryptography` wheel.

## Output fields (`026_icd_codes.json`, one record per paper)
- **Paper:** `slug, doi, pmid, pmcid, year, title, fulltext_status, supplements_missing, step23_outcome_names`
- **Data source:** `medpar_or_ffs`, `data_source`, `data_source_evidence {file, location, quote}`
  - `medpar_or_ffs`:
    - `stated` (44): the paper names MedPAR, Part A, inpatient claims or FFS.
    - `implied` (7): "Medicare billing claims" or "Medicare hospital admissions" without naming MedPAR or FFS (2009–2014 MCAPS-type papers, Prada 2017, AAAI 2025).
    - `null`: no full text.
  - **All 51 papers use Medicare inpatient (Part A) admissions.** None was filtered out.
- **Outcome-wide papers:** `outcome_wide` is a short description for the 6 papers that scan many groups.
- **`outcomes[]`:** `outcome_name` (as named in the methods), `step23_outcome_name` (mapped to the Step 2.3 `outcome_names`; null for controls and other extras), `role`, `codes_status`, `classification`, `icd9`, `icd10`, `icd_versions`, `diagnosis_position`, `cites`, `evidence`, `position_evidence`, `note`.
  - `role` values: `outcome`, `negative_control`, `excluded`, `covariate`, `sensitivity`, `cohort`, and `component` (a Parks group that was not analyzed on its own).
  - `diagnosis_position`:
    - `principal`: "primary" or "principal" diagnosis.
    - `principal_or_secondary`.
    - `any`: any listed position (the first 10 or 25 fields).
    - `null`: not stated.

### `codes_status` (one decision added)
| value | meaning | n entries |
|---|---|---|
| `explicit_codes` | the codes are listed | 343 (227 of them are Parks groups) |
| `classification_ref` | a named grouping (CCS, CCSR) with group numbers but no ICD codes | 47 |
| `cites_prior_paper` | the definition is taken from a cited paper | 1 (AAAI 2025 → Bobb 2014) |
| `not_listed` | the available text names the outcome but gives no codes, and points nowhere | 2 |
| **`in_unfetched_supplement`** | the text says the codes are in a supplement that Step 2.4 could not fetch | 11 |

**Decision:** `in_unfetched_supplement` is **not one of the four statuses in CLAUDE.md**. I added it because Step 2.4 noted that these papers cannot be marked `not_listed`: the codes exist, just not in a file we have. If the Step 2.5 downloads arrive, these entries can be relabeled.

**Codes are kept as written:** ranges such as `426–427` or `426 to 427`, wildcards such as `410.xx` or `410.X1`, `·` decimal points, and codes without dots in the Parks table. Apparent typos are kept and explained in `note`:
- `490-448` and `480-497` (jes 2013)
- `390 to 495` as "CVD" (Medicaid/Medicare 2021)
- `559` for UTI (CDBD 2021)
- `I163` for ischemic stroke (2025 ×2)
- Parks: five codes that seem to lack a leading digit (`4660` → 34660, `330` → 4330, `400` → 4400, `9300` → 49300, `0323` → 00323), flagged by `suspect_codes`.

## Results (51 papers with full text)
| What the paper gives for its main outcomes | papers |
|---|---|
| Explicit ICD codes for all of them | **37** |
| Classification groups only (CCS/CCSR numbers): Bobb 2014, Wei 2019 BMJ, Weinberger 2021 heat warnings, Thomas 2022 MOReTreeS, ee9 2023 heat metric, Nat Commun 2024 infections | 6 |
| Codes in an unfetched supplement: Prada 2017 fractures, Liu 2017 wildfire, Hopp 2018 heat diagnoses, Gilstrap 2019 amyloidosis, Nethery 2021 CAAA | 5 |
| Not listed: Biometrics 2015 (CVD "among others") | 1 |
| Explicit codes, but one subtype not listed: dementia 2019 (vascular dementia subtype codes) | 1 |
| Cites a prior paper: AAAI 2025 | 1 |

- **ICD-10 codes appear in 17 papers.** These are the 2000–2016 cohorts that span the October 2015 switch, plus the ICD-10-only Alzheimer's 2025 paper.
- **Diagnosis position** (177 entries outside Parks):
  - principal: 143
  - principal or secondary: 10. These are the neuro papers (PD/ADRD), kidney/CKD, ARDS, amyloidosis and the CDBD cohort.
  - any position: 8 (dementia 2019, AKI 2023, Alzheimer's 2025)
  - not stated: 16
- **Outcome-wide papers** (the CLAUDE.md rule is to extract every group):
  - **Parks 2021:** all **13 level-1 causes and 214 level-3 groups**, with all their ICD-9-CM codes.
  - **Alzheimer's 2025:** all 17 ICD-10 codes, in 5 categories.
  - **Wei 2019:** 214 CCS groups. Only the 17 groups named in the text are listed (with CCS numbers), plus injury/poisoning as a negative control. The full list is only in figure images (Figures S1–S2) and on the HCUP website.
  - **Bobb 2014:** 283 CCS groups (214 analyzed). The 6 named groups are listed, including CCS 244 for heat stroke. eTable 5 was not fetched.
  - **Thomas 2022:** 57 + 32 multi-level CCS leaves. The groups in Tables 2–3 are listed (7.3.1.1, 7.4.2.2, 7.3.4, 7.2.11, 8.1.2). The leaves are in eAppendix 1, which was not fetched.
  - **Hopp 2018:** 50 diagnoses, all in Supplemental Table S1, which was not fetched.

## Observations for the ICD check (to verify against Step 1)
- Several CVD definitions recur across papers:
  - **The MCAPS five-cause set:** HF 428, rhythm 426–427, cerebrovascular 430–438, IHD 410–414 + 429, PVD 440–448. It appears in 2009–2018 papers.
  - **The 390–459 / I00–I99 "all CVD" range** (2021+ cohorts).
  - **CHD 410–414 / I20–I25 and CBV 430–438 / I60–I69.**
  - **MI 410.x0/410.x1 / I21** and **ischemic stroke 433.x1, 434.x1, 436 / I63** (the DRAM / difference-in-differences papers).
- Respiratory definitions vary:
  - 460–519 / J00–J99 (all respiratory)
  - 464–466 + 480–487 + 490–492 (RTI + COPD)
  - the same plus 493, asthma (tropical cyclones 2021, Burrows 2023)
- "All CVD" in envint 2021 (northeast greenspace) stops at 429, unlike 390–459 elsewhere.

## Caveats
- **Single reader (Claude).** The quotes are machine-verified, but the choice of passage and the reading of position or role are not.
- **The Parks table was parsed automatically.** It yields 214 groups, 108 of them in black (used in the level-3 analyses, which the paper restricts to groups with more than 50,000 admissions). Gray versus black text was read from the PDF colour. One check passed: every level-3 group got exactly one number and one level-1 cause. The paper itself does not state the total number of groups, so 214 could not be checked against it.
- For XML-only papers (author manuscripts), locations are sections or tables, not pages.
- 12 papers have no full text, and 18 have missing supplements (Step 2.5). The outcomes of those papers are either absent or marked `in_unfetched_supplement`.

## Outputs
| File | Purpose |
|---|---|
| `026_extract_text.py` | Full text and supplements → `papers/<slug>/text/*.txt` (git-ignored) |
| `026_parse_ccs_tables.py` | Supplement code tables → `026_ccs_tables.json` (Parks 2021) |
| `026_ccs_tables.json` | 214 CCS level-3 groups: level-1 cause, ICD-9-CM codes, `in_level3_analysis`, pages, `suspect_codes` |
| `026_labels.json` | Hand labels for the 51 papers |
| `026_build_icd_codes.py` | Merges the labels and tables, and verifies quotes → `026_icd_codes.json` |
| `026_icd_codes.json` | One record per paper (63) with its outcomes (404 entries; 227 from Parks) |

## Carry forward
- Compare these definitions with the Step 1 mappings (`010_icd_mappings.json`) by outcome, using `step23_outcome_name` and the Step 1 publication numbers.
- If Step 2.5 downloads arrive, register them in the Step 2.4 manifest, re-run the extraction, and relabel the `in_unfetched_supplement` entries and the 12 `no_fulltext` papers.
