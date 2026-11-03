# Step 4.2 — Steps 2.6 and 2.8 applied to the manually downloaded papers

Input: the 15 papers in `041_status.json`. Steps 2.6, 2.8, 3.6 and 3.8 files are not changed.

Run:
```
.venv/bin/python -I 042_extract_text.py
.venv/bin/python -I 042_build_icd_codes.py
.venv/bin/python -I 042_build_bins.py
```

## Method
1. **Text.** `042_extract_text.py` writes `papers/<slug>/text/<file>.txt` (git-ignored) with the Step 2.6 location markers. PDFs are read with PyMuPDF (added to `requirements.txt`), because `pdftotext` is not on this machine.
2. **Labels.** `042_labels.json` holds the hand labels: data source, each outcome, codes as written, diagnosis position and a quote. Bobb 2014, Thomas 2022 and deSouza 2021 reuse their Step 2.6 labels, because the downloads add no codes to them.
3. **Records.** `042_build_icd_codes.py` → `042_icd_codes.json`, using the Step 3.6 quote search and record format. A quote that is not found stops the build. **All quotes were found.**
4. **Exposure.** `042_exposures.json` uses the Step 2.8 rules. Nine papers are newly classified; six repeat their Step 2.8 or 3.8 labels.
5. **Bins.** `042_build_bins.py` → `042_bins.json`, `042_bins_populated.json`, `042_bins.csv`. These are the Step 2.8 bins and build, with sources from these 15 papers only. Bins with no source here show `no_evidence`. Every explicit code set with role `outcome` is in a bin.

**Added field:** `group_based` marks outcome-wide group entries. Their ICD codes will be handled separately, so Step 5 leaves them out.

## Result
**All 15 papers use Medicare inpatient or FFS claims** (`stated` 13, `implied` 2: Dominici 2006, Peng 2008). There are 75 outcome entries: 56 with explicit codes, 18 `classification_ref` and 1 `not_listed`. 23 entries are group-based.

| # | Paper | Exposure | Codes found | Diagnosis position |
|---|---|---|---|---|
| 1 | Dominici 2006 JAMA | PM2.5, short-term | 7 outcomes + injuries control, ICD-9 | principal |
| 2 | Peng 2008 JAMA | coarse PM, short-term | 2 composites, their 7 causes + injuries control, ICD-9 | principal |
| 3 | Barr 2012 AJE | smoking bans | AMI: 410.xx excluding 410.x2 | principal |
| 4 | Rhee 2019 Chest | PM2.5, ozone, long-term | ARDS: 518.51, 518.52, 518.53, 518.82 (3 subgroup definitions kept as `component`) | principal or secondary |
| 5 | Chen 2021 Lancet Planet Health | PM2.5, short-term | Circulatory, respiratory; ICD-9 and ICD-10 | principal |
| 6 | Qin 2025 AJE | air pollution, long-term | ADRD, CCW algorithm: 24 ICD-9 + 22 ICD-10 | any |
| 7 | Liu 2017 Epidemiology | wildfire smoke, short-term | CVD, respiratory, ICD-9 (5 CVD parts kept as `component`) | principal |
| 8 | Hopp 2018 Prev Med | heat waves | 7 outcomes with explicit ICD-9 codes; the 50 diagnoses are group-based | principal |
| 9 | Bobb 2014 JAMA | heat waves | CCS groups only, group-based | principal |
| 10 | Thomas 2020 JASA | PM2.5, short-term | Circulatory 390–459; 8 model groups are group-based | principal |
| 11 | Thomas 2022 Epidemiology | PM2.5, short-term | CCS groups only, group-based | principal |
| 12 | deSouza 2021 Epidemiology | PM2.5, short-term | 5 outcomes, ICD-9; no new codes | principal |
| 13 | Lee 2023 Environ Int | greenness, long-term | Total kidney disease, CKD, AKI; ICD-9 and ICD-10 | principal or secondary |
| 14 | Delaney 2025 JAMA Intern Med | heat index, short-term | ADRD: CCW named, **codes not printed** | any (first 10) |
| 15 | 2026 AJE, dementia by region and race | region and race | ADRD: CCW named, **codes not printed** | any |

## Findings
- **Ranks 14 and 15 add no code lists.** Step 3.5 ranked them highest because they might add new ADRD lists, but they only name the CCW algorithm. Neither the articles nor the supplements print the codes. Step 5 leaves their ranges empty.
- **Rank 15 supplement is truncated at the publisher.** `Supplementary_materials_kwag087.pdf` declares 14,958,278 bytes and has 14,774,272, and it opens with 0 pages. The zip it came from passes its integrity test, so the download is not the cause. `042_extract_text.py` adds a page tree in memory, and all 21 pages then read normally. The file on disk is not changed.
- **Liu 2017 peripheral vascular disease is printed as 440–449.** Dominici 2006 and Peng 2008 use 440-448.
- **deSouza 2021 "390 to 495"** is kept as written here. It remains a likely typo for Step 5.
- **Stale note in reused labels.** One Bobb 2014 outcome note still says the supplement was "not fetched", because it comes unchanged from `026_labels.json`. The supplement is now on disk.

## Judgement calls
- **Thomas 2020's 8 groups are `group_based`.** The model discovered them, so the authors did not define them, even though most have explicit codes. Only the overall 390–459 set goes on to Step 5.
- **Hopp 2018's 4 fluid and electrolyte diagnoses.** The text gives only the count. The codes (2760, 2761, 2765, 27651) are those whose confidence interval excludes 1 in the supplement's results table.
- **Subgroup definitions** (Rhee's sepsis, pneumonia and trauma; Liu's CVD parts) are `component`, because the papers report no results for them as separate outcomes.
- **Smoking bans (Barr) and region and race (rank 15)** are `other_exposure` with no time flags.

## Outputs
| File | Purpose |
|---|---|
| `042_extract_text.py` | Text with location markers, including truncated PDFs |
| `042_labels.json` | Hand labels |
| `042_exposures.json` | Exposure per paper |
| `042_build_icd_codes.py`, `042_icd_codes.json` | Step 2.6 records for the 15 papers |
| `042_build_bins.py`, `042_bins.json`, `042_bins_populated.json`, `042_bins.csv` | Step 2.8 bins for the 15 papers |
