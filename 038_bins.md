# Step 3.8 — Reference outcome bins from Danielle Braun's papers

Same bins, scope rules and statuses as Step 2.8 (`028_bins.md`). The sources are the Step 3.6 outcomes (`036_icd_codes.json`, the 17 Braun papers).

Run: `.venv/bin/python 038_build_bins.py` → `038_bins_populated.json`, **`038_bins.csv`**. The hand map is `038_bins.json`.

## Results (27 bins)
| status | n | bins |
|---|---|---|
| `explicit` | 6 | AMI, IHD, heart failure (deSouza 2021; ICD-9 only), **Parkinson's (5 papers, ICD-9 and ICD-10)**, **dementia/ADRD** (Shi 2020, Mork 2023; Qin 2025 codes not fetched), **acute kidney failure** (Lee 2023: 584/N17) |
| `explicit_partial` | 2 | stroke (deSouza ischemic stroke 434.91; Thomas 2022 intracranial hemorrhage), fluid and electrolyte disorders (Jung 2025 dehydration 276.51 / E86.0) |
| `classification` | 4 | cerebrovascular (Thomas TCI, CCS 7.3.4); diabetes with complications, sepsis and UTI (Weinberger 2021 CCS 50, 2, 159) |
| `not_found` | 15 | **all 6 respiratory bins**, arrhythmia, cardiac arrest, hypertensive heart disease, blood clots, retinal artery occlusion, depression, skin infections, Pneumocystis, intestinal obstruction |

**What Braun's set adds beyond Dominici's (Step 2.8):**
- **Parkinson's:** 4 new papers with explicit ICD-9 and ICD-10 codes. All define PD as any of the first 10 diagnosis positions. The codes are 332/332.0/G20, with or without 332.1/G21.x (`036_icd_codes.md`).
- **ADRD:** Mork 2023, the full CCW list (ICD-9 and ICD-10). It is identical to Klompmaker 2023, which was already in Step 2.8.
- **Fluid and electrolyte disorders:** Jung 2025 adds an explicit dehydration code with ICD-10 (276.51 / E86.0).

Everything else in Braun's set is a paper shared with Dominici's set. So the **combined Steps 2.8 + 3.8 coverage is the Step 2.8 picture plus these additions.** The Braun set does not add any respiratory or rare-bin evidence.

## Outputs
| File | Purpose |
|---|---|
| `038_bins.json` | Hand map: bin → Step 3.6 outcome entries |
| `038_build_bins.py` | Copy of `028_build_bins.py` with inputs 036, 037 and 038 |
| `038_bins_populated.json`, `038_bins.csv` | One row per bin with sources and codes |
