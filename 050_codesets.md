# Step 5 — Condensed code sets

Input: `026_icd_codes.json`, `036_icd_codes.json`, `042_icd_codes.json` and their exposure files. Run: `.venv/bin/python 050_build_codesets.py` → **`050_codesets.yaml`**.

Codes stay as printed here. Typos are decided with the user in Step 5.3. The final outcomes are in `056_outcomes.yaml` (see `050_outcomes.md`).

## Result
**105 code sets from 61 papers.** Of the 71 unique papers, 9 are on both Google Scholar lists and count once. 24 code sets are shared by more than one paper.

| Codes in the set | Code sets |
|---|---|
| ICD-9 and ICD-10 | 40 |
| ICD-9 only | 39 |
| ICD-10 only | 5 |
| CCS, CCSR or CCW marker, no ICD codes | 15 |
| None (ranges left empty) | 6 |

**An empty list means no code reference at all.** A marker such as `"CCW"`, `"CCS 157"` or `"CCSR GEN001"` in `icd9` or `icd10` means the paper names that definition but does not print its codes. Step 5.2 replaces markers with official codes.

## Format
Same as `francesca_claudio_icdranges01.yaml`, with these added fields:
- `long_name`: written by hand in `050_names.json`.
- `criteria`: free text, from the paper's diagnosis position, or `not stated`.
- `paper_id`: the paper folder names.
- `treatment`: the union over the set's papers, from `air_pollution`, `extreme_weather`, `long_term`, `short_term`.

Paper IDs are quoted, because YAML reads `10_1080_..._1722134` as an integer otherwise. The build reads the YAML back and stops if anything differs.

## How entries were condensed
1. **Each paper counts once**, by folder name. When a paper has entries in more than one step, the later step wins.
2. **Format choices, approved by the user** (`053_decisions.json`):
   - Dots and `·` are removed, `to` and dashes become `-`, and trailing wildcards are removed (`428.xx` → `428`).
   - Ranges side by side are joined (`410-414` + `415-417` → `410-417`). A range printed backwards is left as it is.
   - Wildcards in the middle of a code become the valid codes (`410.X0`, `410.X1`, `433.X1`, `434.X1`, `A37.X1`). `410.xx except 410.x2` is the same list as `410.X0` + `410.X1`.
   - Codes described in words are written as a range (`codes beginning with "I"` → `I00-I99`).
   - BMJ 2024's composite takes the combined codes of its seven subtypes.
3. **Two entries are one code set** when ICD-9, ICD-10 and criteria all match. The outcome name in the paper does not need to match.

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

Four papers have no outcomes in any step, for lack of a full text, so they have no entries here.

**CCS and CCW rule.** The question is whether the paper chose the outcome or iterated over a pool. Chosen outcomes stay, with their codes when printed and with a marker when not.

| Paper | CCS or CCW use | Here |
|---|---|---|
| Klompmaker 2023, Qin 2025, Mork 2023 | CCW, 24 ICD-9 + 22 ICD-10 printed | Codes |
| 2019 Environ Pollut, dementia | CCW, 20 ICD-9 printed | Codes |
| Delaney 2025, 2026 AJE (with ADRD) | CCW named, no codes | Marker |
| Weinberger 2021 | 7 heat-related CCS groups, no codes | Marker, in `icd9` |
| Spangler 2023 | Composite of 7 CCS groups, no codes | Marker, in `icd9` |
| 2024 Nat Commun, infections | CCS and CCSR groups, no codes | Marker |
| Hopp 2018 | 6 CCS categories, codes printed, same model per diagnosis | Left out |
| Wei 2019, Bobb 2014, Thomas 2022 | Scans of many CCS groups | Left out |
| AAAI 2025 | Heat alert methods paper; groups borrowed from Bobb 2014 | Left out |

Hopp 2018 starts from chosen CCS categories, but it fits the same model to each code in them, and the outcomes it highlights come from its results. Its codes are in its Supplemental Table S1.

## Points to keep in mind
- **`treatment` is a union.** A set can have all four values because of different papers. `050_treatment_by_paper.csv` gives the values per paper.
- **Empty `treatment`** means the paper's exposure is none of the listed ones (greenness, noise, policy, trends).
- **`criteria` covers the diagnosis position only.** "First hospitalization" or "second admission" is not recorded.

## Outputs
| File | Purpose |
|---|---|
| `050_build_codesets.py` | Normalizes format and condenses |
| `050_names.json` | Hand short and long names, and the CCS, CCSR and CCW markers |
| **`050_codesets.yaml`** | **The condensed code sets, as printed** |
| `050_left_out.json` | Entries left out, with reasons |
| `050_treatment_by_paper.csv` | `treatment` per code set and paper |
