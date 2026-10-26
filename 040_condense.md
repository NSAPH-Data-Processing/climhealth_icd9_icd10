# Step 4 — Condense Steps 2 (Dominici) and 3 (Braun) into one set

Each paper is counted once: papers in both Scholar profiles are merged by DOI slug. Outputs are prefixed `040_`. The files are built in substeps, and each substep is committed separately.

## 4a. Papers and outcomes
Run: `.venv/bin/python 040_build_papers.py` → **`040_papers.json`**, **`040_outcomes.json`**.

**Inputs:**
- the Step 2.4 and 3.4 manifests;
- the Step 2.6 and 3.6 code records;
- the Step 2.8 and 3.8 exposure classifications.

**How shared papers are merged:** for papers in both sets, the Step 3 record is used, because Step 3 is the newer run. For example, Qin 2025 now has an open-access PDF, and the Step 2 record keeps that change in `fulltext_status_step24`. The codes and exposure labels in the shared records are identical, since Step 3 reused them.

**`040_papers.json`** has one record per paper in scope: Medicare papers whose outcomes are Medicare inpatient hospitalizations other than mortality or all-cause (Steps 2.3–2.4 and 3.3–3.4).
- **Fields:**
  - ids, label, year, title;
  - `in_dominici_scholar` / `in_braun_scholar`;
  - full-text status and source, missing supplements;
  - `medpar_or_ffs` and `data_source` with evidence;
  - `outcome_wide_scan`, set for Parks 2021, Wei 2019, Bobb 2014 and Hopp 2018;
  - `exposure`, with `air_pollution`, `extreme_heat`, `extreme_weather`, `long_term`, `short_term`, `other_exposure`, `note`, and `source`;
  - outcome counts.
- **Exposure source:** `full text` for the 58 papers with full text (Steps 2.8 and 3.8). For the 13 papers without full text, it is hand-labeled from the title and abstract (`source: abstract`, `NO_FULLTEXT` in the script).
- **New labels:** Peng 2009 JRSS-C, Chang 2011 Biostatistics, Levy 2012 AJE, and the HEI 2016 report.

**`040_outcomes.json`** has one record per (paper, outcome):
- **Full-text papers:** all Step 2.6/3.6 entries, including the 227 Parks CCS entries.
- **Papers without full text:** their Step 2.3/3.3 outcome names, with `codes_status: no_fulltext`.
- **Fields:**
  - `codes_status`, `classification`, `role`;
  - `has_icd_codes`;
  - `flags`, copied from the paper's exposure;
  - `outcome_wide_scan`.
- **IDs:** `slug::outcome name`, except Parks CCS groups, which use `slug::ccs-l<level>-<group>`. Two Parks groups share a printed name: the supplement labels **CCS 58** "Other disorders of stomach and duodenum" (as for CCS 141), even though its codes are 270–279 (nutritional and metabolic disorders). The label is kept as printed.

**Results:**
- **Papers: 71.** 54 are Dominici only, 8 Braun only, and 9 are in both. 58 have full text.
- **Exposure:** 43 papers study air pollution, 15 extreme heat, and 5 extreme weather. 30 are long-term and 36 short-term. 17 have another exposure (greenness, noise, policy, trends).
- **Outcomes: 439.**
  - 351 `explicit_codes` (227 of them Parks CCS groups);
  - 47 `classification_ref`;
  - 12 `in_unfetched_supplement`;
  - 2 `not_listed`;
  - 1 `cites_prior_paper`;
  - 26 `no_fulltext`.

## 4b. Download shortlist
Run: `.venv/bin/python 040_build_shortlist.py` → **`040_shortlist.json`**.

**How it is built:**
- **Gaps** are taken from the current status in `040_papers.json`: no full text, or referenced supplements that are missing.
- **Ranks and reasons** are reused from the hand tables `PRIORITY` in `025_build_shortlist.py` and `035_build_shortlist.py`.
- **Order:** the Step 2.5 order is kept. Braun-only items go after Step 2.5 rank 10, because they are not cited in the Step 1 PDF but add ADRD code lists for heat and long-term pollution studies.
- **Resolved since Step 2.5:** Qin 2025 AJE (now open access).

