# Step 3.6 — Data source and ICD codes per outcome (Danielle Braun's papers)

Same method, fields and statuses as Step 2.6 (`026_icd_codes.md`), including the added status `in_unfetched_supplement`. Input: the 17 papers in `034_fulltext_manifest.json`; 14 have full text.

## Method
1. **`036_extract_text.py`** (copy of 026, input 034) wrote `papers/<slug>/text/` for the new papers. Shared papers already had their text.
2. **Labels** → `036_labels.json`:
   - **7 shared papers reuse their Step 2.6 labels** (`reused_from_step26: true`).
   - **7 papers were read by hand.** These are the 6 new full texts and **Qin 2025 AJE**, which only now has a PDF (Step 3.4). The passage search helper is now `.cache/036_snippets.py` (inside the project).
3. **`036_build_icd_codes.py`** (copy of 026; inputs 034 and 036) → **`036_icd_codes.json`**. **All quotes were found** and located.

Run: `.venv/bin/python 036_extract_text.py && .venv/bin/python 036_build_icd_codes.py`.

## Results
**All 14 full-text papers use MedPAR / Medicare Part A FFS claims (`stated`).** There are 35 outcome entries.

The papers read in this step:

| Paper | Outcome | Codes | Position |
|---|---|---|---|
| Mork 2023 Env Int (ADRD, lagged air pollution) | first hospitalization with ADRD | **CCW list: 24 ICD-9 + 22 ICD-10** (Table S1) | any of the first 10 |
| Qin 2025 AJE (ADRD, causal methods) | first hospitalization with ADRD | CCW algorithm; codes in Appendix S1, **not fetched** | any |
| Klompmaker 2024 Env Int (PD, street-view greenspace) | first PD-involved hospitalization | ICD-9 332.0, 332.1 / ICD-10 G20, G21.11, G21.19, G21.8 | any discharge diagnosis |
| Wang 2024 npj PD (PD, air pollution) | first hospitalization with PD | ICD-9 332 / ICD-10 G20 | first 10 |
| Dinehart 2026 J Expo Sci Environ Epidemiol (PD, extreme heat) | first hospitalization with PD (warm season) | ICD-9 332.0 / ICD-10 G20 | first 10 |
| Delaney 2026 Environ Epidemiol (PD, 10-year air pollution) | first hospitalization with PD | ICD-9 332/332.0 / ICD-10 G20 | first 10 |
| Jung 2025 Environ Epidemiol (heat, Greater Boston) | heat-related illness; excessive natural heat; dehydration | 992.0–992.9 / T67.3–67.5; E900 / X30; 276.51 / E86.0 | principal or secondary |

**Observations:**
- **There are three PD definitions:**
  - 332 or 332.0 / G20 (Wang 2024, Dinehart 2026, Delaney 2026).
  - 332.0 + 332.1 / G20 + G21.x (Klompmaker 2023 JAMA Netw Open and Klompmaker 2024).
  - 332 / G20, G21.11, G21.19, G21.8 (Shi 2020).

  332.1 (secondary parkinsonism) and G21.x are included only by some.
- **The ADRD CCW list in Mork 2023 is identical to Klompmaker 2023 JAMA Netw Open.** Qin 2025 uses the CCW algorithm too, but its list was not fetched.
- **Jung 2025 (Boston heat): its ICD-10 heat range (T67.3–T67.5) is narrower than its ICD-9 range** (992.0–992.9). 992.x maps to T67.0–T67.9, so this deserves a check.

## Outputs
| File | Purpose |
|---|---|
| `036_extract_text.py`, `036_build_icd_codes.py` | Copies of the Step 2.6 scripts with Braun inputs and outputs |
| `036_labels.json` | 14 paper labels (7 reused, 7 new) |
| `036_icd_codes.json` | One record per Step 3.4 paper (17), with 35 outcome entries |
