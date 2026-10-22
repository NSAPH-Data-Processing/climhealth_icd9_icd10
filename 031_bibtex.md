# Step 3.1 — BibTeX entries for Danielle Braun's Google Scholar publications

Same method as Step 2.1 (`021_bibtex.md`): a Crossref title search, then the BibTeX for the DOI. `bib` is null when there is no confident match.

The only change is in the match rule: **"Braun is an author"** replaces "Dominici is an author":
- title similarity ≥ 0.90, AND
- (Braun is an author, OR the Scholar year is within 1 and the title has at least 4 words).

Run: `.venv/bin/python 031_fetch_bibtex.py`. The cache is `.cache/031_crossref.json`. Run on **2026-10-22**.

## Results
- **118 of 140 records have a BibTeX entry**, with 118 unique DOIs (no shared DOIs). The other 22 are `no_confident_match`.
- **32 of these DOIs are also in Dominici's Step 2.1 set.**

## Known wrong or weak matches (kept; for review)
| Scholar title | Crossref match | Note |
|---|---|---|
| Dong 2025, air pollution and readmission in AD/ADRD (Lancet Planet Health) | SSRN preprint `10.2139/ssrn.4325230` (2023) | **Preprint, not the journal article.** The journal DOI is `10.1016/S2542-5196(25)00001-4` (Step 1.3, CV #320). |
| "Acknowledgement of reviewers 2014" | `10.1016/s1434-4610(14)00114-x` | **Wrong:** another journal's acknowledgement page. It isn't a research paper either way. |

The other accepted matches with similarity below 0.97 are the same paper. Scholar truncated their titles with "…".

## Outputs
| File | Purpose |
|---|---|
| `031_fetch_bibtex.py` | Copy of `021_fetch_bibtex.py` (author check: Braun) |
| `031_scholar_bibtex.json` | One record per Scholar publication: `status, doi, match, bib` |
| `031_scholar_publications.bib` | The 118 BibTeX entries |
