# Step 2.8 — Outcome bins for the Step 2.6 code sets, with exposure attributes

**Rewritten on 2026-10-26.** The first version treated the CLAUDE.md list as a checklist. Bins are now **our own classification** of every Step 2.6 code set:
- the 27 reference bins, plus **22 added bins** for outcomes that appear in the papers but not on the list;
- every code set is tagged with the paper's **exposure**: air pollution, extreme heat or extreme weather, and long-term or short-term.

## Method
1. **Exposure per paper** → `028_exposures.json` (hand-labeled from the methods of the 51 full-text papers). Each paper gets these attributes:
   - `air_pollution`, `extreme_heat`, `extreme_weather`;
   - `long_term`, `short_term`: from the study design, e.g. annual or multi-year averages vs. daily lags, event days or drought periods;
   - `other_exposure`: the exposure, when it is none of the above (e.g. greenness, noise, policy);
   - a short `note`.

   Decisions (confirmed with the user):
   - **Wildfire smoke** = `air_pollution` + `extreme_weather`.
   - **Long-term average climate** (summer/winter temperature, specific humidity) = `extreme_heat` + `long_term`.
   - **Greenness, parks, blue space, aircraft noise, industry proximity** = `other_exposure` only.
   - **Air-quality policies** (NAAQS nonattainment, Clean Air Act) = `air_pollution` + `long_term` + `other_exposure` (policy).
   - **Heat-alert papers** = `extreme_heat` + `short_term` + `other_exposure` (policy).
   - **Trends and coding papers** (pancreatic cancer, MI geography, amyloidosis, dementia coding) = `other_exposure`, with no time flags.
2. **Bins** → `028_bins.json` (hand). Every code set is assigned to one or more bins, with a scope:
   - `exact`;
   - `narrower`: the code set is part of the bin;
   - `broader`: the code set is the bin plus other conditions. An optional ICD-9 filter picks the bin's codes inside it.

   Parks 2021 contributes its CCS groups where they define a bin. Its 13 broad causes go to the composite bins, and the rest go to `W1`.
3. **`028_build_bins.py`** → `028_bins_populated.json` and **`028_bins.csv`**:
   - **Bin exposure attributes** are the union over the papers of its `exact` and `narrower` sources. `broader` sources studied a larger group, so they do not count.
   - **`support`** lists the papers for each exposure × term, e.g. `air_pollution_long_term`.
   - **Coverage check:** every author-defined (explicit) code set with role `outcome` must be in a bin. **All are** (`unbinned_code_sets` is empty).

Run: `.venv/bin/python 028_build_bins.py`. The first version of the map is kept at `.cache/028_bins_v1.json` (not committed).

## Bins (49: 27 reference + 22 added)
**How to read the table:**
- The exposure columns give the number of papers: `L` = long-term, `S` = short-term.
- "other" = papers with other exposures.
- ICD-10 ✓ = at least one coded source gives ICD-10 codes.
- Status: `explicit` = an exact code set with ICD codes; `explicit_partial` = codes only from broader or narrower sets; `no_codes` = sources exist, but their codes are not available.

