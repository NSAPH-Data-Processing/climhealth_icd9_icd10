# Step 3.4 — Full text and supplements for Danielle Braun's Medicare outcome papers

Same method and scope rule as Step 2.4 (`024_fulltext.md`): unique papers from Step 3.3 with `uses_medicare`, `outcome` and not `uncertain`. Conference abstracts are dropped, but there were none. Sources: PMC AWS open data → Europe PMC → OpenAlex OA PDF.

Files go to the same git-ignored `papers/<slug>/` folder as Step 2.4, so papers shared with Dominici's set reuse the files already downloaded.

Run: `.venv/bin/python 034_fetch_fulltext.py`. The cache is `.cache/034_api.json`. Run on **2026-10-22**.

## Results (17 papers; 8 are new, 9 are shared with Step 2.4)
| status | source | n |
|---|---|---|
| `fulltext` (≥ 1 supplement) | pmc_aws | 11 |
| `fulltext_no_supplements` | pmc_aws | 2 (Danesh Yazdi 2021 / deSouza 2021 and Thomas 2022: referenced supplements unreachable, as in Step 2.4) |
| `fulltext_no_supplements` | openalex_oa_pdf | 1 (**Qin 2025 AJE**, ADRD methods) |
| `no_fulltext` | — | 3 |

- **Qin 2025 AJE (#311 in the CV) now has an open-access PDF.** It was `no_fulltext` in Step 2.4 (item 6 of the Step 2.5 download list). The 024 manifest was not re-run, so it still says `no_fulltext`; Step 3.6 reads the paper.
- **6 of the 8 new papers have full text, all with their supplement:**
  - Parkinson's ×4: heat 2026, air pollution 2024, street-view greenspace 2024, long-term air pollution 2026.
  - ADRD lagged air pollution 2023.
  - Heat in Greater Boston 2025.
- **No full text (2 new papers):** JAMA Intern Med 2025 (heat and ADRD) and AJE 2026 (ADRD hospitalization by region and race).
- **Also no full text (shared paper):** Greenness and kidney 2023 (Env Int), which was already a gap in Step 2.4.

## Fixes to the fetch script (also applied to `024_fetch_fulltext.py`)
1. **Folders inside `papers/<slug>/` were listed as supplements.** That includes the `text/` folder created by Step 2.6. Directories are now skipped.
2. **`.webp` figure images were treated as supplements.** `.webp` is now in the image list.

The committed `024_fulltext_manifest.json` was built before `text/` existed, so it is not affected.

## Outputs
| File | Purpose |
|---|---|
| `034_fetch_fulltext.py` | Copy of `024_fetch_fulltext.py` with Braun inputs and outputs |
| `034_fulltext_manifest.json` | 17 papers, in the same fields as the Step 2.4 manifest |
