# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with content in this folder.

Ignore files starting with an underscore. Do not read them. Before moving forwards when you start, give me a thumbs up that you understand this every time we resume a session

If there is a need to install software for claude to work, prefer python libraries over other options. If a python package is required at any point, create an environment specific for this folder and a create a requirements.txt file. Before moving forwards when you start, give me a thumbs up that you understand this every time we resume a session.

Do not ever reach data or files outside of the root of this project, except Claude's memory and plan files, or other login files at the home folder. Before moving forwards when you start, give me a thumbs up that you understand this every time we resume a session.

## Project Descriptio

I need to perform an extensive check of  icd9 and icd 10 mappings. Each mapping is assigned to an outcome. The set of mappings was created using public health papers from Francesca Dominici's research group. 

Ultimately we should have a list of outcomes associated with pollution and heat, and for each a validated list of icd9-10. 

## Steps

We will work step by step. Write an md for each step that, update your context to reflect content/decisions we establish in those md.

Naming of these md files: the number prefix is the step number times ten, written with three
characters. `Step 1` → `010_*.md`, `Step 2` → `020_*.md`, `Step 2.5` → `025_*.md`,
`Step 10.5` → `105_*.md`.

Before moving forwards when you start, give me a thumbs up that you understand this every time we resume a session.

### Step 1
Parse Dominici_hospitalization_ICD_codes.md.pdf to extract the inventory of icd mappings in the document. Store the mappings in json form. 

### Step 1.2
Parse only the publication list in a super simple json.

### Step 1.3
Check whether the Dominici_CV_updated_10132026.pdf numbered papers match the CV numbers in the document. 

### Step 2
Independently from Step 1 mappings, pull out an actual publication list from Francesca Dominici Google Scholar.

### Step 2.1
Create a script that pulls out citation .bib entries for each off the publications in the 020 json when possible. Null when not found.

### Step 2.2
Extract abstracts for as many of the publications as possible. Null when not found.

### Step 2.3
For each publication with a non-null, unflagged abstract (Step 2.2), identify whether it uses
CMS Medicare data (`uses_medicare`) and whether it uses CMS Medicare defined outcomes different
than mortality and all-cause hospitalizations (`outcome: True`). Record the outcome names, a short
evidence quote, and `uncertain: True` when the abstract is not enough to decide. Publications
without a usable abstract get `outcome: null`.

### Step 2.4
Fetch the full text and supplements of the papers whose ICD codes we will check.
- Scope: unique papers (by DOI) from Step 2.3 with `uses_medicare: True`, `outcome: True` and
  `uncertain: False`. Drop conference abstracts (e.g. ISEE abstracts `10.1289/isee*`,
  Environmental Epidemiology meeting abstracts `10.1097/01.ee9*`, journal supplement abstracts);
  list what was dropped and why.
- Sources, automated only: Europe PMC / PMC full text (JATS XML) and supplementary files, then
  open-access PDFs located through OpenAlex. No Unpaywall (it requires an email) and no manual
  downloads.
- Store full texts and supplements in a git-ignored `papers/` folder (copyrighted material is not
  committed). Commit only a manifest: one record per paper with ids (DOI, PMID, PMCID), the
  full-text source and format, the list of supplement files, and a status (`fulltext`,
  `fulltext_no_supplements`, `no_fulltext`). Papers without an accessible full text stay in the
  manifest with `no_fulltext`.

### Step 2.5
Prepare a short, prioritized shortlist of documents for the user to try to download manually
(e.g. through a library account). Candidates are the Step 2.4 gaps: papers with `no_fulltext`
and papers whose referenced supplements could not be fetched (`supplements_missing`). Rank them
by how much they matter for the ICD check (e.g. cited in the Step 1 PDF, the available text
points to the missing supplement for the code list, outcomes not covered by other fetched
papers), and keep the list short. For each item give: rank, the exact document to get (paper or
named supplement file), a link (DOI / PMC page), why it matters, and the `papers/<slug>/` folder
to save it in. Downloaded files will be registered in the Step 2.4 manifest.

### Step 2.6
- Filter the papers that use MedPAR (inpatient admissions) and/or fee-for-service claims; record
  the data source and a quote supporting it.
- For each `outcome name` (taken from the paper's methods, mapped back to the Step 2.3
  `outcome_names`), identify whether the paper lists the ICD codes (ICD-9 and/or ICD-10) used to
  tag the inpatient hospitalizations. Record:
  - `codes_status`: `explicit_codes` (codes listed), `classification_ref` (a named grouping such
    as CCS or CCW categories, without codes), `cites_prior_paper` (definition taken from a cited
    paper), `not_listed`.
  - the codes as written, the ICD version(s), and the diagnosis position when stated (principal
    vs. any).
  - `evidence`: the file, the location (page number for PDFs; section, table/figure number, or
    supplement number/table), and a short quote.
- Papers that scan many disease groups at once (outcome-wide studies, e.g. 214 CCS groups):
  extract every group, and populate the same json entries.

### Step 2.7
Build one check table with one row per Step 1 mapping. Show the Step 1 ICD-9/ICD-10 codes next to
the codes found (Step 2.6) in the papers that row cites, with a per-paper and a per-row verdict
(match / match_category / differs / not_comparable / no_evidence). The CV number → paper
crosswalk and the row → outcome choices are made by hand. Uncited papers with the same outcome
may be shown as context, but they do not change the verdict. Deliver a CSV for review.

### Step 2.8 "Bin" definition check
We want to identify relevant outcome categories or bins from the publications. Use the list below as reference, check if we can populate all of these outcomes from the publications in step 2. 

```
# Respiratory

* Asthma exacerbations
* COPD exacerbations
* Bronchiectasis
* Pneumonia and some other respiratory infections
* Respiratory failure, insufficiency, or arrest
* Upper respiratory infections

# Cardiovascular and blood-vessel conditions

* Heart attack (acute myocardial infarction)
* Ischemic heart disease and coronary atherosclerosis
* Heart failure
* Abnormal heart rhythms (arrhythmias/dysrhythmias)
* Cardiac arrest
* Hypertensive heart disease
* Stroke, including ischemic and hemorrhagic stroke
* Blood clots and related conditions, including phlebitis, thrombophlebitis, and thromboembolism
* Retinal artery occlusion, a blockage of blood flow to the eye

# Neurological and mental health
* Parkinson’s disease
* Dementia, including Alzheimer’s disease
* Depression-related hospital visits or admissions in some studies
* Stroke and other cerebrovascular conditions

# Kidney, metabolic, and fluid-balance conditions
* Acute or unspecified kidney failure
* Fluid and electrolyte disorders
* Diabetes with complications

# Infections and other reported admission categories

* Sepsis/septicemia
* Urinary tract infections
* Skin and soft-tissue infections
* Pneumocystis pneumonia in some people with HIV or other underlying conditions
* Intestinal obstruction
``` 

### Step 3
Repeat all the steps in 2 but for Danielle Braun's Google scholar. Try to produce the same files that are gerenerated in step 2, except the name of output files should be numbered like 03x_xxxx.xx. 