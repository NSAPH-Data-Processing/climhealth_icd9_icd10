# Step 5 — Condensed code sets

Input: `026_icd_codes.json`, `036_icd_codes.json`, `042_icd_codes.json` and their exposure files. Run: `.venv/bin/python 050_build_codesets.py` → **`050_codesets.yaml`**.

## Result
**101 code sets from 61 papers.** Of the 71 unique papers, 9 are on both Google Scholar lists and count once. 24 code sets are shared by more than one paper.

| Codes in the set | Code sets |
|---|---|
| ICD-9 and ICD-10 | 38 |
| ICD-9 only | 37 |
| ICD-10 only | 5 |
| CCS, CCSR or CCW marker, no ICD codes | 15 |
| None (ranges left empty) | 6 |

**An empty list means no code reference at all.** A marker such as `"CCW"`, `"CCS 157"` or `"CCSR GEN001"` in `icd9` or `icd10` means the paper names that definition but does not print its codes. Markers are not ICD codes. The range expander has not been checked against them.

## Format
Same as `francesca_claudio_icdranges01.yaml`, with these added fields:
- `long_name`: written by hand in `050_names.json`.
- `criteria`: free text. `principal diagnosis`, `principal or secondary diagnosis`, `any diagnosis` or `not stated`, or the number of diagnosis fields when the paper states it (for example `any of the first 10 diagnosis fields`).
- `paper_id`: the paper folder names.
- `treatment`: the union over the set's papers, from `air_pollution`, `extreme_weather`, `long_term`, `short_term`.

Paper IDs are quoted, because YAML reads `10_1080_..._1722134` as an integer otherwise. The build reads the YAML back and stops if anything differs.

## How entries were condensed
1. **Each paper counts once**, by folder name. When a paper has entries in more than one step, the later step wins.
2. **Codes are normalized:** dots and `·` removed, `to` and dashes become `-`, trailing wildcards removed (`428.xx` → `428`), and contiguous ranges joined (`410-414` + `415-417` → `410-417`).
3. **Wildcards in the middle of a code are expanded to their valid codes:** `410.X0`, `410.X1`, `433.X1`, `434.X1`, `A37.X1`. `410.xx except 410.x2` becomes the same list as `410.X0` + `410.X1`.
4. **Two entries are one code set** when ICD-9, ICD-10 and criteria all match. The outcome name in the paper does not need to match, so `coronary heart disease` and `ischemic heart disease` merge when their codes do.

**Typos fixed** (`FIXES` in the script):
| Paper | Printed | Used | Why |
|---|---|---|---|
| 2013 J Expo Sci Environ Epidemiol | `490-448` | `490-492` | Cites Peng 2008, which prints 490-492 |
| 2013 J Expo Sci Environ Epidemiol | `480-497` | `480-487` | Cites Peng 2008, which prints 480-487 |
| deSouza 2021 Epidemiology | `390 to 495` | `390-459` | The CVD range; 460-495 is respiratory |
| 2021 Sci Total Environ | `559` | `5990` | 559 is not an ICD-9 category; UTI is 599.0 |
| 2 papers, 2025 | `I163` | `I63` | I63 in the group's other papers |
| Delaney 2026 Environ Epidemiol | `332/332.0` | `3320` | Ambiguous as printed; 332.0 is the Parkinson's code and pairs with G20 |

**Kept as printed, because they may be real choices:**
- `390-429` as "all CVD" (2 papers), and `all CVD` stopping at 429 (2021 Environ Int).
- `T67.3-T67.5` next to `992.0-992.9` (Jung 2025). The ICD-10 range is narrower than the ICD-9 range.

Codes printed as `codes beginning with "I"` or `"J"` are written as `I00-I99` or `J00-J99`.

## Left out
295 entries, listed with their reasons in `050_left_out.json`.

