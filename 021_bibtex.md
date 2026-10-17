# Step 2.1 — BibTeX entries for the Google Scholar publications

Input: `020_scholar_publications.json` (687 records). `bib` is set to null when there is no confident match.

## Method
1. Search Crossref by title (`query.bibliographic`, top 5 hits). Hits of type component, peer-review, grant, or dataset are skipped.
2. Pick the best candidate by normalized title similarity (difflib ratio on lowercase alphanumerics; the title plus subtitle also counts). Ties go to a candidate with Dominici as an author, then to a non-preprint.
3. **Accept** if similarity ≥ 0.90 **and** either Dominici is among the Crossref authors, **or** the Scholar year is known, the years differ by at most 1, and the title has at least 4 words.
4. Fetch BibTeX from Crossref (`/works/{doi}/transform/application/x-bibtex`).

Run: `.venv/bin/python 021_fetch_bibtex.py`. Crossref responses are cached in `.cache/021_crossref.json`, so re-runs are offline and resumable. Run log: `.cache/021_run.log`. Run on **2026-10-17**.

## Outputs
| File | Purpose |
|---|---|
| `021_fetch_bibtex.py` | The script |
| `021_scholar_bibtex.json` | One record per Scholar publication: `scholar_pub_id, title, year, status, doi, match, bib`. `match` keeps the best Crossref candidate **even when it was rejected**, for review. |
| `021_scholar_publications.bib` | 486 BibTeX entries. Keys are made unique with `_a`, `_b`, …, and each entry has a `scholar_pub_id` field. |

## Results
| status | n |
|---|---|
| `found` | **486** (71%) |
| `no_confident_match` (bib = null) | 201 |
| `search_failed` / `bibtex_failed` | 0 |

- Of the 592 unflagged Step 2 records, 446 were found. For 2011–2026, 344 of 447 were found.
- In 463 of the 486 matches, Dominici is a Crossref author.
- Crossref types: 459 journal articles, 14 preprints (`posted-content`), 6 book chapters, 5 proceedings articles, 2 books.
- Why records went unmatched: 187 best candidates scored below 0.90, 10 scored ≥ 0.90 but failed the author/year rule, and 4 searches returned no candidate. 36 of the unmatched records have no Scholar year, and many are Step 2 artifacts (`suspect_title`, `no_venue`).

## Known issues (not fixed, review downstream)
- **Shared DOIs:** 486 matches cover **451 unique DOIs**, because 32 DOIs are used by 2 or 3 records. Most cases are legitimate:
  - Scholar listed the same paper twice (Step 2 `duplicate_title`).
  - A preprint or working-paper version mapped to the published paper (e.g. the 2022 "Ambient Heat Metric" preprint, the 2008 "Bayesian approach to effect estimation…" working paper → the 2012 Biometrics paper).
  - Scholar listed a **supplement or technical appendix** as a separate item ("Supplemental Material…", "Supplementary Materials for…", "Technical Appendix…"), and it now points to the parent paper's BibTeX.
  - In one wrong match, a 2015 Scholar entry was mapped to a 2000 Biostatistics DOI (`10.1093/biostatistics/1.2.157`).

  In any per-paper step, **deduplicate on DOI**.
- **Wrong match found while spot-checking:** "Algorithmic Collective Action with *Multiple* Collectives" (score 0.905, Dominici not listed as an author) was matched to a different paper, "…with *Two* Collectives". Matches with a score below 0.95 and no Dominici authorship are the least reliable.
- 41 rejected records have a near-miss candidate scoring 0.80–0.90. Some could be recovered by hand if they matter for Step 2.3.

## Carry forward to Step 2.3
- Use only `status == "found"` records, deduplicated by DOI (≈451 papers).
- BibTeX from Crossref usually has **no abstract**. Judging CMS Medicare outcomes will need abstracts (PubMed or Semantic Scholar by DOI) or the full text, not BibTeX alone.
