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

## 4d. Bins
Run: `.venv/bin/python 040_build_bins.py` → **`040_bins.json`**, **`040_bins.csv`**.

**Method:**
1. **Union:** the Step 2.8 and 3.8 maps are merged by bin id, and sources are deduplicated by outcome id. Each source brings its code sets, including the new `ccs_resolved` sets.
2. **Restructure:** hand decisions in the script (`DROP`, `RESTRUCTURE`, `MOVES`, `RENAME`).
   - **Merged:** bronchiectasis into **COPD and bronchiectasis** (494 is in CCS 127 and in 490–492/494–496), and cardiac arrest into **Arrhythmias and cardiac arrest** (427.4–427.5 are inside 426–427).
   - **Split:** "Stroke" becomes **Ischemic stroke** (C15, with 5 author-defined code sets), and all stroke goes into **Cerebrovascular disease, including stroke** (N4). Hemorrhagic stroke has no code set (only multi-level CCS 7.3.1.1).
   - **Renamed:** hypertensive heart disease becomes **Hypertension with complications** (CCS 99), and fractures become **Hip fracture**.
   - **Dropped:** retinal artery occlusion and Pneumocystis (only inside larger groups), cardiac amyloidosis (no codes, no exposure study), and the outcome-wide scans (not an outcome).
3. **Representation rule (checked by the script):** every kept bin has
   - at least one `exact` source with a code set that has ICD codes, not counting Parks groups that Parks did not analyze on their own; and
   - at least one supporting paper with an air pollution, extreme heat or extreme weather exposure.
4. **Coverage rule (checked by the script):** every author-defined code set with role `outcome` is in a kept bin.

**Flags per bin:**
- the exposure flags: `air_pollution`, `extreme_heat`, `extreme_weather`, `long_term`, `short_term`, `other_exposure`, with `support` listing the papers per exposure × term;
- `author_defined`: at least one exact author-defined code set without a `suspect` note;
- `ccs_only`: no author-defined code set at all;
- `icd10_available`;
- `outcome_wide_only`: every supporting exposure paper is an outcome-wide scan (Parks 2021, Wei 2019, Bobb 2014, Hopp 2018);
- `in_reference_list`;
- paper counts in total and by Scholar profile, plus `n_exact_codesets`, `n_author_defined_exact` and `n_suspect_codesets`.

## Results: 44 bins (22 from the reference list or renamed from it, 22 added)
- **27 bins have an author-defined code set**, and **23 have ICD-10 codes.**
- **13 are CCS-only:** their codes come from the CCS table, ICD-9 only.
- **9 are supported only by an outcome-wide scan:** asthma, upper respiratory infections, respiratory failure, hypertension with complications, blood clots, skin infections, intestinal obstruction, injuries, pancreatic cancer.
  - These are well represented by codes, but weakly by dedicated studies.
  - **Candidates to review:** pancreatic cancer (whose only exposure support is the cyclone scan) and injuries.
- **Air pollution:**
  - long-term studies support the cardiorespiratory, kidney, neurodegenerative, infection and cardiomyopathy/valvular/aneurysm bins;
  - short-term studies support most bins.
- **Extreme heat:**
  - short-term studies support heat-related illness, dehydration, fluid/electrolyte, kidney failure, sepsis, UTI, diabetes with complications, peripheral vascular, heart failure, Parkinson's, and the psychiatric bins;
  - long-term studies (climate) support all CVD, IHD, AMI, ischemic stroke, cerebrovascular, and all respiratory.
- **Extreme weather:** cyclones, drought and wildfire. Short-term only, mostly through Parks 2021.

How to read the table: the exposure columns give the number of papers (`L` = long-term, `S` = short-term). The last column gives the paper count in total and by profile (Dominici / Braun; shared papers count in both).

