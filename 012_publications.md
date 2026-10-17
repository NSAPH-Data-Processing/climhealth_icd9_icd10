# Step 1.2 — Publication list as a simple JSON

## Input
`010_icd_mappings.json` (Step 1). Only Section 1 cites publications. Section 2 rows have a typical exposure instead.

## Outputs
| File | Purpose |
|---|---|
| `012_extract_publications.py` | Reproducible builder. It uses only the standard library. Run it with `python3 012_extract_publications.py`. |
| `012_publications.json` | **47 publications**, sorted by CV number. |

## Shape
```json
[
  {"cv": 57, "citation": "Dominici et al. 2006 JAMA", "mappings": ["S1-01", "S1-02", "S1-03", "S1-05", "S1-06", "S1-07"]},
  ...
]
```
- `cv`: the CV number (`#NN`) from the PDF. **This is the key: one entry per CV number.**
- `citation`: the citation text as printed, without the `(#…)` part. If the same CV number is cited with different wording in different rows, the fullest version is kept. For example, #132 becomes "Anderson et al. 2013, AJRCCM" and #153 keeps its title.
- `mappings`: the Step 1 mapping IDs that cite the publication.

## Decisions
1. **A shared citation with two CV numbers becomes two entries**, each with the same citation text. This applies to `Bell et al. 2009 (#89, #94)`, `Chen et al. 2021 (#245, #253)`, `Carlsen et al. 2021 (#250, #252)`, `Thomas et al. 2020/2022 (#220, #268)`, and `Feng et al. 2024 (#303/#309)`. The PDF doesn't say which paper is which.
2. **Notes inside the parentheses are dropped**, e.g. "smoking bans", "tropical cyclones", "cardiovascular category". They stay in `publications_raw` in `010_icd_mappings.json`.
3. **The PDF has only short citations.** There are no full titles or DOIs, except the titles for #153 and #177.
