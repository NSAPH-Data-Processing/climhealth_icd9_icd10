# Step 3.7 — Step 1 check table using Danielle Braun's papers

Same comparison and verdicts as Step 2.7 (`027_step1_check.md`). The difference is the evidence: only papers in **Braun's Step 3.4 set** count (`036_icd_codes.json`).

## How the crosswalk was made
`037_crosswalk.json` is derived from `027_crosswalk.json` (which follows the CV numbers checked in Step 1.3):
- **CV numbers:** a cited CV number keeps its paper only if that paper is in Braun's set. Other CV numbers get "not in Braun's Step 3.4 set".
- **Row → outcome choices:** kept for papers in Braun's set.
- **Additions:**
  - CV **#311** (Qin 2025 AJE) is now a cited paper for S1-17 (dementia), because it has full text since Step 3.4.
  - **Context** (shown, not counted toward the verdict):
    - S1-15 (neurological): 4 new Parkinson's papers plus Shi 2020.
    - S1-17: Mork 2023 (ADRD).
    - S1-24 (heat illness): Jung 2025 (Boston heat).

Run: `.venv/bin/python 037_build_check.py` → `037_step1_check.json`, **`037_step1_check.csv`**.

## Results (37 Section 1 rows)
**Braun's papers are cited for only 4 Step 1 rows.** 35 rows are `no_evidence` from Braun's set alone. Step 1 was built from Dominici's papers, so this is expected.

| Row | Cited Braun paper | Verdict |
|---|---|---|
| S1-13 cardiorespiratory | Thomas 2022 (CCS chapters 7 and 8) | not_comparable |
| S1-17 dementia | Qin 2025 (CCW codes in the unfetched Appendix S1) | no_evidence |
| S1-18 kidney | Lee 2023 (AKI 584/N17 only) | differs (no 585/N18) |

**Context from Braun-only papers:**
- **S1-24 heat illness: Jung 2025 matches on ICD-9** (992.0–992.9). Its ICD-10 range is printed "T67.3-67.5", which the comparison cannot parse, and it is narrower than Step 1's T67.0–T67.9.
- **S1-17 dementia:** Mork 2023 uses the CCW list, which is much broader than Step 1's 290.0 and 331.0. It adds 294.x and 797 (ICD-9) and F04–F06, G13.8, G31.x, G94, R41.81, R54 (ICD-10).
- **S1-15 neurological (320–359 / G00–G99):** the 4 Parkinson's papers "differ", as expected. They use only 332 / G20 (± 332.1, G21.x), a single disease inside the row's range. **Step 1 has no Parkinson's row**, even though 5 papers in the combined set define Parkinson's hospitalization explicitly. This is a candidate addition for the final outcome list.

## Outputs
| File | Purpose |
|---|---|
| `037_crosswalk.json` | The crosswalk restricted to Braun's papers, plus the context additions |
| `037_build_check.py` | Copy of `027_build_check.py` with inputs 036 and 037 |
| `037_step1_check.csv`, `037_step1_check.json` | The check table (65 rows; Section 2 rows are `not_checked`) |
