# Step 4.1 — Manual downloads of the shortlisted papers

Input: the 15 shortlisted papers in `040_shortlist.json`. Files are saved in `papers/<slug>/` (git-ignored).

Run: `.venv/bin/python 041_build_status.py` → `041_status.json`, the status of each paper, updated after each download.

## How we worked
- **In Chrome, together.** Claude opened publisher pages and saved files where the site allowed it. The user signed in through Harvard Library when a site asked, and downloaded files by hand where noted. Claude never entered credentials.
- **PMC-hosted files were clicked by the user.** PMC serves a bot check to scripts (Step 2.4), so Claude did not automate those pages.
- **Filing.** Files were moved from `~/Downloads` to the paper's folder. Article PDFs are saved as `article.pdf`; supplements keep their original names.
- **No manifests changed.** The Step 2.4 and 3.4 manifests are not edited.

## Downloads
| # | Paper | Files | Source | Access |
|---|---|---|---|---|
| 1 | Dominici 2006 JAMA | `article.pdf` | JAMA | Harvard sign-in. No supplement link found on the page. |
| 2 | Peng 2008 JAMA | `article.pdf` | JAMA | Harvard sign-in. No supplement link found on the page. |
| 3 | Barr 2012 AJE | `article.pdf`, `kws267-kws267_web_material.pdf` | Oxford Academic | User download |
| 4 | Rhee 2019 Chest | `article.pdf`, `mmc1.pdf` | Chest journal site | User download |
| 5 | Chen 2021 Lancet Planet Health | `article.pdf`, `supplement_mmc1.pdf` | The Lancet | Open access |
| 6 | Qin 2025 AJE | `article.pdf`, `web_material_kwae133.zip`, `Causal_AD_ADRD Supp.pdf` (from the zip; its `latex.zip` is left unextracted) | Oxford Academic | User download |
| 7 | Liu 2017 Epidemiology | `article.pdf`, `NIHMS823701-supplement-Supplemental.docx` | PMC | User download |
| 8 | Hopp 2018 Prev Med | `article.pdf`, `NIHMS944332-supplement.docx` | PMC | User download |
| 9 | Bobb 2014 JAMA | `article.pdf`, `NIHMS657527-supplement-Hospitalizations_and_heat_waves_-_Supplemental_Material.pdf` | PMC | User download |
| 10 | Thomas 2020 JASA | `article.pdf`, `uasa_a_1722134_sm0458.pdf`, `uasa_a_1722134_sm0459.pdf` | Taylor & Francis | Article: Harvard sign-in. Supplements: free. |
| 11 | Thomas 2022 Epidemiology | `NIHMS1763059-supplement-eAppendix_1.pdf`, `_2.pdf`, `_3.pdf` (full text `PMC8852365.1.xml` is from Step 2.4) | PMC | User download |
| 12 | deSouza 2021 Epidemiology | `article.pdf`, `NIHMS1662172-supplement-Supplemental_Digital_Content.pdf` | PMC | User download |
| 13 | 2023 Env Int, greenness and kidney disease | `article.pdf`, `1-s2.0-S0160412023001174-mmc1.docx` | ScienceDirect | User download |
| 14 | 2025 JAMA Intern Med, heat and ADRD | `article.pdf`, `ioi240093supp1_prod_1743791974.59513.pdf` (Supplement 1) | JAMA Network | Harvard sign-in. Supplement 2 (data sharing statement) skipped. |
| 15 | 2026 AJE, dementia by region and race | `article.pdf`, `web_material_kwag087.zip`, `Supplementary_materials_kwag087.pdf` (the only file in the zip) | Oxford Academic | Harvard sign-in |

All 15 shortlisted papers are downloaded.

**Note on #6.** `034_fulltext_manifest.json` records `papers/10_1093_aje_kwae133/fulltext.pdf`, and `035_shortlist.md` says no download is needed, but that file is not on disk, so the paper was downloaded here as `article.pdf`.

**Not done in this step:** the files have not been opened, checked against their papers, or used for code extraction.
