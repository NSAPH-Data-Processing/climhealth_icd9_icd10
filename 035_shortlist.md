# Step 3.5 — Shortlist of documents to download manually (Danielle Braun)

Input: `034_fulltext_manifest.json`. Run: `.venv/bin/python 035_build_shortlist.py` → `035_shortlist.json`. The criteria are the same as Step 2.5 (`025_shortlist.md`).

## Candidates
**5 gaps:**
- 3 papers with no full text.
- 2 papers whose referenced supplements could not be fetched.

3 of the 5 are already on the Step 2.5 list.

## Shortlist
Save each file in the listed folder; the folders exist. A PMC link usually works in a normal browser.

| # | Get | Paper | Link | Why | Save to |
|---|---|---|---|---|---|
| 1 | Article PDF + Supplement 1 (eMethods) | 2025 JAMA Intern Med: extreme heat and hospitalization with ADRD | [PMC11791774](https://pmc.ncbi.nlm.nih.gov/articles/PMC11791774/) | **New:** the ADRD code list for a heat study (2000–2018, ICD-9 and ICD-10) | `papers/10_1001_jamainternmed_2024_7719/` |
| 2 | Article PDF + supplementary material | 2026 AJE: hospitalization with and without dementia by region and race | [doi](https://doi.org/10.1093/aje/kwag087) | **New:** another ADRD definition, 2000–2018 | `papers/10_1093_aje_kwag087/` |
| 3 | `NIHMS1763059-supplement-eAppendix_1..3.pdf` | Thomas 2022 Epidemiology (MOReTreeS) | [PMC8852365](https://pmc.ncbi.nlm.nih.gov/articles/PMC8852365/) | Same as Step 2.5 #11: the 57 + 32 CCS leaves (Step 1 S1-13) | `papers/10_1097_ede_0000000000001456/` |
| 4 | `NIHMS1662172-supplement-Supplemental_Digital_Content.pdf` | deSouza 2021 Epidemiology | [PMC7896354](https://pmc.ncbi.nlm.nih.gov/articles/PMC7896354/) | Same as Step 2.5 #20 (low): the codes are in the main text | `papers/10_1097_ede_0000000000001265/` |
| 5 | Article PDF | 2023 Env Int: greenness and kidney disease (Massachusetts) | [doi](https://doi.org/10.1016/j.envint.2023.107844) | Same as Step 2.5 #26 (low) | `papers/10_1016_j_envint_2023_107844/` |

**Update to Step 2.5:** item #6 there (Qin 2025 AJE) no longer needs a download. Step 3.4 found an open-access PDF.

## After downloading
Tell me which items you got. I will register them in the Step 3.4 manifest (and the Step 2.4 manifest for shared papers) and relabel the affected entries.
