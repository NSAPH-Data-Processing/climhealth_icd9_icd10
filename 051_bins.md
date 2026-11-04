# Step 5.1 — Bins over the condensed code sets

Input: `050_codesets.yaml`. Run: `.venv/bin/python 051_build_bins.py` → **`051_bins.yaml`**.

## Result
**34 bins from the 101 code sets.** 88 code sets are in a bin's long-term or short-term list, and 13 are in neither (see below).

- **Both long-term and short-term:** 17 bins.
- **Long-term only:** valvular, cardiomyopathy, aortic aneurysm, ARDS, kidney and urinary composite, CKD, non-respiratory infections, CNS infections, intestinal infections.
- **Short-term only:** multiple sclerosis, depression, schizophrenia, bipolar, fluid and electrolyte, diabetes, heat-related illness, heat composite.

## How it works
- **`051_bin_map.json`** is the hand map. Each code set belongs to exactly one bin, and the build stops otherwise.
- **`long_term` and `short_term` come from each code set's `treatment`.** A code set studied both ways appears in both lists of its bin.
- **Bins come from the code sets.** They start from the Step 2.8 bins, and a bin with no code set in the YAML is not kept.

## Changes from the Step 2.8 bins
- **Merged:** the two stroke and cerebrovascular bins became `cerebrovascular`; diabetes with complications and all diabetes became `diabetes`; dehydration joined `fluid_electrolyte`.
- **Added:** `ischemic_stroke`, because several papers define it separately from all cerebrovascular disease.
- **Dropped, no code set in the YAML:** asthma, bronchiectasis, upper respiratory infections, cardiac arrest, hypertensive heart disease, blood clots, retinal artery occlusion, skin infections, Pneumocystis pneumonia, intestinal obstruction, injuries and the outcome-wide bin. Most of these came from Parks 2021 or other CCS scans, so the separate CCS work may bring them back.

## Code sets in neither list
Their papers' exposure is none of the listed ones, so `treatment` is empty.

| Code sets | Exposure |
|---|---|
| `parkinson_secondary_prim_sec`, `parkinson_secondary_any`, `adrd_ccw_prim_sec`, `aki_prim_sec` | Greenness, parks, blue space |
| `mi_acute_icd9` | Smoking bans; geographic trends |
| `adrd_ccw_unlisted_any` | Region and race |
| `alzheimers_icd10`, `dementia_vascular_icd10`, `dementia_nonspecific_icd10`, `dementia_picks_icd10`, `neurocognitive_icd10` | Dementia coding |
| `pancreatic_cancer`, `cardiac_amyloidosis` | Trends |

The last two were the only members of their bins, so those bins are not written. The map keeps them, so they return if the exposure rule changes.

## Points to keep in mind
- **A bin does not separate air pollution from extreme weather.** The format has only the two time lists. `cvd_all` long-term, for example, includes air pollution and long-term temperature papers. Each code set's `treatment` and `050_treatment_by_paper.csv` show which is which.
- **A shared code set counts as one entry.** The list sizes show how many definitions exist, not how many papers support the bin. `cvd_all` has 3 long-term code sets, but one of them has 6 papers.
- **Bins do not choose one definition.** `dementia` holds 10 listed code sets with different codes and criteria.
- **Some bin memberships are judgement calls.** `cerebral_degenerations` (ICD-9 331) is in `dementia`, and `cvd_five_causes` and the `390-429` sets are in `cvd_all`, although they do not cover all of 390-459.

## Outputs
| File | Purpose |
|---|---|
| `051_bin_map.json` | Hand map: bin → code sets |
| `051_build_bins.py` | Splits each bin into long-term and short-term |
| **`051_bins.yaml`** | **The bins** |
