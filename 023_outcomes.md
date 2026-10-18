# Step 2.3 — Does each publication use CMS Medicare outcomes beyond mortality and all-cause hospitalization?

Input: `022_abstracts.json`. Records with a null or flagged abstract are not classified (`outcome: null`).

## Definitions (decisions)
- **`uses_medicare`** is True when the study analyzes CMS Medicare data. That covers fee-for-service Part A / MedPAR claims, the Medicare denominator file, MCBS, and SEER-Medicare.
  - **Medicaid-only studies are False** (CMS data, but not Medicare). This is stated in `note`.
  - Studies that use Medicaid **plus a Medicare comparison group** are True.
  - The commercial + **Medicare Advantage** claims database (2 BMJ papers) is True but `uncertain`, because those are not CMS fee-for-service claims.
  - The 1987 National Medical Expenditure Survey (AHRQ) is False, `uncertain`.
- **`outcome`** is True when the study's **outcome** is a Medicare-defined event other than all-cause mortality or all-cause hospitalization. Examples are cause-specific hospitalizations or ED visits (CVD, respiratory, ADRD, kidney, heat stroke, …), first admission with a diagnosis, disease-group outcome-wide scans (214/283/432 ICD-9 groups), cause-specific incidence, and postoperative complications.
  - Outcomes that are **not** True: all-cause mortality, life expectancy, all-cause hospitalization, all-cause readmission, overall survival, costs/utilization.
- **`cohort_names`** is a separate field for outcomes that are all-cause but **measured in a cohort defined by diagnosis codes**. Examples are 30-day readmission after an ADRD admission, HRRP readmission after AMI/CHF/pneumonia, and survival in SEER-Medicare glioblastoma. These have `outcome: False` but may still matter for the ICD-mapping check (28 papers).
- **`uncertain`** is True when the abstract does not show the data source or does not name the outcome. Examples are "deaths and hospitalizations among Medicare enrollees", HEI report summaries, and Medicare studies that never say "Medicare".

## Method
1. **`023_prefilter.py`** → `023_candidates.json`. This takes the usable abstracts (476 − 13 flagged = 463 records), deduplicates them **by DOI** into **430 unique papers**, and screens each title and abstract:
   - `medicare` (182): mentions Medicare, CMS, Medicaid, MedPAR, fee-for-service, or beneficiaries
   - `older_adult` (24): no Medicare term, but mentions older adults, the elderly, or age 65+
   - `none` (224): neither of these. Coded False/False (`label_source: keyword_rule`).
2. **Hand labels** → `023_labels.json`. Claude read the **title + full abstract** of all 206 `medicare`/`older_adult` papers and recorded `uses_medicare`, `outcome`, `outcome_names`, `cohort_names`, `uncertain`, an `evidence_phrase`, and a `note`.
3. **Check of the keyword rule.** The 224 `none` papers were searched for hospitalization/admission/claims terms. That flagged 22, and their abstracts were read. **7 are Medicare studies that never say "Medicare"**, identified from the group's matching designs: the same county sets and the MCAPS 1999–2005 period. They were hand-labeled with `override_keyword_rule: true` → `label_source: hand_override`, all `uncertain: True`. The other 15 stay False. They use NY SPARCS, a single Baltimore hospital, managed care or commercial claims, Brazil COVID data, or reviews.
4. **`023_build_outcomes.py`** → `023_outcomes.json`. One record per Scholar publication (687). Duplicates inherit their paper's label. `evidence` is the **full sentence from the abstract** that contains the evidence phrase. The script verifies each phrase is found; all 213 were found.

Run: `.venv/bin/python 023_prefilter.py && .venv/bin/python 023_build_outcomes.py`. The labels in `023_labels.json` are the hand-made input. Re-running only re-applies them.

## Results (unique papers, n = 430 with usable abstract)
| | n |
|---|---|
| `uses_medicare` True | **188** |
| `outcome` True | **107** (17 uncertain), 95 of them dated 2011+ |
| Medicare, but only mortality / all-cause outcomes | 81 (28 of these have an ICD-defined `cohort_names`) |
| No Medicare | 242 (217 by the keyword rule + 25 hand-labeled) |
| `uncertain` total | 31 |

By Scholar record (687): `outcome` True 116, False 347, **null 224** (no usable abstract).

The most common outcome names are respiratory, cardiovascular / CVD, MI, heart failure, ischemic heart disease, cerebrovascular, Parkinson's, fluid & electrolyte disorders, heat stroke, pneumonia, COPD, ischemic stroke, and CKD/AKI.

## Caveats
- Labels come from **abstracts only**. A paper whose abstract reports only mortality may still analyze other outcomes in its body or supplement. The reverse can also happen.
- `uncertain` papers (31) and `hand_override` papers (7 records) are where a human check matters most.
- The 224 records with `outcome: null` are mostly Scholar artifacts, but some are real papers whose abstract could not be found (see Step 2.2: 27 with a DOI or title match but no abstract).
- This was a single reader (Claude), with no second annotator. Each label's `evidence` sentence makes spot-checking quick.

## Outputs
| File | Purpose |
|---|---|
| `023_prefilter.py` | Deduplicates and screens papers → `023_candidates.json` |
| `023_candidates.json` | 430 unique papers with `screen` and `duplicate_ids` |
| `023_labels.json` | 213 hand labels (206 screened + 7 overrides), keyed by DOI (or Scholar id) |
| `023_build_outcomes.py` | Merges everything → `023_outcomes.json` |
| `023_outcomes.json` | One record per Scholar publication: `uses_medicare, outcome, outcome_names, cohort_names, uncertain, evidence, label_source, note` |

## Carry forward
- The `outcome: True` papers (107) are the set whose ICD definitions should be compared against the Step 1 mappings (`010_icd_mappings.json`). The `outcome_names` give the comparison keys.
- `cohort_names` papers (28) can be added if cohort-defining codes count as part of the check.
