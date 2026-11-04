# Step 6 — Outcomes for the foundation model

Input: `050_codesets.yaml`, `051_bin_map.json`. Step 5 and 5.1 files are not changed.

Run:
```
.venv/bin/python 060_download_lists.py
.venv/bin/python 061_runnable_criteria.py
.venv/bin/python 062_resolve_markers.py
.venv/bin/python 063_icd_coverage.py
.venv/bin/python 064_remove_duplicates.py
.venv/bin/python 065_final_yaml.py
.venv/bin/python 066_update_bins.py
```

## Result
**`065_outcomes.yaml`: 77 outcomes from 57 papers, each with ICD-9 and ICD-10 codes.** 28 outcomes are shared by more than one paper. 53 have a `note`. **`066_bins.yaml`** has 34 bins.

| Step | From | To |
|---|---|---|
| 6.2 Left out, no codes and no named definition | 101 code sets | 95 |
| 6.3 Different pairings give separate entries | 95 | 96 |
| 6.4 Identical codes and criteria merged | 96 | 77 |

**Where the codes come from:**
| ICD-9 | ICD-10 | Outcomes |
|---|---|---|
| Printed | Printed | 34 |
| Printed | GEM | 25 |
| Official list | GEM | 6 |
| GEM | Printed | 5 |
| Official list | Official list | 3 |
| Printed | Another paper's pairing | 2 |
| Official list | Another paper's pairing | 2 |

An outcome counts as printed if any of its merged entries printed that version. Merged sets also use pairings, so more than these 4 sets were filled from a paper: 12 before merging.

**Criteria:** 56 principal diagnosis, 16 any diagnosis, 5 first 10 fields.

## Official lists
Machine-readable versions are in `official_lists/`. Raw files are in `official_lists/raw/` (git-ignored), and `official_lists/downloads.json` has the URLs, dates and checksums.

| List | File | Version |
|---|---|---|
| CCW ADRD | `ccw_adrd_27cc_2022.json` | 27 CCW conditions, revised 02/2022 |
| CCS | `ccs_icd9_2015.csv` | HCUP single-level CCS, 2015 |
| CCSR | `ccsr_icd10_v2023_1.csv` | HCUP CCSR v2023.1 |
| GEMs | `gem_2018_icd9_to_icd10.csv`, `gem_2018_icd10_to_icd9.csv` | CMS 2018, the file with both directions and flags |

**CCW source.** The link cited by the papers is dead, and the current CCW document is a different version: 30 conditions, revised 08/2026, with no ICD-9 codes and Alzheimer's split from other dementias. So the list comes from the Internet Archive copy of the cited document. Its 24 ICD-9 and 22 ICD-10 codes are identical to the list printed by Klompmaker 2023, Mork 2023 and Qin 2025, so Delaney 2025 and the 2026 AJE paper merge with them.

## Step notes
**6.1.** Translated as follows. `not stated` (12 sets) became principal diagnosis, except `cerebral_degenerations` and `dementia_no_codes`, which became the first 10 fields. `dementia_no_codes` then leaves in 6.2.
| Step 5 criteria | `criteria` | `outcome_criteria` | `first_n` |
|---|---|---|---|
| principal diagnosis | principal diagnosis | `first_n` | 1 |
| any of the first 10 diagnosis fields | same | `first_n` | 10 |
| any diagnosis; principal or secondary; up to 25 fields | any diagnosis | `all` | |

**6.2.** Left out: `cvd_no_codes_principal`, `cvd_no_codes_not_stated`, `cardiac_amyloidosis`, `dementia_vascular_no_codes`, `dementia_no_codes`, `fracture_osteoporosis_no_codes` (`062_left_out.json`).

**Typo corrected.** The 2024 Nat Commun infections paper prints CCSR `GEN001` for urinary tract infection. In the CCSR table, `GEN001` is nephritis and UTI codes such as N39.0 are `GEN004`. With `GEN001`, only 6% of the mapped codes overlapped with CCS 159. It is read as `GEN004` in `uti_ccs` and `nonresp_infection_ccs`, with a note on both. Only CCSR v2023.1 was checked, so an older version numbering is not ruled out.

**Typos in the notes.** The final YAML notes also list the 7 corrections made in Step 5, so every corrected code can be seen on its outcome. No typos were fixed before Step 5.

**6.3.** A pairing needs identical codes in the available version. 38 sets had no pairing and use GEMs, which were applied to every valid code in the set's ranges, in the direction from the available version.
- **Flagged for review (32 outcomes):** those with approximate, one-to-many or unmapped GEM codes. The counts are in each `note`. Most GEM entries are marked approximate, so this flag is common and does not separate good mappings from bad ones.
- **Flagged for coverage (10 outcomes):** the two versions overlap by less than 70% when passed through the GEMs, in either direction: `resp_infection_copd_494`, `resp_infection_copd_asthma`, `pneumonia_broad`, `parkinson_332_first10`, `parkinson_332_principal`, `adrd_shi`, `heat_illness`, `excessive_natural_heat`, `septicemia_ccs`, `uti_ccs`. The 70% threshold is a choice made here. GEM-filled sets are not checked, because they agree by construction.

**6.4.** Codes are compared after expansion to valid codes, so `F04-F05` equals `F04` + `F05`. Some definitions that looked different in Step 5 turn out to be the same:
- `cvd_heart_groups` equals `cvd_390_429`.
- `parkinson_secondary_*` (3320, 3321) equals `parkinson_332_g21` (332), since 332.0 and 332.1 are all of 332.

**6.6.** Regenerated from `051_bin_map.json`. An outcome merged from code sets in several bins is in each of them. Seven outcomes are in neither list because `treatment` is empty: `alzheimers_any`, `dementia_vascular`, `dementia_nonspecific`, `dementia_picks`, `neurocognitive`, `aki_any`, `pancreatic_cancer`.

## Points to keep in mind
- **Ranges are not exact codes.** `428` means every code under 428. Ranges and printed categories still go through your expander. Official and GEM codes are exact codes, which is why some lists are long: `nonresp_infection_ccs` has 2,968 codes and `heat_composite_ccs` 952.
- **Printed ranges and GEM lists are not equally broad.** A printed range includes rarely used codes, and a GEM list has only what the ICD-9 codes map to. Injury codes in GEMs usually carry the initial-encounter 7th character only, which matters for `hip_fracture` and `heat_external_ccs`.
- **CCS and CCSR are different schemes.** Pairing `septicemia_ccs` and `uti_ccs` across them gives a coverage flag. Jumps at October 2015 are most likely here and in the GEM-filled sets.
- **`first_n` versus position.** "Principal or secondary" runs as `all`, even where a paper may have limited the fields. Papers stating the first 10 fields keep `first_n: 10`.
- **Not checked:** whether the expander accepts these lists, and any count. The recommended checks after the counts are generated still apply.

## Outputs
| File | Purpose |
|---|---|
| `060_download_lists.py`, `official_lists/` | Official lists, raw and machine-readable |
| `061_*`, `062_*`, `063_*`, `064_*` | Scripts and JSON for Steps 6.1 to 6.4, with the source of every code and any flags |
| `062_left_out.json` | Sets left out in Step 6.2 |
| **`065_outcomes.yaml`** | **The final outcomes** |
| **`066_bins.yaml`** | **The bins, with the final short names** |
