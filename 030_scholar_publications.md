# Step 3 — Publication list from Danielle Braun's Google Scholar profile

Step 3 repeats Steps 2–2.8 for Danielle Braun. Outputs are numbered `03x_*`; Step 3.1 corresponds to Step 2.1, and so on. Each `03x` script is a copy of its `02x` script with Braun's inputs and outputs, so the methods and decisions in the `02x` mds apply unless a `03x` md says otherwise.

## Source
- Profile: https://scholar.google.com/citations?user=zQEnP70AAAAJ (Danielle Braun; Harvard T.H. Chan School of Public Health, Dana-Farber Cancer Institute).
- **How the ID was found:** Scholar's author search needs a login, and Braun is not in the co-author list of Dominici's profile, so the ID came from a web search.
- Retrieved **2026-10-22**. The profile showed 6,370 citations, an h-index of 33, and **140 publications**.

## Outputs
| File | Purpose |
|---|---|
| `030_fetch_scholar.py` | Same as `020_fetch_scholar.py`, with `SCHOLAR_ID = "zQEnP70AAAAJ"` |
| `030_scholar_publications.json` | Profile metadata plus 140 `publications`, in the same shape and with the same flags as Step 2 |

## Results
- 136 records have no flags. 3 have `no_venue`, 3 have `no_year`, and 1 has `suspect_title` ("Package 'CausalGPS'", an R package).
- No duplicate titles.
- By year: 5 are from 2010–2014, 23 from 2015–2019, 73 from 2020–2024, 36 from 2025+, and 3 have no year.
- **39 titles also appear (exactly) in Dominici's Step 2 list.** They are deduplicated later by DOI, when the two sets are combined.

## Decisions
Same as Step 2: the profile list view only, and nothing is dropped, only flagged.
