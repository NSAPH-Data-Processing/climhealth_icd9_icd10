# Step 3.3 — Medicare outcomes in Danielle Braun's publications

Same definitions and method as Step 2.3 (`023_outcomes.md`): `uses_medicare`, `outcome`, `outcome_names`, `cohort_names`, `uncertain`, and `evidence` (the full sentence from the abstract). Publications without a usable abstract get `outcome: null`.

## Method
1. **`033_prefilter.py`** → `033_candidates.json`. It takes the 114 usable abstracts (deduplicated by DOI) and screens them: **34 `medicare`**, 0 `older_adult`, 80 `none`.
2. **Labels** → `033_labels.json`:
   - **20 papers are also in Dominici's Step 2.3 set** (same DOI). Their hand labels are **copied** from `023_labels.json` (`reused_from_step23: true`), so the two steps agree.
   - **14 papers were read and labeled by hand** (Claude, title and full abstract).
   - **Keyword-rule check:** none of the 80 `none` papers mentions hospitalization, admission, claims or ED visits, so there are no overrides.
3. **`033_build_outcomes.py`** → `033_outcomes.json`: one record per Scholar publication (140). All evidence phrases were found.

Run: `.venv/bin/python 033_prefilter.py && .venv/bin/python 033_build_outcomes.py`.

## Results (114 usable abstracts)
| | n |
|---|---|
| `uses_medicare` True | 32 |
| **`outcome` True** | **17** (none uncertain) |
| Medicare, mortality or all-cause outcomes only | 15 (4 uncertain: HEI reports and a mixtures report) |
| No Medicare | 82 (80 by the keyword rule, 2 by hand) |

By record (140): `outcome` True 17, False 97, null 26 (no usable abstract).

**8 of the 17 outcome papers are not in Dominici's Step 2.3 set.** All use Medicare FFS:

| Year | DOI | Outcome |
|---|---|---|
| 2026 | 10.1038/s41370-026-00882-7 | hospitalization with Parkinson's disease (extreme heat) |
| 2026 | 10.1093/aje/kwag087 | hospitalization with / without ADRD |
| 2026 | 10.1097/ee9.0000000000000519 | first hospitalization with PD (long-term air pollution) |
| 2025 | 10.1097/ee9.0000000000000395 | heat-related hospitalizations (Greater Boston) |
| 2025 | 10.1001/jamainternmed.2024.7719 | first hospitalization with ADRD (extreme heat) |
| 2024 | 10.1016/j.envint.2024.108739 | first PD-involved hospitalization (street-view greenspace) |
| 2024 | 10.1038/s41531-024-00815-x | first hospitalization with PD (air pollution) |
| 2023 | 10.1016/j.envint.2022.107694 | first hospitalization with ADRD (lagged air pollution) |

The other 9 outcome papers are shared with Dominici's set and were already handled in Steps 2.4–2.8.

## Outputs
| File | Purpose |
|---|---|
| `033_prefilter.py`, `033_build_outcomes.py` | Copies of the Step 2.3 scripts with Braun inputs and outputs |
| `033_candidates.json` | 114 unique usable papers with `screen` |
| `033_labels.json` | 34 labels (20 reused from Step 2.3, 14 new) |
| `033_outcomes.json` | One record per Scholar publication (140) |