| id | bin | origin | status | air pollution | extreme heat | extreme weather | long-term | short-term | other | ICD-10 |
|---|---|---|---|---|---|---|---|---|---|---|
| R0 | All respiratory disease (composite) | added | explicit | L1 S7 | L1 | S5 | ✓ | ✓ | 1 | ✓ |
| R1 | Asthma exacerbations | reference | explicit |  |  | S1 |  | ✓ |  |  |
| R2 | COPD exacerbations | reference | explicit | L1 S2 |  | S1 | ✓ | ✓ | 1 |  |
| R3 | Bronchiectasis | reference | explicit_partial |  |  |  |  |  |  |  |
| R4 | Pneumonia and other respiratory infections (incl. influenza) | reference | explicit | L2 S4 |  | S1 | ✓ | ✓ | 1 | ✓ |
| R5 | Respiratory failure, insufficiency, or arrest (incl. ARDS) | reference | explicit | S1 |  | S1 | ✓ | ✓ | 1 |  |
| R6 | Upper respiratory infections (and acute bronchitis) | reference | explicit |  |  | S1 |  | ✓ |  |  |
| C0 | All cardiovascular disease (composite) | added | explicit | L5 S10 | L3 S1 | S5 | ✓ | ✓ | 3 | ✓ |
| C1 | Heart attack (acute myocardial infarction) | reference | explicit | L5 S3 | L2 | S1 | ✓ | ✓ | 1 | ✓ |
| C2 | Ischemic heart disease and coronary atherosclerosis | reference | explicit | L3 S4 | L2 | S1 | ✓ | ✓ | 2 | ✓ |
| C3 | Heart failure | reference | explicit | L3 S5 | S1 | S1 | ✓ | ✓ | 2 | ✓ |
| C4 | Abnormal heart rhythms (arrhythmias/dysrhythmias) | reference | explicit | L4 S2 |  | S1 | ✓ | ✓ | 2 | ✓ |
| C5 | Cardiac arrest | reference | explicit |  |  | S1 |  | ✓ |  |  |
| C6 | Hypertensive heart disease | reference | explicit_partial | L1 |  |  | ✓ |  |  | ✓ |
| C7 | Stroke, including ischemic and hemorrhagic stroke | reference | explicit | L4 S2 | L2 | S1 | ✓ | ✓ |  | ✓ |
| C8 | Blood clots: phlebitis, thrombophlebitis, and thromboembolism | reference | explicit | S1 |  | S1 |  | ✓ |  |  |
| C9 | Retinal artery occlusion | reference | explicit_partial |  |  |  |  |  |  |  |
| C10 | Peripheral vascular disease and atherosclerosis | added | explicit | L1 S1 | S1 | S1 | ✓ | ✓ | 3 |  |
| C11 | Cardiomyopathy | added | explicit | L1 |  |  | ✓ |  |  | ✓ |
| C12 | Valvular heart disease | added | explicit | L1 |  | S1 | ✓ | ✓ |  | ✓ |
| C13 | Aortic and other arterial aneurysms | added | explicit | L1 S2 |  | S1 | ✓ | ✓ |  | ✓ |
| C14 | Cardiac amyloidosis | added | no_codes |  |  |  |  |  | 1 |  |
| N1 | Parkinson's disease | reference | explicit | L1 S2 |  | S1 | ✓ | ✓ | 1 | ✓ |
| N2 | Dementia, including Alzheimer's disease | reference | explicit | L3 S1 |  |  | ✓ | ✓ | 3 | ✓ |
| N3 | Depression and mood disorders | reference | explicit | S1 | S1 |  |  | ✓ |  | ✓ |
| N4 | Stroke and other cerebrovascular conditions | reference | explicit | L3 S2 | L2 | S1 | ✓ | ✓ | 2 | ✓ |
| N5 | Multiple sclerosis | added | explicit | S1 |  | S1 |  | ✓ |  |  |
| N6 | Schizophrenia and other psychotic disorders | added | explicit | S1 | S1 | S1 |  | ✓ |  | ✓ |
| N7 | Bipolar disorder | added | explicit | S1 | S1 |  |  | ✓ |  | ✓ |
| K0 | Kidney and urinary system diseases (composite) | added | explicit | L1 |  |  | ✓ |  |  | ✓ |
| K1 | Acute or unspecified kidney failure | reference | explicit | L1 S1 | S3 | S1 | ✓ | ✓ | 1 | ✓ |
| K2 | Fluid and electrolyte disorders (incl. dehydration) | reference | explicit | S1 | S3 | S1 |  | ✓ | 1 |  |
| K3 | Diabetes with complications | reference | explicit | S1 | S1 | S1 |  | ✓ | 1 |  |
| K4 | Chronic kidney disease | added | explicit | L1 |  | S1 | ✓ | ✓ |  | ✓ |
| K5 | Diabetes mellitus (all) | added | explicit | S1 |  | S1 |  | ✓ |  |  |
| H1 | Heat-related illness (heat stroke, heat exhaustion, effects of heat) | added | explicit_partial |  | S3 |  |  | ✓ |  |  |
| H2 | Heat-sensitive admissions composite (CCS 2, 50, 55, 114, 157, 159, 244) | added | classification |  | S2 |  |  | ✓ | 1 |  |
| I0 | Non-respiratory infections (composite) | added | explicit_partial | L1 |  |  | ✓ |  |  |  |
| I1 | Sepsis/septicemia | reference | explicit | L1 S1 | S2 | S1 | ✓ | ✓ | 1 |  |
| I2 | Urinary tract infections | reference | explicit | L1 S2 | S2 | S1 | ✓ | ✓ | 1 |  |
| I3 | Skin and soft-tissue infections | reference | explicit | S1 |  | S1 |  | ✓ |  |  |
| I4 | Pneumocystis pneumonia | reference | explicit_partial |  |  |  |  |  |  |  |
| I5 | Intestinal obstruction | reference | explicit |  |  | S1 |  | ✓ |  |  |
| I6 | Central nervous system infections | added | explicit_partial | L1 |  | S1 | ✓ | ✓ |  |  |
| I7 | Intestinal infections | added | explicit | L1 |  | S1 | ✓ | ✓ |  |  |
| X1 | Injuries | added | explicit |  |  | S1 |  | ✓ |  |  |
| X2 | Fractures (incl. hip and osteoporosis-related) | added | explicit_partial | L1 S1 |  | S1 | ✓ | ✓ |  |  |
| O1 | Pancreatic cancer | added | explicit |  |  | S1 |  | ✓ | 1 |  |
| W1 | Outcome-wide scans of all disease groups | added | explicit_partial | S1 | S2 | S1 |  | ✓ |  |  |

