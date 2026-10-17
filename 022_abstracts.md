# Step 2.2 — Abstracts for the Google Scholar publications

Inputs: `020_scholar_publications.json` (687 records) and `021_scholar_bibtex.json` (DOIs). `abstract` is set to null when no source has one.

## Method
**Records with a DOI from Step 2.1 (486 records, 451 unique DOIs).** Sources are tried in order, and the first non-empty abstract is used:
1. **Europe PMC** by DOI. It carries the MEDLINE/PubMed abstracts and also gives the PMID.
2. **OpenAlex** by DOI. It stores abstracts as an inverted index, which the script rebuilds into text.
3. **Semantic Scholar** batch API by DOI.
4. **Crossref** `/works/{doi}` (JATS abstract).

**Records without a DOI (201).** Europe PMC title search, with the **same accept rule as Step 2.1**: title similarity ≥ 0.90 AND (Dominici is an author OR the year is within 1 and the title has at least 4 words). When a match is accepted, its PMID and DOI are filled in too.

Cleaning: HTML/JATS tags are stripped, entities are unescaped, and a leading "Abstract"/"Summary" is removed.

Run: `.venv/bin/python 022_fetch_abstracts.py`. Responses are cached in `.cache/022_abstracts_cache.json`, so re-runs are offline. Run log: `.cache/022_run.log`. Run on **2026-10-17**.

**Environment note:** the folder `.venv` runs **Python 3.6.8**, so scripts must avoid 3.8+ syntax such as `dict | dict` and the walrus operator.

## Outputs
| File | Purpose |
|---|---|
| `022_fetch_abstracts.py` | The script |
| `022_abstracts.json` | One record per Scholar publication: `scholar_pub_id, title, year, doi, pmid, via (doi/title/null), abstract_source, abstract, title_match, flags` |

## Results
**476 of 687 records have an abstract.** These cover 434 unique DOIs. For 2011–2026, 336 of 447 have one.

| via | source | n |
|---|---|---|
| doi | europepmc | 289 |
| doi | openalex | 167 |
| doi | s2 | 3 |
| doi | crossref | 2 |
| doi | none found | 25 |
| title | europepmc | 15 |
| title | none found (matched, no abstract) | 2 |
| none (no DOI, no accepted title match) | — | 184 |

- 319 records have a PMID.
- Title search found a best candidate for 41 of the 201 records without a DOI, and 17 of those passed the accept rule. This adds 15 abstracts and 17 DOIs/PMIDs that Step 2.1 did not have.
- The median abstract length is about 1,700 characters.

## Quality flags (record kept, not nulled)
| Flag | n | Meaning |
|---|---|---|
| `short_abstract` | 11 | Under 200 characters. Often a title echo or author list. |
| `suspect_abstract` | 7 | Matches an author-list or landing-page pattern ("Author Information", "Download a PDF", "MD;", "PhD,"). |

There are 13 flagged records in total, all from OpenAlex. **Treat flagged abstracts as missing in Step 2.3**, which leaves about 463 usable abstracts.

Other things noted while spot-checking OpenAlex, but not flagged:
- A few abstracts start with the article's title or a column header before the actual text.
- Commentaries and book chapters have descriptive summaries rather than study abstracts.

## Carry forward to Step 2.3
- The unit of analysis is the abstract, deduplicated by DOI (434 unique DOIs; after dropping flagged abstracts, 421 unique DOIs plus 9 title-matched records that have no DOI). Records with a null or flagged abstract can be classified from the title only and marked as such, or left undecided.
- For papers where the abstract is not enough to decide (e.g. "Medicare beneficiaries" without saying which outcome), the PMID allows a later lookup of MeSH terms or the PMC full text.
