# Step 2.8 — Can the reference outcome bins be populated from the Step 2 publications?

Input: the reference list in CLAUDE.md Step 2.8 (27 bins in 5 groups) and the Step 2.6 outcomes (`026_icd_codes.json`). It covers the 51 papers with full text, including the Parks 2021 CCS table.

## Method
1. **Search.** Each bin was searched by keyword in every Step 2.6 outcome and in the Step 2.3 outcome names (abstract level). The script is `.cache/028_scan.py`, which is not committed. The rare bins (Pneumocystis, retinal artery occlusion, intestinal obstruction, cardiac arrest, hypertensive heart disease) were also searched in all 476 Step 2.2 abstracts and the full texts. **No paper in the set studies any of them as an outcome.**
2. **Hand map** → `028_bins.json`. For each bin I listed the Step 2.6 outcome entries that populate it, with a **scope**:
   - `exact`: the paper's outcome is this bin.
   - `narrower`: the outcome is part of the bin (e.g. ischemic stroke for "stroke").
   - `broader`: the paper's group contains the bin plus other conditions. A code **filter** then picks the bin-specific ICD-9 codes inside the group, e.g. 362.3x retinal artery occlusion inside CCS 87, or 136.3 Pneumocystis inside CCS 122.
3. **`028_build_bins.py`** → `028_bins_populated.json` and **`028_bins.csv`** (one row per bin).

**Bin status** (the best source wins):

| status | meaning |
|---|---|
| `explicit` | an `exact` source lists ICD codes |
| `explicit_partial` | ICD codes come only from `broader` (filtered) or `narrower` sources |
| `classification` / `no_codes` / `not_found` | only CCS numbers / codes unavailable / no source (none occurred) |

`parks_only` marks bins whose only coded source is the Parks 2021 CCS table. That table is ICD-9 only, and its codes come from the AHRQ CCS assignment, not from authors defining the outcome.

Run: `.venv/bin/python 028_build_bins.py`.

## Results (27 bins)
**Every bin can be populated with ICD codes: 23 `explicit` and 4 `explicit_partial`.** How well each one is supported varies a lot:

| Support | Bins |
|---|---|
| **Several papers with author-defined codes, including ICD-10** | AMI (C1, 10 papers), IHD/coronary (C2, 11), heart failure (C3, 11), arrhythmia (C4, 8), stroke (C7, 7: mostly ischemic stroke), cerebrovascular (N4, 9), Parkinson's (N1, 5), dementia (N2, 7), pneumonia/respiratory infections (R4, 6), acute kidney failure (K1, 6: Lee 2023 AKI 584/N17), depression (N3: Qiu 2022) |
| **Author-defined codes, ICD-9 only** | COPD (R2), asthma (R1, only inside the cardiorespiratory composites of Yan 2021 / Burrows 2023), respiratory failure (R5: ARDS in Rhee 2020 is narrower), diabetes with complications (K3: Zanobetti 2014 "diabetes 250" is broader), UTI (I2: Yitshak-Sade's "559" is likely a typo for 599.0) |
| **Only the Parks CCS table (ICD-9, CCS-assigned)**; the other papers give CCS numbers only | Upper respiratory infections (R6), cardiac arrest (C5), blood clots (C8; Wei 2019 CCS 118), fluid and electrolyte disorders (K2; Wei 2019 / Weinberger 2021 / Bobb 2014 CCS 55), sepsis (I1; CCS 2), skin infections (I3; CCS 197), intestinal obstruction (I5) |
| **Only inside a broader group** (`explicit_partial`) | Bronchiectasis (R3: inside COPD/CCS 127, ICD-9 494), hypertensive heart disease (C6: ICD-9 402/404 inside Parks CCS 99, and inside Wei 2024's heart-failure list), retinal artery occlusion (C9: 362.3x inside Parks CCS 87, gray), Pneumocystis pneumonia (I4: 136.3 inside Parks CCS 122 Pneumonia) |

Observations:
- **The five rarest bins have no paper in the Step 2 set** that studies them: Pneumocystis, retinal artery occlusion, intestinal obstruction, cardiac arrest and hypertensive heart disease. Their codes exist here only because Parks published the full CCS → ICD-9 table. These bins probably come from outcome-wide studies outside this set, e.g. Wei 2019 BMJ-style CCS scans in other cohorts or other groups' papers.
- **ICD-10 is missing for 15 bins.** ICD-10 codes come only from the 2016+ cohort papers (Danesh Yazdi, Klompmaker, Shi, Wei 2024, Lee, Qiu, Spoto). The CCS-based bins have no ICD-10 at all. They would need CCSR (ICD-10) or a GEM crosswalk later.
- Ischemic and hemorrhagic stroke are studied separately (ischemic 433.x1/434.x1/436/I63; intracranial hemorrhage only as CCS 7.3.1.1). Only Parks CCS 109 combines them.

## Caveats
- The map is one reader's judgement, especially the `scope` labels; see the notes in `028_bins.json`.
- Populated does not mean validated. Definitions for the same bin often differ between papers (Step 2.7 shows how). Choosing and validating one ICD-9/ICD-10 list per bin is the next step.
- Parks is ICD-9 only, and a few of its printed codes look truncated (Step 2.6 `suspect_codes`).

## Outputs
| File | Purpose |
|---|---|
| `028_bins.json` | Hand map: bin → Step 2.6 outcome entries, scope, code filters, notes |
| `028_build_bins.py` | Builds the bin table |
| `028_bins_populated.json` | Per bin: status, flags, and every source with its codes, position and evidence location |
| `028_bins.csv` | **Review table**: one row per bin |
