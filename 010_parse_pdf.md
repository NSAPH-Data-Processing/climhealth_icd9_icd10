# Step 1 — Parse the PDF into a JSON inventory of ICD mappings

## Input
`Dominici_hospitalization_ICD_codes.md.pdf` (7 pages). It contains:
- **Section 1: From Dr. Dominici's Publications.** 37 rows with columns: Cause, ICD-9-CM, ICD-10-CM, Representative Publication(s) (with CV numbers `#NN`).
- **Section 2: Broader environmental epidemiology literature, not necessarily in the CV.** 28 rows with columns: Cause, ICD-9-CM, ICD-10-CM, Typical Exposure Studied.
- A note after Section 1 and three "Notes on Interpretation". These are stored in `document_notes`.

## Outputs
| File | Purpose |
|---|---|
| `010_extract_mappings.py` | Reproducible builder. It uses only the standard library (no environment needed). Run it with `python3 010_extract_mappings.py`. |
| `010_icd_mappings.json` | The inventory: **65 mappings** (S1 = 37, S2 = 28). |

## Decisions
1. **Transcribed from the rendered pages, not the PDF text layer.** The text layer corrupts some cells: it drops dots (`9929`, `T670–T679`), merges words (`substancerelated`, `Hopp et al2018`), and truncates text at page breaks. Each row was checked against the page image.
2. **Every mapping is one table row.** IDs are `S{section}-{row:02d}` (e.g. `S1-08`, `S2-11`), and each row records its PDF page.
3. **Each ICD cell keeps `raw` (verbatim) and parsed `codes`.** A code spec is either `{type:"code", code}` or `{type:"range", start, end}`. Parenthetical text becomes `label`, and subsets marked "esp." become `emphasis`.
4. **No normalization or expansion yet.** Codes and en-dashes are kept as printed. Ranges are not expanded into individual codes, and validity against official ICD code sets is not checked. That is left for later steps.
5. **`parse_status` flags cells that are not clean code lists:**

| Status | Meaning | Cells |
|---|---|---|
| `parsed` | All codes captured | 58 ICD-9 / 58 ICD-10 |
| `qualified` | Codes captured but hedged ("Multiple (…)", "Varies (…)") | S1-26 (both), S1-28 ICD-10 |
| `partial` | Open-ended ("etc.", "site-specific infection codes") | S1-36 (both) |
| `unspecified` | No codes given | S1-28 ICD-9, S1-29 ICD-9, S1-31 (both) |
| `reference` | "See CVD row above" | S1-33 (both); ambiguous whether this means S1-01 or S1-08 |
| `none` | Em dash `—` | S1-29 ICD-10, S2-28 (both) |

6. **Publications (S1) are split on `;`**, and CV numbers are extracted into `cv_numbers`. **Typical exposure (S2)** is split on top-level commas.

## JSON shape (per mapping)
```json
{
  "id": "S1-24", "section": 1, "row": 24, "page": 3,
  "outcome": "Heat stroke / heat-related illness",
  "icd9cm":  {"raw": "...", "parse_status": "parsed", "codes": [{"type": "code", "code": "992.0", "label": "heat stroke"}, ...]},
  "icd10cm": {"raw": "...", "parse_status": "parsed", "codes": [...]},
  "publications_raw": "...", "publications": [{"citation": "...", "cv_numbers": ["171"]}]
  // Section 2 has typical_exposure_raw / typical_exposure instead of publications
}
```

## Observations to carry forward (not yet assessed)
I noticed these while transcribing. They are candidates for the checking steps:
- The header says "last 15 years, 2011–2026", but several cited papers are from 2006–2009 (#57, #61, #78, #89, #92, #94).
- Some ICD-9 and ICD-10 ranges don't align one-to-one, e.g. COPD `490–492, 494–496` vs `J40–J44`, CO-associated `427–428` vs `I47–I50`, and dementia `290.0, 331.0` vs `F01–F03, G30`.
- Some codes may not exist or may be non-billable as written, e.g. `I46.2`/`I46.8` and the ICD-10 range `E10–E14` (E12 is not used in ICD-10-CM).
- S1-36 is labelled "long-term PM2.5", which conflicts with the document's short-term scope.
- Several outcomes overlap or duplicate each other: S1-13, S1-30, S1-34, and S1-35 are all `390–519`, and S1-19 and S1-21 are both `290–319`.