## Summary
- **Status:**
  - 38 bins are `explicit`.
  - 9 are `explicit_partial`: bronchiectasis, hypertensive heart disease, retinal artery occlusion, heat-related illness, Pneumocystis, CNS infections, fractures, non-respiratory infections, and the outcome-wide `W1`.
  - 1 is `no_codes`: cardiac amyloidosis.
  - 1 is `classification`: the heat-sensitive CCS composite `H2`.
- **Bins supported by long-term air pollution studies:**
  - all CVD and all respiratory;
  - AMI, IHD, heart failure, arrhythmia, stroke and cerebrovascular disease;
  - Parkinson's and dementia;
  - pneumonia and COPD;
  - acute kidney failure, CKD and kidney/urinary disease;
  - cardiomyopathy, valvular disease and aneurysm;
  - sepsis, UTI, non-respiratory/CNS/intestinal infections;
  - fractures and hypertensive heart disease.
- **Bins supported by short-term air pollution studies:** most of the cardiorespiratory bins, plus Parkinson's, dementia, diabetes, MS, the psychiatric bins, and the Wei 2019 CCS groups (sepsis, fluid/electrolyte, renal failure, UTI, skin infections, blood clots).
- **Bins supported by extreme heat:**
  - short-term (heat waves): heat-related illness, fluid/electrolyte, acute kidney failure, sepsis, UTI, diabetes with complications, peripheral vascular, heart failure, the psychiatric bins, and all CVD;
  - long-term (climate): all CVD, IHD, stroke/cerebrovascular, AMI, all respiratory.
- **Bins supported by extreme weather:**
  - tropical cyclones (Parks 2021: every CCS group, so most bins; Yan 2021; Burrows 2023), drought and wildfire, all short-term;
  - asthma, upper respiratory infections, cardiac arrest and intestinal obstruction are supported **only** by Parks 2021 (cyclones).
- **No exposure study at all:** bronchiectasis, retinal artery occlusion and Pneumocystis. Their only source is a broader Parks group.
- **Only trend or other papers:** cardiac amyloidosis, and pancreatic cancer (apart from Parks). These are candidates to drop from a pollution/weather list.

## Caveats
- Exposure classification, bin assignment and scope are one reader's judgement. All of it is in `028_exposures.json` and `028_bins.json`.
- **Parks 2021 marks many bins as extreme-weather (short-term) supported**, because it tested every CCS group. Support from a single outcome-wide scan is weaker than a dedicated study.
- Bins classify code sets; they do not yet choose one validated code list. Definitions inside a bin often differ (Step 2.7).

## Outputs
| File | Purpose |
|---|---|
| `028_exposures.json` | Hand exposure attributes for the 51 Step 2.6 papers |
| `028_bins.json` | Hand bin definitions and the code set → bin map |
| `028_build_bins.py` | Builds the bins with exposure attributes and the coverage check |
| `028_bins_populated.json` | Per bin: attributes, `support`, status and sources (codes, evidence, exposure) |
| `028_bins.csv` | **Review table**: one row per bin |
