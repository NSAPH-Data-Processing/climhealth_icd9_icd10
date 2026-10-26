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
