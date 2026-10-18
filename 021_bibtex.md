# Step 2.1 — BibTeX entries for the Google Scholar publications

## Input
`020_scholar_publications.json` (687 records).

## Method
Fetching BibTeX from Scholar would take one request per publication, and Scholar blocks this. Instead, for each record:
1. **Search Crossref by title.** This uses the public REST API (`query.bibliographic`) and takes the top 5 hits. Crossref records of type `component`, `peer-review`, `grant`, and `dataset` are skipped, because supplements and reviews share titles with the papers.
2. **Pick the best title match.** Titles are lowercased, HTML tags and entities are stripped, and all non-alphanumerics are removed, so "PM2. 5" equals "PM2.5". Similarity is `difflib` ratio, taking the higher of title and title+subtitle. Ties prefer Dominici authorship, then non-preprints.
3. **Accept the match only if** one of these holds:
   - Dominici is a Crossref author **and** the score is ≥ 0.90, **or**
   - the score is ≥ 0.95, the Scholar year is known and within ±1 of Crossref's, **and** the title has ≥ 4 words.

   Titles that normalize to an empty string (non-Latin scripts) are never matched.
4. **Fetch BibTeX** from Crossref for the DOI (`/works/{doi}/transform/application/x-bibtex`).
5. Otherwise `bib` is **null**.

### Why the rule looks like this (from reviewing the first run)
- **The top Crossref hit is often wrong.** For the 2006 JAMA paper, the first hit was a similarly titled Amazon study, so the best match is chosen across the top 5.
- **Crossref author lists are often incomplete.** In the first run, 22 of 23 accepted matches without Dominici in the authors were correct (e.g. Dominici 2000/2001/2004, Peng 2008 JAMA). So her authorship is not required.
- **The one wrong match** ("…with Multiple Collectives" matched to "…with Two Collectives", score 0.905) led to the stricter 0.95 threshold when she isn't listed as an author.

## Outputs
| File | Purpose |
|---|---|
| `021_fetch_bibtex.py` | Builder. Run it with `.venv/bin/python 021_fetch_bibtex.py`. Crossref responses are cached in `.cache/021_crossref.json` (ignored by git), so reruns are fast and resumable. Delete the cache to re-query. |
| `021_scholar_bibtex.json` | One record per Scholar publication (687). |
| `021_scholar_publications.bib` | All found entries, **one per DOI** (450). The Crossref keys collide (e.g. `Dominici_2006`), so they get suffixes `_a`, `_b`, …. Each entry has a `scholar_pub_id` field. |

### Record shape
```json
{"scholar_pub_id": "...", "title": "...", "year": 2006,
 "status": "found | no_confident_match | search_failed | bibtex_failed",
 "doi": "10.1001/jama.295.10.1127",
 "match": {"doi": "...", "crossref_title": "...", "crossref_year": 2006, "crossref_type": "journal-article",
           "score": 1.0, "dominici_in_authors": true},
 "same_doi_as": ["..."],
 "bib": "@article{Dominici_2006, ...}"}
```
- `match` is the best Crossref candidate. **It is kept even when rejected**, so null cases can be reviewed by hand. `doi` and `bib` are set only when the match is accepted.
- `same_doi_as` lists other Scholar records that resolved to the same DOI.

## Results
| Status | Records |
|---|---|
| `found` | **485** (71%), giving 450 unique DOIs |
| `no_confident_match` | **202**, with `bib: null` |
| `search_failed` / `bibtex_failed` | 0 |

- **69 found records share a DOI with another record.** These are Scholar duplicates, or "Supplemental Material …" entries that resolve to the main paper.
- **Accepted Crossref types:** mostly `journal-article`. There are also about 14 `posted-content` (preprints), plus a few books and proceedings.
- **Null cases are mostly** Scholar artifacts (`suspect_title`), conference abstracts, reports (e.g. HEI), theses, non-Latin titles, and records whose Crossref year differs by more than 1 with Dominici not listed as an author.
- **The BibTeX is verbatim from Crossref.** Some titles contain HTML entities (e.g. `PM&lt;sub&gt;2.5&lt;/sub&gt;`), and Crossref BibTeX has **no abstracts**.

## Carry forward to Step 2.3
- Step 2.3 applies only to records with a non-null `bib` (485 records, 450 unique papers).
- To judge whether a paper uses CMS Medicare outcomes **other than mortality and all-cause hospitalization**, titles and BibTeX alone are thin. Abstracts can be fetched by DOI from PubMed (via DOI→PMID) or from Crossref, where available.