| id | bin | air pollution | extreme heat | extreme weather | long-term | short-term | author-defined codes | ICD-10 | scan only | papers (D/B) |
|---|---|---|---|---|---|---|---|---|---|---|
| R0 | All respiratory disease (composite) | L1 S7 | L1 | S5 | ✓ | ✓ | ✓ | ✓ |  | 13 (13/1) |
| R1 | Asthma exacerbations |  |  | S1 |  | ✓ |  |  | ✓ | 3 (3/0) |
| R2 | COPD and bronchiectasis | L1 S2 |  | S1 | ✓ | ✓ | ✓ |  |  | 4 (4/0) |
| R4 | Pneumonia and other respiratory infections (incl. influenza) | L2 S4 |  | S1 | ✓ | ✓ | ✓ | ✓ |  | 7 (7/1) |
| R5 | Respiratory failure, insufficiency, or arrest (incl. ARDS) | S1 |  | S1 | ✓ | ✓ |  |  | ✓ | 3 (3/0) |
| R6 | Upper respiratory infections (and acute bronchitis) |  |  | S1 |  | ✓ |  |  | ✓ | 1 (1/0) |
| C0 | All cardiovascular disease (composite) | L5 S10 | L3 S1 | S5 | ✓ | ✓ | ✓ | ✓ |  | 24 (24/2) |
| C1 | Heart attack (acute myocardial infarction) | L5 S3 | L2 | S1 | ✓ | ✓ | ✓ | ✓ |  | 10 (10/1) |
| C2 | Ischemic heart disease and coronary atherosclerosis | L3 S4 | L2 | S1 | ✓ | ✓ | ✓ | ✓ |  | 11 (11/1) |
| C3 | Heart failure | L3 S5 | S1 | S1 | ✓ | ✓ | ✓ | ✓ |  | 11 (11/2) |
| C4 | Arrhythmias and cardiac arrest | L4 S2 |  | S1 | ✓ | ✓ | ✓ | ✓ |  | 8 (8/0) |
| C6 | Hypertension with complications (hypertensive heart and kidney disease) |  |  | S1 |  | ✓ |  |  | ✓ | 1 (1/0) |
| C15 | Ischemic stroke | L4 S1 | L2 |  | ✓ | ✓ | ✓ | ✓ |  | 5 (5/1) |
| C8 | Blood clots: phlebitis, thrombophlebitis, and thromboembolism | S1 |  | S1 |  | ✓ |  |  | ✓ | 2 (2/0) |
| C10 | Peripheral vascular disease and atherosclerosis | L1 S1 | S1 | S1 | ✓ | ✓ | ✓ |  |  | 5 (5/1) |
| C11 | Cardiomyopathy | L1 |  |  | ✓ |  | ✓ | ✓ |  | 2 (2/0) |
| C12 | Valvular heart disease | L1 |  | S1 | ✓ | ✓ | ✓ | ✓ |  | 2 (2/0) |
| C13 | Aortic and other arterial aneurysms | L1 S2 |  | S1 | ✓ | ✓ |  | ✓ |  | 4 (4/1) |
| N1 | Parkinson's disease | L3 S2 | S1 | S1 | ✓ | ✓ | ✓ | ✓ |  | 9 (5/5) |
| N2 | Dementia, including Alzheimer's disease | L5 S1 |  |  | ✓ | ✓ | ✓ | ✓ |  | 10 (9/3) |
| N3 | Depression and mood disorders | S1 | S1 |  |  | ✓ | ✓ | ✓ |  | 2 (2/0) |
| N4 | Cerebrovascular disease, including stroke | L3 S2 | L2 | S1 | ✓ | ✓ | ✓ | ✓ |  | 9 (9/1) |
| N5 | Multiple sclerosis | S1 |  | S1 |  | ✓ | ✓ |  |  | 2 (2/0) |
| N6 | Schizophrenia and other psychotic disorders | S1 | S1 | S1 |  | ✓ | ✓ | ✓ |  | 2 (2/0) |
| N7 | Bipolar disorder | S1 | S1 |  |  | ✓ | ✓ | ✓ |  | 2 (2/0) |
| K0 | Kidney and urinary system diseases (composite) | L1 |  |  | ✓ |  | ✓ | ✓ |  | 2 (2/1) |
| K1 | Acute or unspecified kidney failure | L1 S1 | S3 | S1 | ✓ | ✓ | ✓ | ✓ |  | 6 (6/2) |
| K2 | Fluid and electrolyte disorders (incl. dehydration) | S1 | S4 | S1 |  | ✓ |  | ✓ |  | 6 (5/2) |
| K3 | Diabetes with complications | S1 | S1 | S1 |  | ✓ |  |  |  | 4 (4/1) |
| K4 | Chronic kidney disease | L1 |  | S1 | ✓ | ✓ | ✓ | ✓ |  | 2 (2/1) |
| K5 | Diabetes mellitus (all) | S1 |  | S1 |  | ✓ | ✓ |  |  | 2 (2/0) |
| H1 | Heat-related illness (heat stroke, heat exhaustion, effects of heat) |  | S4 |  |  | ✓ | ✓ | ✓ |  | 7 (6/2) |
| H2 | Heat-sensitive admissions composite (CCS 2, 50, 55, 114, 157, 159, 244) |  | S2 |  |  | ✓ |  |  |  | 2 (2/1) |
| I0 | Non-respiratory infections (composite) | L1 |  |  | ✓ |  |  |  |  | 2 (2/0) |
| I1 | Sepsis/septicemia | L1 S1 | S2 | S1 | ✓ | ✓ |  |  |  | 5 (5/1) |
| I2 | Urinary tract infections | L1 S2 | S2 | S1 | ✓ | ✓ |  |  |  | 6 (6/1) |
| I3 | Skin and soft-tissue infections | S1 |  | S1 |  | ✓ |  |  | ✓ | 2 (2/0) |
| I5 | Intestinal obstruction |  |  | S1 |  | ✓ |  |  | ✓ | 1 (1/0) |
| I6 | Central nervous system infections | L1 |  | S1 | ✓ | ✓ |  |  |  | 2 (2/0) |
| I7 | Intestinal infections | L1 |  | S1 | ✓ | ✓ |  |  |  | 2 (2/0) |
| X1 | Injuries |  |  | S1 |  | ✓ |  |  | ✓ | 1 (1/0) |
| X2 | Hip fracture | S1 |  | S1 |  | ✓ | ✓ |  |  | 3 (3/0) |
| O1 | Pancreatic cancer |  |  | S1 |  | ✓ | ✓ |  | ✓ | 2 (2/0) |
| K6 | Dehydration and volume depletion |  | S1 |  |  | ✓ | ✓ | ✓ |  | 1 (0/1) |

**Removed (7):**
- W1 Outcome-wide scans of all disease groups: not an outcome (outcome-wide scans); the scans' groups are in the disease bins.
- C9 Retinal artery occlusion: only inside a broader Parks group (CCS 87, not analyzed on its own); no study of the outcome.
- I4 Pneumocystis pneumonia: only inside the pneumonia CCS group (136.3 in CCS 122); its codes stay in R4.
- C14 Cardiac amyloidosis: no code set (codes in an unfetched supplement) and no environmental exposure study.
- R3 Bronchiectasis: merged into R2.
- C5 Cardiac arrest: merged into C4.
- C7 Stroke, including ischemic and hemorrhagic stroke: merged into N4.

## Notes for the next step (the YAML for medpar_outcomes)
- A bin's sources often define it differently (Step 2.7). The next step should choose **one code list per bin** and validate it, and include ICD-10 for the CCS-only bins (e.g. via CCSR or the GEMs).
- Codes from CCS are printed without decimals; author codes are as written, with wildcards and ranges. They need normalizing before the YAML.
