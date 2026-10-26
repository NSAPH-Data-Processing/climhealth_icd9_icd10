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
