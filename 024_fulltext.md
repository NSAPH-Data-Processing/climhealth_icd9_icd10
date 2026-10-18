# Step 2.4 — Full text and supplements for the papers to check

Input: `023_outcomes.json`. Run: `.venv/bin/python 024_fetch_fulltext.py`. Run on **2026-10-17**.

## Scope
- Unique papers (by DOI) with `uses_medicare: True`, `outcome: True` and `uncertain: False`: **90**.
- **27 conference abstracts were dropped.** These have no full paper. The list is in `dropped` in the manifest.

| Reason | DOI pattern | n |
|---|---|---|
| ISEE conference abstract | `10.1289/isee.*`, `10.1289/isesisee.*` | 21 |
| Environmental Epidemiology meeting abstract | `10.1097/01.ee9.*` | 5 |
| Epidemiology journal supplement abstract (ISEE meeting) | `10.1097/00001648-YYYYMM001-*` | 1 |

- **63 papers remain**, 58 of them from 2011 onward. One has no DOI: the HEI research report, PMID 27526497.

## Sources (automated only; no Unpaywall, no manual downloads)
1. **PMC Article Datasets on AWS.** This is NCBI's public bucket `pmc-oa-opendata`, covering the PMC open-access subset and NIH author manuscripts. The script takes the latest version folder `PMCxxxx.N/` and downloads the JATS XML, the PDF, and every non-image file as a supplement. The PMCID comes from Europe PMC (searched by DOI, or by PMID when there is no DOI).
2. **The Europe PMC REST API.** It provides `fullTextXML` when an article is not on AWS. Its `supplementaryFiles` zip is also tried when AWS has the article but no supplements. This added nothing in this run.
3. **OpenAlex open-access PDFs** (`best_oa_location` / `locations[].pdf_url`, keeping only `is_oa`). A file is kept only if it is really a PDF.

Not done:
- **PMC website links.** `pmc.ncbi.nlm.nih.gov/.../bin/...` now serves a JavaScript proof-of-work challenge to scripts, and **I did not try to get around it**.
- **Publisher PDF links.** The links that OpenAlex points to (JAMA, OUP, Lancet/Cell Press, Chest) refuse scripted downloads.
- **Images.** Figures (jpg/gif/png/tif) are not downloaded.

## Outputs
| File | Purpose |
|---|---|
| `024_fetch_fulltext.py` | The script. It reuses downloaded files and caches API responses in `.cache/024_api.json`. |
| `024_fulltext_manifest.json` | The committed output: `dropped` (27) plus `papers` (63). |
| `papers/<slug>/` | **Git-ignored.** Holds the XML, PDF and supplements (about 127 MB). The slug is the DOI with non-alphanumerics replaced by `_`. |

Each paper record in the manifest has these fields: `slug, doi, pmid, pmcid, year, title, scholar_pub_ids, outcome_names, status, source, source_url, fulltext_xml, fulltext_pdf, supplements, supplements_referenced, supplements_missing`.
- `supplements_referenced`: supplement file names cited in the JATS XML (`<supplementary-material>`), excluding external URLs and images.
- `supplements_missing`: referenced supplements that could not be fetched.

## Results (63 papers)
| status | source | n |
|---|---|---|
| `fulltext` (≥ 1 supplement file) | pmc_aws | **27** |
| `fulltext_no_supplements` | pmc_aws | **23** |
| `fulltext_no_supplements` | openalex_oa_pdf | **1** (the AAAI 2025 paper) |
| `no_fulltext` | — | **12** |

**Formats:**
- 50 papers have XML, and 27 have a PDF. 26 have both, 24 have XML only, and 1 has a PDF only.
- **XML-only papers have no page numbers.** These are the author manuscripts that AWS ships as text only. Step 2.5 evidence for them will use the section, table or figure label instead.

**Supplements:**
- 39 files: 26 PDF, 9 DOCX, 2 XLSX, 2 ZIP. The zips are not extracted yet.
- **18 of the 23 `fulltext_no_supplements` papers do reference supplements that could not be fetched.** These are author manuscripts whose AWS folder has only XML/text, and whose supplements sit behind the PMC website's bot check. Examples are the *Epidemiology* "Supplemental Digital Content" for tropical cyclones, ARDS and the Bayesian multi-outcome paper, and the JAMA 2014 heat paper's supplement. The other 5 papers reference no supplements.

**No full text (12):**
- JAMA 2006 (Dominici, PM2.5 and hospital admissions)
- JAMA 2008 (Peng, coarse PM)
- JRSS-C 2009 (distributed lag model)
- Biostatistics 2011
- AJE 2012 ×2 (incl. smoking bans and AMI)
- HEI report 2016
- Chest 2019 (ARDS)
- JASA 2020 (432 cardiovascular diseases)
- Lancet Planetary Health 2021 (temporal variation)
- Env Int 2023 (greenness and kidney)
- AJE 2025

Several of these have a PMCID, but they are not in the AWS open-data subset, and Europe PMC returns no full text for them.

## Carry forward to Step 2.5
- Work from the 51 papers with full text. Prefer the PDF for page numbers when there is one, and otherwise use the XML section, table or figure labels.
- For supplements in DOCX, XLSX and PDF format, add the parsers to `requirements.txt` when needed (`pdfplumber`, `python-docx`, `openpyxl`). The 2 zip supplements need extracting.
- For the 18 papers with unreachable supplements, and the 12 without full text, Step 2.5 can only say "not found in available text". It cannot say `not_listed`.
- `papers/` is not in git. Re-run the script on another machine to rebuild it.
