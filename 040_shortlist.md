# Step 4 — Unified shortlist of documents to download manually

Input: `025_shortlist.json`, `035_shortlist.json` (read only). Run: `.venv/bin/python 040_build_shortlist.py` → `040_shortlist.json`.

## Result
| | Papers | Shortlisted |
|---|---|---|
| Step 2.5 (Francesca Dominici) | 30 | 10 |
| Step 3.5 (Danielle Braun) | 5 | 5 |
| **Unified** | **32** | **15** |

3 papers are on both lists and appear once.

## How the list is built
- **One row per paper,** matched by DOI. One Step 2.5 item has no DOI (rank 30, HEI 2016), so it is matched by its `save_to` folder. It is not on the Step 3.5 list.
- **Shortlisted** means shortlisted in either step. All 3 shared papers are shortlisted in Step 3.5 only.
- **Unified rank:**
  1. Shortlisted papers on the Step 2.5 list, in Step 2.5 order.
  2. Shortlisted papers on the Step 3.5 list only, in Step 3.5 order.
  3. The other papers, in Step 2.5 order. All of them are on the Step 2.5 list only.

The unified rank follows this rule and is not a new judgement of value. The shared papers at ranks 11–13 are rated optional or low in Step 2.5, but they come before ranks 14–15, which Step 3.5 rates highest because they add new ADRD code lists.

## Fields
- `unified_rank`, `shortlist`, and `lists` (which list or lists the paper came from).
- `step25_rank`, `step35_rank`, `step25_shortlist`, `step35_shortlist` (null when the paper is not on that list).
- `document_step25`, `document_step35`, `why_step25`, `why_step35`, kept per list.
- `step1_cv` (the union of both lists).
- `gap`, `year`, `title`, `doi`, `pmid`, `pmcid`, `links`, `save_to`.

## Shortlist
| # | Step 2.5 | Step 3.5 | Paper | Gap | Save to |
|---|---|---|---|---|---|
| 1 | 1 | | Dominici 2006 JAMA, PM2.5 and CVD/respiratory admissions | no full text | `papers/10_1001_jama_295_10_1127/` |
| 2 | 2 | | Peng 2008 JAMA, coarse PM | no full text | `papers/10_1001_jama_299_18_2172/` |
| 3 | 3 | | Barr 2012 AJE, smoking bans and AMI | no full text | `papers/10_1093_aje_kws267/` |
| 4 | 4 | | Rhee 2019 Chest, PM2.5/ozone and ARDS | no full text | `papers/10_1016_j_chest_2019_03_017/` |
| 5 | 5 | | Chen 2021 Lancet Planetary Health, temporal variation | no full text | `papers/10_1016_s2542_5196_21_00168_6/` |
| 6 | 6 | | Qin 2025 AJE, ADRD methods comparison | no full text (see note) | `papers/10_1093_aje_kwae133/` |
| 7 | 7 | | Liu 2017 Epidemiology, wildfire PM2.5 | supplement missing | `papers/10_1097_ede_0000000000000556/` |
| 8 | 8 | | Hopp 2018 Prev Med, heat-wave diagnoses | supplement missing | `papers/10_1016_j_ypmed_2018_02_001/` |
| 9 | 9 | | Bobb 2014 JAMA, cause-specific heat risk | supplement missing | `papers/10_1001_jama_2014_15715/` |
| 10 | 10 | | Thomas 2020 JASA, 432 cardiovascular diseases | no full text | `papers/10_1080_01621459_2020_1722134/` |
| 11 | 11 | 3 | Thomas 2022 Epidemiology, Bayesian multi-outcome | supplement missing | `papers/10_1097_ede_0000000000001456/` |
| 12 | 20 | 4 | deSouza 2021 Epidemiology, short-term PM2.5 | supplement missing | `papers/10_1097_ede_0000000000001265/` |
| 13 | 26 | 5 | 2023 Env Int, greenness and kidney disease | no full text | `papers/10_1016_j_envint_2023_107844/` |
| 14 | | 1 | 2025 JAMA Intern Med, extreme heat and ADRD | no full text | `papers/10_1001_jamainternmed_2024_7719/` |
| 15 | | 2 | 2026 AJE, dementia by region and race | no full text | `papers/10_1093_aje_kwag087/` |

**Note on #6.** `025_shortlist.json` lists Qin 2025 as having no full text, and it stays on the list as that file records it. `035_shortlist.md` says this paper no longer needs a download, because Step 3.4 found an open-access PDF.

## Not shortlisted
Ranks 16–32 (17 papers) are in `040_shortlist.json`, all from the Step 2.5 list. Step 2.5 rates them optional or low value.
