# Step 2 — Publication list from Francesca Dominici's Google Scholar profile

Built **independently of Step 1/1.2**: nothing from the PDF was used to fetch or filter.

## Source
- Profile: https://scholar.google.com/citations?user=RSwElNMAAAAJ (Francesca Dominici, "Professor of Biostatistics").
- Retrieved **2026-10-17**. At retrieval the profile showed 63,127 citations, an h-index of 109, and **687 publications**.
- Scholar's author search redirects to a Google login, so the profile ID was found by web search. The public profile page itself is accessible.

## Environment
- Python venv at `.venv/` (ignored by git). Dependencies are in `requirements.txt` (`scholarly==1.7.11`).
- Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`

## Outputs
| File | Purpose |
|---|---|
| `020_fetch_scholar.py` | Fetches the profile with `scholarly`. Run it with `.venv/bin/python 020_fetch_scholar.py`. Re-running it gives a new snapshot, so counts may change. |
| `020_scholar_publications.json` | Profile metadata plus a `publications` list (687 records), sorted by year (newest first), then by title. |

## Shape (per publication)
```json
{"scholar_pub_id": "RSwElNMAAAAJ:d1gkVwhDpl0C",
 "title": "Fine particulate air pollution and hospital admission for cardiovascular and respiratory diseases",
 "year": 2006, "venue": "Jama 295 (10), 1127-1134, 2006", "num_citations": 3516, "flags": []}
```

## Decisions
1. **Profile list view only.** Each record has the title, year, venue string, and citation count. Authors, abstracts, and DOIs are **not** fetched, because that would take one request per publication (687) and Scholar rate-limits or blocks this. They can be fetched later for a filtered subset if needed.
2. **Nothing is dropped, only flagged.** Scholar profiles contain artifacts, so each record gets `flags`:

| Flag | Count | Meaning |
|---|---|---|
| `no_venue` | 64 | No venue string |
| `no_year` | 43 | No year |
| `suspect_title` | 23 | Fewer than 4 words, or a known artifact pattern (e.g. "Europe PMC free article", "S2 File", "THE ANNALS", "2018.“" dated 1940). **This is a heuristic.** A few real items are caught too, e.g. "Particulate matter matters" and a workshop report. |
| `duplicate_title` | 22 | 11 titles appear twice |

592 records have no flags.
3. **No date or topic filtering here.** For reference, 447 records are dated 2011–2026, which is the window the PDF claims to cover. Filtering is left for later steps, e.g. Step 2.3 (CMS Medicare outcomes).

## Carry forward
- Step 2.3 will need more than titles to judge whether a paper uses CMS Medicare outcomes. Options are abstracts (Scholar per-publication fetches, or PubMed/Crossref by title) or title keywords as a first pass.
- Matching these records to the PDF's CV numbers (`#NN` in `012_publications.json`) is not possible directly. The CV numbering is not on Scholar, so matching would have to use author, year, and title.