**Fields:**
- rank and `shortlist` (the first 11);
- the gap type, plus the Step 2.5 and 3.5 ranks;
- which Scholar profile(s) the paper is in, and its Step 1 CV numbers;
- the exact document to get, links, and why it matters;
- `save_to`. The folders now exist (git-ignored).

**Shortlist: 31 gaps in total, 11 shortlisted.**

| # | Get | Paper | Link | Save to |
|---|---|---|---|---|
| 1 | Article PDF + supplement | Dominici 2006 JAMA | [PMC3543154](https://pmc.ncbi.nlm.nih.gov/articles/PMC3543154/) | `papers/10_1001_jama_295_10_1127/` |
| 2 | Article PDF + supplement | Peng 2008 JAMA | [PMC3169813](https://pmc.ncbi.nlm.nih.gov/articles/PMC3169813/) | `papers/10_1001_jama_299_18_2172/` |
| 3 | Article PDF + supplement | Barr 2012 AJE | [PMC3530376](https://pmc.ncbi.nlm.nih.gov/articles/PMC3530376/) | `papers/10_1093_aje_kws267/` |
| 4 | Article PDF + supplement | Rhee 2019 Chest | [PMC6607425](https://pmc.ncbi.nlm.nih.gov/articles/PMC6607425/) | `papers/10_1016_j_chest_2019_03_017/` |
| 5 | Article PDF + appendix | Chen 2021 Lancet Planet Health | [doi](https://doi.org/10.1016/s2542-5196(21)00168-6) | `papers/10_1016_s2542_5196_21_00168_6/` |
| 6 | Supplement `NIHMS823701-supplement-Supplemental.docx` | Liu 2017 Epidemiology | [PMC5130603](https://pmc.ncbi.nlm.nih.gov/articles/PMC5130603/) | `papers/10_1097_ede_0000000000000556/` |
| 7 | Supplement `NIHMS944332-supplement.docx` | Hopp 2018 Prev Med | [PMC6040588](https://pmc.ncbi.nlm.nih.gov/articles/PMC6040588/) | `papers/10_1016_j_ypmed_2018_02_001/` |
| 8 | Supplement `NIHMS657527-supplement-…Supplemental_Material.pdf` | Bobb 2014 JAMA | [PMC4319792](https://pmc.ncbi.nlm.nih.gov/articles/PMC4319792/) | `papers/10_1001_jama_2014_15715/` |
| 9 | Article PDF + supplement (likely paywalled) | Thomas 2020 JASA | [doi](https://doi.org/10.1080/01621459.2020.1722134) | `papers/10_1080_01621459_2020_1722134/` |
| 10 | Article PDF + Supplement 1 (eMethods: ADRD codes) | 2025 JAMA Intern Med (heat and ADRD) | [PMC11791774](https://pmc.ncbi.nlm.nih.gov/articles/PMC11791774/) | `papers/10_1001_jamainternmed_2024_7719/` |
| 11 | Article PDF + supplement (ADRD definition) | 2026 AJE (ADRD by region and race) | [doi](https://doi.org/10.1093/aje/kwag087) | `papers/10_1093_aje_kwag087/` |

Ranks 12–31 are optional; they are in the JSON.

## 4c. Code sets
Run: `.venv/bin/python 040_build_codesets.py` → **`040_codesets.json`**.

**Three kinds of code sets (`source_type`):**
| source_type | what it is | n |
|---|---|---|
| `author_defined` | The paper lists ICD codes (Parks table excluded). 119 have role `outcome`, from 43 papers; 59 of them include ICD-10. The other 5 are controls, covariates and sensitivity sets. | 124 |
| `ccs_table` | A Parks 2021 CCS group (214 level 3) or cause (13 level 1 = the union of its groups). | 227 |
| `ccs_resolved` | **New in Step 4.** An outcome named only by single-level AHRQ CCS group number(s), e.g. Wei 2019 "septicemia (CCS 2)", Weinberger 2021, Spangler 2023, Feng 2024. Its ICD-9 codes come from the Parks table for those groups. Bobb 2014 gives group names without numbers, so `CCS_BY_NAME` maps them (`resolved_by: name`). | 36 |

**Not resolved (11, listed in `unresolved_classification_outcomes`):**
- whole-classification scans (Bobb 283/214 groups, Wei 214 groups, Wei injury/poisoning);
- multi-level CCS (Wei 2019's 122 groups and Thomas 2022). The Parks table is single-level only.
- Feng 2024 includes CCS 248, which is not in the Parks table. That is flagged in `suspect`.

**Flags per code set:**
- `ccs`, `ccs_groups`, `ccs_level`;
- `parks_analyzed`: whether Parks analyzed the group on its own. Gray groups (`false`) were not.
- `icd_versions`, `n_icd9`, `n_icd10`, `diagnosis_position`, `role`, `outcome_wide_scan`;
- `code_format`: CCS-derived codes are printed without the decimal point (e.g. 4280 = 428.0);
- `suspect`: printed codes that look wrong. There are 13: the typos noted in Steps 2.6/3.6, plus the Parks codes missing a leading digit;
- `flags`: the paper's exposure attributes.

**ICD-10:** `ccs_table` and `ccs_resolved` sets are ICD-9 only. ICD-10 comes only from author-defined sets.

## 4d. Bins (revised 2026-10-26: both code set types fully represented)
Run: `.venv/bin/python 040_build_bins.py` → **`040_bins.json`**, **`040_bins.csv`**, **`040_bins_author_defined.json`**, **`040_bins_derived.json`**.

**Goal (from the user):** bins are useful only if they classify ICD code sets, ideally several per bin. So every final bin must be represented by **both** author-defined and derived code sets.

**Method:**
1. **Union:** the Step 2.8 and 3.8 maps are merged by bin id, and sources are deduplicated by outcome id. Each source brings its code sets, including the `ccs_resolved` sets.
2. **Membership:** a bin's member code sets are those of its `exact` and `narrower` sources that have ICD codes. Parks groups that Parks did not analyze on their own are excluded, and so are `broader` sources (a larger group that contains the bin). In merged bins, each source keeps the scope it had in its original bin.
3. **Restructure** (hand decisions in the script: `DROP`, `RESTRUCTURE`, `MOVES`, `RENAME`). Bins were merged or renamed until **every bin has at least one author-defined member (without a `suspect` note) and at least one derived member** (`ccs_table` or `ccs_resolved`). The script checks this rule, plus:
   - every bin has at least one air pollution, extreme heat or extreme weather paper;
   - every author-defined code set with role `outcome` is in a bin.

**Merges:**
- **R2** Chronic lower respiratory disease: COPD, bronchiectasis and asthma ← R1 (Asthma exacerbations), R3 (Bronchiectasis)
- **C3** Heart failure and hypertensive heart disease ← C6 (Hypertensive heart disease)
- **C4** Arrhythmias and cardiac arrest ← C5 (Cardiac arrest)
- **C10** Peripheral vascular disease and thromboembolism ← C8 (Blood clots: phlebitis, thrombophlebitis, and thromboembolism)
- **C11** Cardiomyopathy and valvular heart disease ← C12 (Valvular heart disease)
- **N1** Parkinson's disease and other neurological disorders (incl. multiple sclerosis) ← N5 (Multiple sclerosis)
- **N3** Psychiatric disorders: depression, bipolar disorder, schizophrenia ← N6 (Schizophrenia and other psychotic disorders), N7 (Bipolar disorder)
- **N4** Cerebrovascular disease, including ischemic stroke ← C7 (Stroke, including ischemic and hemorrhagic stroke)
- **K1** Kidney disease: acute kidney failure, chronic kidney disease, kidney and urinary ← K0 (Kidney and urinary system diseases (composite)), K4 (Chronic kidney disease)
- **K2** Fluid and electrolyte disorders, including dehydration ← K6 (Dehydration and volume depletion)
- **K3** Diabetes mellitus (with or without complications) ← K5 (Diabetes mellitus (all))
- **H1** Heat-related illness and heat-sensitive admissions ← H2 (Heat-sensitive admissions composite (CCS 2, 50, 55, 114, 157, 159, 244))
- **I1** Infections: respiratory (pneumonia, influenza, bronchitis, upper respiratory) and other (sepsis, urinary tract, skin, CNS, intestinal) ← R4 (Pneumonia and other respiratory infections (incl. influenza)), R6 (Upper respiratory infections (and acute bronchitis)), I0 (Non-respiratory infections (composite)), I2 (Urinary tract infections), I3 (Skin and soft-tissue infections), I6 (Central nervous system infections), I7 (Intestinal infections)
- **X1** Injuries and fractures ← X2 (Fractures (incl. hip and osteoporosis-related))

**Dropped:**
- W1 Outcome-wide scans of all disease groups: not an outcome (outcome-wide scans); the scans' groups are in the disease bins.
- C9 Retinal artery occlusion: only inside a broader Parks group (CCS 87, not analyzed on its own); no study of the outcome.
- I4 Pneumocystis pneumonia: only inside the pneumonia CCS group (136.3 in CCS 122); its codes stay in the infections bin.
- C14 Cardiac amyloidosis: no code set (codes in an unfetched supplement) and no environmental exposure study.
- I5 Intestinal obstruction: only one derived code set (Parks CCS 145) and no author-defined code set to group it with.

**Flags per bin:**
- the exposure flags: `air_pollution`, `extreme_heat`, `extreme_weather`, `long_term`, `short_term`, `other_exposure`, with `support` listing the papers per exposure × term;
- `icd10_available`;
- `outcome_wide_only`: every supporting exposure paper is an outcome-wide scan;
- `in_reference_list`, `former_name`, `merged_from`;
- `n_papers` in total and by Scholar profile, `n_member_codesets`, `n_author_defined_members`, `n_derived_members`, `n_suspect_codesets`.

## Results: 22 bins, each represented by both author-defined and derived code sets
How to read the table: the exposure columns give the number of papers (`L` = long-term, `S` = short-term). "author / derived sets" counts member code sets. "papers (D/B)" gives the total and the counts by Scholar profile (Dominici / Braun).

| id | bin | air pollution | extreme heat | extreme weather | long-term | short-term | ICD-10 | scan only | author / derived sets | papers (D/B) |
|---|---|---|---|---|---|---|---|---|---|---|
| R0 | All respiratory disease (composite) | L1 S7 | L1 | S5 | ✓ | ✓ | ✓ |  | 9 / 1 | 13 (13/1) |
| R2 | Chronic lower respiratory disease: COPD, bronchiectasis and asthma | L1 S2 |  | S1 | ✓ | ✓ |  |  | 2 / 3 | 6 (6/0) |
| R5 | Respiratory failure, insufficiency, or arrest (incl. ARDS) | S1 |  | S1 | ✓ | ✓ |  | ✓ | 1 / 1 | 3 (3/0) |
| C0 | All cardiovascular disease (composite) | L5 S10 | L3 S1 | S5 | ✓ | ✓ | ✓ |  | 17 / 1 | 24 (24/2) |
| C1 | Heart attack (acute myocardial infarction) | L5 S3 | L2 | S1 | ✓ | ✓ | ✓ |  | 8 / 2 | 10 (10/1) |
| C2 | Ischemic heart disease and coronary atherosclerosis | L3 S4 | L2 | S1 | ✓ | ✓ | ✓ |  | 9 / 2 | 11 (11/1) |
| C3 | Heart failure and hypertensive heart disease | L3 S5 | S1 | S1 | ✓ | ✓ | ✓ |  | 7 / 3 | 11 (11/2) |
| C4 | Arrhythmias and cardiac arrest | L4 S2 |  | S1 | ✓ | ✓ | ✓ |  | 6 / 3 | 8 (8/0) |
| C10 | Peripheral vascular disease and thromboembolism | L1 S2 | S1 | S1 | ✓ | ✓ |  |  | 3 / 4 | 6 (6/1) |
| C11 | Cardiomyopathy and valvular heart disease | L1 |  | S1 | ✓ | ✓ | ✓ |  | 2 / 1 | 2 (2/0) |
| C13 | Aortic and other arterial aneurysms | L1 S2 |  | S1 | ✓ | ✓ | ✓ |  | 1 / 1 | 4 (4/1) |
| N1 | Parkinson's disease and other neurological disorders (incl. multiple sclerosis) | L3 S2 | S1 | S1 | ✓ | ✓ | ✓ |  | 8 / 2 | 9 (5/5) |
| N2 | Dementia and delirium (incl. Alzheimer's disease) | L5 S1 |  | S1 | ✓ | ✓ | ✓ |  | 11 / 1 | 10 (9/3) |
| N3 | Psychiatric disorders: depression, bipolar disorder, schizophrenia | S1 | S1 | S1 |  | ✓ | ✓ |  | 3 / 2 | 2 (2/0) |
| N4 | Cerebrovascular disease, including ischemic stroke | L7 S3 | L4 | S1 | ✓ | ✓ | ✓ |  | 10 / 3 | 14 (14/2) |
| K1 | Kidney disease: acute kidney failure, chronic kidney disease, kidney and urinary | L2 S1 | S3 | S1 | ✓ | ✓ | ✓ |  | 3 / 4 | 7 (7/3) |
| K2 | Fluid and electrolyte disorders, including dehydration | S1 | S4 | S1 |  | ✓ | ✓ |  | 2 / 4 | 6 (5/2) |
| K3 | Diabetes mellitus (with or without complications) | S2 | S1 | S1 |  | ✓ |  |  | 1 / 4 | 4 (4/1) |
| H1 | Heat-related illness and heat-sensitive admissions |  | S6 |  |  | ✓ | ✓ |  | 3 / 1 | 9 (8/3) |
| I1 | Infections: respiratory (pneumonia, influenza, bronchitis, upper respiratory) and other (sepsis, urinary tract, skin, CNS, intestinal) | L3 S4 | S2 | S1 | ✓ | ✓ | ✓ |  | 4 / 21 | 10 (10/2) |
| X1 | Injuries and fractures | L1 S1 |  | S1 | ✓ | ✓ |  |  | 1 / 2 | 3 (3/0) |
| O1 | Pancreatic cancer |  |  | S1 |  | ✓ |  | ✓ | 1 / 1 | 2 (2/0) |

- **Every bin captures at least 2 code sets.** The largest are all CVD (17 author-defined sets), dementia and delirium (11), cerebrovascular disease (10) and infections (21 derived).
- **2 bins are supported only by an outcome-wide scan:**
  - respiratory failure: Rhee 2020's ARDS paper studies industry proximity, so its exposure is "other";
  - **pancreatic cancer:** its only exposure support is the Parks cyclone scan, and its author-defined set comes from a trends paper. It is the weakest bin and a candidate to drop.
- **No ICD-10 in the bin's code sets:** chronic lower respiratory, respiratory failure, peripheral vascular, diabetes, injuries and fractures, pancreatic cancer. These need ICD-10 codes (e.g. via CCSR or the GEMs) before the YAML.

## 4e. Bins split by code set type
`040_bins_author_defined.json` and `040_bins_derived.json` hold the **same 22 bins**. Each is populated only with author-defined code sets, or only with derived ones (`ccs_table`, `ccs_resolved`), with the flags recomputed per list.
- **After the revision, all 22 bins are `represented` in both files** (0 partial, 0 empty).
- In the author-defined file, the infections bin rests on the respiratory-infection sets (pneumonia, respiratory tract infection). Yitshak-Sade's UTI set ("559", suspect) is listed but not counted.

## Notes for the next step (the YAML for medpar_outcomes)
- Choose **one validated code list per bin**, from its author-defined and derived members. Their definitions often differ (Step 2.7).
- Normalize the codes: CCS codes are printed without decimals; author codes use ranges and wildcards.