| Reason | Entries |
|---|---|
| Parks 2021 | 227 |
| Group-based (Bobb 2014, Thomas 2020 model groups, Thomas 2022, Hopp 2018's 50 diagnoses) | 23 |
| Scan of CCS groups, no explicit codes (Wei 2019 BMJ) | 18 |
| Not an outcome (component, control, exclusion, sensitivity, covariate, cohort) | 17 |
| Hopp 2018: the same model over each diagnosis in 6 CCS categories | 7 |
| By hand: amyloidosis component; AAAI 2025, which takes CCS groups from Bobb 2014; "without ADRD" in the 2026 AJE paper, which is every other hospitalization | 3 |

**CCS and CCW rule.** The question is whether the paper chose the outcome or iterated over a pool. Chosen outcomes stay, with their codes when printed and with a marker when not.

| Paper | CCS or CCW use | In the YAML |
|---|---|---|
| Klompmaker 2023 JAMA Netw Open | CCW, 24 ICD-9 + 22 ICD-10 printed | Codes: `adrd_ccw_prim_sec` |
| Qin 2025 AJE | CCW, same list printed | Codes: `adrd_ccw_any` |
| Mork 2023 Environ Int | CCW, same list printed | Codes: `adrd_ccw_first10` |
| 2019 Environ Pollut, dementia | CCW, 20 ICD-9 printed | Codes: `dementia_ccw_icd9` |
| Delaney 2025 JAMA Intern Med | CCW named, no codes | Marker: `adrd_ccw_unlisted_first10` |
| 2026 AJE, hospitalization with ADRD | CCW named, no codes | Marker: `adrd_ccw_unlisted_any` |
| Weinberger 2021 Environ Int | 7 heat-related CCS groups, no codes | Marker, 7 sets |
| Spangler 2023 Environ Epidemiol | Composite of 7 CCS groups, no codes | Marker, 1 set |
| 2024 Nat Commun, infections | CCS and CCSR groups, no codes | Marker, 5 sets |
| Hopp 2018 Prev Med | 6 CCS categories, codes printed, same model per diagnosis | No |
| Wei 2019 BMJ, Bobb 2014, Thomas 2022 | Scans of many CCS groups | No |
| AAAI 2025 | Heat alert methods paper; groups borrowed from Bobb 2014 | No |

**Judgement calls:**
- **Hopp 2018** drops out completely, including its 7 explicit sets (for example `heat_stroke`, which still has 2 other papers). It starts from chosen CCS categories, but it fits the same model to each code in them, and the outcomes it highlights come from its results. Its codes are in Supplemental Table S1 for the separate CCS work.
- **The CCW list is not copied into the marker entries.** Delaney 2025 and the 2026 AJE paper cite the 1999-2021 algorithm, and it is not confirmed that this matches the printed list.
- **Weinberger 2021 and Spangler 2023 have the CCS marker in `icd9` only**, because their labels record no CCSR or ICD-10 definition. CCS itself is an ICD-9 scheme, and whether these papers also cover ICD-10 years has not been checked.

## Points to keep in mind
- **ICD-9-only and ICD-9 + ICD-10 sets stay separate**, even when the ICD-9 codes match (`chf` and `chf_icd9`). No ICD-10 codes were inferred. Many of these papers ended before ICD-10 began.
- **`treatment` is a union.** `parkinson_3320` has all four values because one paper is long-term air pollution and the other is short-term heat, not because either paper studies all four. `050_treatment_by_paper.csv` gives the values per paper.
- **Empty `treatment`** means the paper's exposure is none of the listed ones (greenness, noise, policy, trends). Its `long_term` flag is not carried over, because there is no exposure to attach it to.
- **`criteria` covers the diagnosis position only.** "First hospitalization" or "second admission" is not recorded, so `mi_acute` includes a paper on second admissions.
- **Ranges are not exact codes.** `medpar_outcomes/src/get_outcomes.py` uses an exact match, so this YAML needs the range expander before it runs. Sets with an empty list or a marker also need handling there.
- **Papers not in the YAML for lack of a full text:** 4 papers have no outcomes in any step (`050_left_out.json` does not list them, because they have no entries).

## Outputs
| File | Purpose |
|---|---|
| `050_build_codesets.py` | Normalizes, fixes typos and condenses |
| `050_names.json` | Hand short and long names, and the CCS, CCSR and CCW markers |
| **`050_codesets.yaml`** | **The condensed code sets** |
| `050_left_out.json` | Entries left out, with reasons |
| `050_treatment_by_paper.csv` | `treatment` per code set and paper |
