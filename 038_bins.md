# Step 3.8 — Outcome bins for Danielle Braun's code sets, with exposure attributes

**Rewritten on 2026-10-26**, with the same method as the rewritten Step 2.8 (`028_bins.md`). The Step 2.8 bins are applied to Braun's Step 3.6 code sets (`036_icd_codes.json`, the 14 full-text papers), and the bin list is expanded where her papers need it. Step 4 unifies both sets.

## Method
1. **Exposure per paper** → `038_exposures.json`:
   - 7 papers shared with Step 2.8 reuse its entries (`reused_from_step28: true`).
   - 7 new papers were classified by hand:
     - **Long-term air pollution:** Mork 2023, Wang 2024, Qin 2025 and Delaney 2026 (annual or 10-year lagged PM2.5, NO2, ozone).
     - **Short-term extreme heat:** Jung 2025 and Dinehart 2026 (daily heat index).
     - **Other exposure:** Klompmaker 2024 (street-view greenspace).
2. **Bins** → `038_bins.json`:
   - The 49 Step 2.8 bins, with Braun's code sets mapped to them under the same scope rules.
   - **One bin added: K6 "Dehydration and volume depletion"** (Jung 2025: 276.51 / E86.0). It is a key heat outcome: Bobb 2014 reports 276.51 as the most common code in CCS 55 during heat waves. Jung's dehydration set is `exact` for K6 and `narrower` for K2 (fluid and electrolyte disorders).
   - Jung's "heat-related illness" (992.x / T67.3–T67.5) and "exposure to excessive natural heat" (E900 / X30) are `exact` for H1.
   - Bins without a Braun source are kept, with status `no_evidence` and "no source in this set", so the two lists line up for Step 4.
3. **`038_build_bins.py`** (copy of `028_build_bins.py` with Braun inputs) → `038_bins_populated.json`, **`038_bins.csv`**. **Coverage: every explicit code set is binned.**

Run: `.venv/bin/python 038_build_bins.py`.

## Results (50 bins)
| status | n | bins |
|---|---|---|
| `explicit` | 11 | all CVD, AMI, IHD, heart failure (deSouza 2021); **Parkinson's** (5 papers); **dementia/ADRD** (Shi 2020, Mork 2023; Qin 2025 codes not fetched); kidney/urinary, CKD, acute kidney failure (Lee 2022/2023); **dehydration** (K6, new); **heat-related illness** (H1, Jung 2025) |
| `explicit_partial` | 2 | stroke (ischemic 434.91; intracranial hemorrhage as CCS), fluid/electrolyte (dehydration only) |
| `classification` | 9 | all respiratory, pneumonia/influenza, cerebrovascular, aneurysm (Thomas 2022 CCS); peripheral vascular, diabetes with complications, sepsis, UTI, heat composite (Weinberger 2021 / Spangler 2023 CCS) |
| `no_evidence` | 28 | no Braun paper: all respiratory-specific bins except the composites, arrhythmia, cardiac arrest, depression and psychiatric bins, rare bins, infections, injuries, cancer, outcome-wide scans |

**Exposure support in Braun's set:**
- **Long-term air pollution:** Parkinson's (Shi, Wang, Delaney), dementia (Shi, Mork, Qin), and kidney (Lee 2022, Lee 2023).
- **Short-term air pollution:** the cardiovascular bins (deSouza 2021, Thomas 2022) and the Thomas respiratory CCS groups.
- **Short-term extreme heat:**
  - Parkinson's (Dinehart 2026);
  - heat-related illness and dehydration (Jung 2025);
  - fluid/electrolyte disorders, renal failure, sepsis, UTI, diabetes with complications and peripheral vascular disease (Weinberger 2021, CCS);
  - the heat composite (Spangler 2023).
- **Extreme weather:** none. Braun's set has no cyclone, drought or wildfire paper.

**New relative to Step 2.8:**
- Parkinson's gains short-term heat support (Dinehart 2026) and 3 more long-term air pollution papers.
- Dementia gains Mork 2023.
- Heat-related illness gains an `exact` code set with ICD-10 (Jung 2025).
- Dehydration becomes its own bin.

## Outputs
| File | Purpose |
|---|---|
| `038_exposures.json` | Exposure attributes for the 14 Braun full-text papers (7 reused, 7 new) |
| `038_bins.json` | The Step 2.8 bins plus K6, mapped to Braun's code sets |
| `038_build_bins.py` | Copy of `028_build_bins.py` with Braun inputs |
| `038_bins_populated.json`, `038_bins.csv` | Per bin: status, exposure attributes, support, sources |
