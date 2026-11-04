# Step 6 — Bins over the final outcomes

Input: `056_outcomes.yaml`, `055_outcomes.json`, `060_bin_map.json`. Run: `.venv/bin/python 060_build_bins.py` → **`060_bins.yaml`**.

Bins are labels. They change no ICD codes.

## Result
**34 bins from the 79 outcomes.** 72 outcomes are in a bin's long-term or short-term list, and 7 are in neither (see below).

- **Both long-term and short-term:** 16 bins.
- **Long-term only:** valvular, cardiomyopathy, aortic aneurysm, ARDS, kidney and urinary composite, CKD, non-respiratory infections, CNS infections, intestinal infections.
- **Short-term only:** multiple sclerosis, depression, schizophrenia, bipolar, fluid and electrolyte, diabetes, heat-related illness, heat composite, fracture.

## How it works
- **`060_bin_map.json`** is the hand map from each bin to the code sets of `050_codesets.yaml`. The build stops if an outcome's code set has no bin.
- **An outcome is in the bin of every code set it was merged from.** `055_outcomes.json` records them in `from_codesets`. Both parts of a set split in Step 5.3 stay in that set's bin.
- **`long_term` and `short_term` come from each outcome's `treatment`.** An outcome studied both ways appears in both lists of its bin.
- **Bins come from the outcomes.** They start from the Step 2.8 bins, and a bin with no outcome in its lists is not written.

## Changes from the Step 2.8 bins
- **Merged:** the two stroke and cerebrovascular bins became `cerebrovascular`; diabetes with complications and all diabetes became `diabetes`; dehydration joined `fluid_electrolyte`.
- **Added:** `ischemic_stroke`, because several papers define it separately from all cerebrovascular disease.
- **Dropped, no outcome in the YAML:** asthma, bronchiectasis, upper respiratory infections, cardiac arrest, hypertensive heart disease, blood clots, retinal artery occlusion, skin infections, Pneumocystis pneumonia, intestinal obstruction, injuries and the outcome-wide bin.

## Outcomes in neither list
Their papers' exposure is none of the listed ones, so `treatment` is empty: `alzheimers_any`, `dementia_vascular`, `dementia_nonspecific`, `dementia_picks`, `neurocognitive`, `aki_any`, `pancreatic_cancer`.

`pancreatic_cancer` was the only member of its bin, so that bin is not written. `cardiac_amyloidosis` has no bin either, because its code set has no codes and left in Step 5.2.

## Points to keep in mind
- **A bin does not separate air pollution from extreme weather.** The format has only the two time lists. Each outcome's `treatment` shows which is which, and `050_treatment_by_paper.csv` gives the values per Step 5 code set and paper.
- **A shared outcome counts as one entry.** The list sizes show how many definitions exist, not how many papers support the bin.
- **Bins do not choose one definition.** `dementia` holds several outcomes with different codes and criteria.
- **Some bin memberships are judgement calls.** `cerebral_degenerations` (ICD-9 331) is in `dementia`, and `cvd_five_causes` and `cvd_390_429` are in `cvd_all`, although they do not cover all of 390-459.

## Outputs
| File | Purpose |
|---|---|
| `060_bin_map.json` | Hand map: bin → code sets |
| `060_build_bins.py` | Splits each bin into long-term and short-term |
| **`060_bins.yaml`** | **The bins** |
