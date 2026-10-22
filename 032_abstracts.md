# Step 3.2 — Abstracts for Danielle Braun's Google Scholar publications

Same method as Step 2.2 (`022_abstracts.md`):
- **Records with a DOI:** sources are tried in order (Europe PMC → OpenAlex → Semantic Scholar → Crossref).
- **Records without a DOI:** a Europe PMC title search. The accept rule is the same as Step 3.1, with **Braun** as the author check.
- Quality flags are the same: `short_abstract` and `suspect_abstract`.

Run: `.venv/bin/python 032_fetch_abstracts.py`. The cache is `.cache/032_abstracts_cache.json`. Run on **2026-10-22**.

## Results
**115 of 140 records have an abstract.** 97 records have a PMID.

| via | source | n |
|---|---|---|
| doi | europepmc | 90 |
| doi | openalex | 18 |
| doi | crossref | 2 |
| doi | none found | 8 |
| title | europepmc | 5 (all checked: same paper; this adds DOIs and PMIDs) |
| none (no DOI, no accepted title match) | — | 17 |

- **Flagged:** 1 (`short_abstract`, "Long-term impact of fine particulate matter on mortality…").
- **This leaves 114 usable abstracts for Step 3.3.**

## Outputs
| File | Purpose |
|---|---|
| `032_fetch_abstracts.py` | Copy of `022_fetch_abstracts.py` (Braun inputs; author check: Braun) |
| `032_abstracts.json` | One record per Scholar publication, in the same fields as `022_abstracts.json` |
