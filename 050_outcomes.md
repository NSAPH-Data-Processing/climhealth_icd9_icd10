# Steps 5.1 to 5.6 — Outcomes for the foundation model

Input: `050_codesets.yaml`, which is not changed.

Run:
```
.venv/bin/python 052_download_lists.py
.venv/bin/python 051_runnable_criteria.py
.venv/bin/python 052_resolve_markers.py
.venv/bin/python 053_scan_codes.py
.venv/bin/python 053_apply_decisions.py
.venv/bin/python 054_icd_coverage.py
.venv/bin/python 055_remove_duplicates.py
.venv/bin/python 056_final_yaml.py
```

## Result
**`056_outcomes.yaml`: 79 outcomes from 57 papers, each with ICD-9 and ICD-10 codes.** 28 outcomes are shared by more than one paper. 23 have a `note`.

| Step | From | To |
|---|---|---|
| 5.2 Left out, no codes and no named definition | 105 code sets | 99 |
| 5.3 Four sets split in two | 99 | 103 |
| 5.5 Identical codes and criteria merged | 103 | 79 |

**Where the codes come from:**
| ICD-9 | ICD-10 | Outcomes |
|---|---|---|
| Printed | Printed | 30 |
| Printed | GEM | 29 |
| GEM | Printed | 8 |
| Official list | GEM | 6 |
| Official list | Official list | 3 |
| Official list | Another paper's pairing | 2 |
| Printed | Another paper's pairing | 1 |

An outcome counts as printed if any of its merged entries printed that version. Corrected typos count as printed. 12 sets were filled from a paper's pairing before merging.

**Criteria:** 56 principal diagnosis, 18 any diagnosis, 5 first 10 fields.

**Notes in the YAML** cover only the Step 5.3 decisions and assigned criteria. The source of every code and the GEM counts are in `055_outcomes.json`.

## Official lists
Machine-readable versions are in `official_lists/`. Raw files are in `official_lists/raw/` (git-ignored), and `official_lists/downloads.json` has the URLs, dates and checksums.

| List | File | Version |
|---|---|---|
| CCW ADRD | `ccw_adrd_27cc_2022.json` | 27 CCW conditions, revised 02/2022 |
| CCS | `ccs_icd9_2015.csv` | HCUP single-level CCS, 2015 |
| CCSR | `ccsr_icd10_v2023_1.csv` | HCUP CCSR v2023.1 |
| GEMs | `gem_2018_icd9_to_icd10.csv`, `gem_2018_icd10_to_icd9.csv` | CMS 2018 |

**CCW source.** The link cited by the papers is dead, and the current CCW document is a different version: 30 conditions, revised 08/2026, with no ICD-9 codes and Alzheimer's split from other dementias. So the list comes from the Internet Archive copy of the cited document. Its 24 ICD-9 and 22 ICD-10 codes are identical to the list printed by Klompmaker 2023, Mork 2023 and Qin 2025, so Delaney 2025 and the 2026 AJE paper merge with them.

## Step notes
**5.1.** `not stated` (12 sets) became principal diagnosis, except `cerebral_degenerations` and `dementia_no_codes`, which became the first 10 fields. `dementia_no_codes` then leaves in 5.2.
| Step 5 criteria | `criteria` | `outcome_criteria` | `first_n` |
|---|---|---|---|
| principal diagnosis | principal diagnosis | `first_n` | 1 |
| any of the first 10 diagnosis fields | same | `first_n` | 10 |
| any diagnosis; principal or secondary; up to 25 fields | any diagnosis | `all` | |

**5.2.** Left out: `cvd_no_codes_principal`, `cvd_no_codes_not_stated`, `cardiac_amyloidosis`, `dementia_vascular_no_codes`, `dementia_no_codes`, `fracture_osteoporosis_no_codes` (`052_left_out.json`).

**5.3.** `053_scan.json` is the pre-decision record: potential typos in the printed codes, and coverage in both directions for sets with both versions. Coverage is the share of GEM-mapped codes that fall inside the other version. It counts codes, not admissions. All decisions were made one by one with the user and are in `053_decisions.json`, with their evidence:

| Printed | Code set | Decision |
|---|---|---|
| `490-448`, `480-497` | `resp_printed_490_448` | Corrected to `490-492`, `480-487` (the cited Peng 2008) |
| `I163` | `stroke_ischemic_i163` | Corrected to `I63` |
| `559` | `uti_559` | Corrected to `5990` |
| `CCSR GEN001` | `uti_ccs_ccsr`, `nonresp_infection_ccs` | Corrected to `CCSR GEN004`; only v2023.1 was checked |
| `390 to 495` | `cvd_390_495` | Corrected to `390-459` |
| `332/332.0` | `parkinson_332_or_3320` | Ambiguous, read as `3320` |
| `390-429` | `cvd_390_429_*` | Kept; excludes stroke and blood vessel disease |
| `I64.x` | `cerebrovascular`, `cvd_composite_seven` | Kept; not in ICD-10-CM, so it matches no US claims |

**Coverage review.** Sets at 50% or below, in either direction, were reviewed:
| Set | Lowest overlap | Decision |
|---|---|---|
| `resp_infection_copd_asthma` | 17% | Split |
| `parkinson_332` | 25% | Split |
| `heat_illness` | 30% | Split |
| `adrd_shi` | 33% | Split |
| `resp_infection_copd_494` | 33% | Kept: the authors evaluated this conversion |
| `excessive_natural_heat` | 50% | Kept: rests on too few codes |

**5.4.** A pairing needs identical codes in the available version. 12 sets took a pairing, and 48 use GEMs, including the 8 split entries, which go straight to the GEMs. GEMs apply to every valid code in the set's ranges.

**5.5.** Codes are compared after expansion to valid codes, so `F04-F05` equals `F04` + `F05`. Some definitions that look different turn out to be the same: `cvd_heart_groups` equals `cvd_390_429`, and `parkinson_secondary_*` (3320, 3321) equals `parkinson_332_g21` (332).

## Points to keep in mind
- **Ranges are not exact codes.** `428` means every code under 428. Ranges and printed categories still go through the expander. Official and GEM codes are exact codes, which is why some lists are long: `nonresp_infection_ccs` has 2,968 codes and `heat_composite_ccs` 952.
- **GEM lists are narrower than printed ranges.** Injury codes in GEMs usually carry the initial-encounter 7th character only, such as `T670XXA`. Most GEM entries are also marked approximate. Jumps at October 2015 are most likely in these sets, and in sets pairing CCS with CCSR, which are different schemes.
- **Split sets carry side effects of the mapping.** For example, the GEM ICD-9 list of `heat_illness__icd10` includes `909.4` and `V58.89`. These are in its note.
- **Not checked:** whether the expander accepts these lists, and any count.

## Outputs
| File | Purpose |
|---|---|
| `052_download_lists.py`, `official_lists/` | Official lists, raw and machine-readable |
| `051_*`, `052_*`, `053_*`, `054_*`, `055_*` | Scripts and JSON for Steps 5.1 to 5.5, with the source of every code and any flags |
| `053_decisions.json` | **The Step 5.3 decisions and their evidence** |
| `052_left_out.json` | Sets left out in Step 5.2 |
| **`056_outcomes.yaml`** | **The final outcomes** |
