# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with content in this folder.

Ignore files starting with an underscore. Do not read them. Before moving forwards when you start, give me a thumbs up that you understand this every time we resume a session

If there is a need to install software for claude to work, prefer python libraries over other options. If a python package is required at any point, create an environment specific for this folder and a create a requirements.txt file. Before moving forwards when you start, give me a thumbs up that you understand this every time we resume a session.

Do not ever reach data or files outside of the root of this project, except Claude's memory and plan files, or other login files at the home folder. Before moving forwards when you start, give me a thumbs up that you understand this every time we resume a session.

## Project Descriptio

I need to generate a list of outcomes associated with pollution and extreme weather, and for each a validated list of icd9-10. The final list, should be stored as a yaml that will be ingested into medpar_outcomes https://github.com/NSAPH-Data-Processing/medpar_outcomes. Specifically, it should be formatted as francesca_claudio_icdranges01.yaml.



## Steps

We will work step by step. Write an md for each step that, update your context to reflect content/decisions we establish in those md.

Naming of these md files: the number prefix is the step number times ten, written with three
characters. `Step 1` → `010_*.md`, `Step 2` → `020_*.md`, `Step 2.5` → `025_*.md`,
`Step 10.5` → `105_*.md`.

Before moving forwards when you start, give me a thumbs up that you understand this every time we resume a session.

### Step 1: check previous list
First we will check  icd9 and icd 10 mappings from a previously generated document. 

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

### Step 2.8 "Bin" definitions
Define our own list of outcome bins. Bins are a classification of the Step 2.6 code sets, not a
checklist to fill.
- Start from the reference list below, and add a bin for every relevant outcome in the Step 2.6
  papers that the list lacks (e.g. all-cardiovascular and all-respiratory composites,
  heat-related illness, peripheral vascular disease, chronic kidney disease). Every
  author-defined code set must fall into at least one bin; list any that do not, with the reason.
  Keep reference bins that have no paper evidence, marked as such.
- Map each code set to its bin(s), with a scope: `exact`, `narrower` (part of the bin) or
  `broader` (the bin plus other conditions).
- Classify each paper's exposure, and record it per code set and per bin as JSON attributes:
  `air_pollution`, `extreme_heat`, `extreme_weather` (e.g. tropical cyclones, drought, wildfire,
  snowstorms), `long_term`, `short_term` (true/false, from the study design: e.g. annual
  averages vs. daily lags or event days), plus `other_exposure` for papers whose exposure is
  none of these (e.g. greenness, noise, policy). A bin's attributes are the union over its
  papers, with the supporting papers listed. Add notes on whether the bin is supported for
  long-term or short-term effects, and for air pollution or extreme weather.
- Output: the bins JSON, plus a CSV with one row per bin listing its code sets, papers and
  attributes.

Reference list:

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

### Step 4: Condense 025 and 035 
Build a unified shortlist from 025_shortlist.json and 035_shortlist.json, as the first step of
condensing Steps 2 and 3.
- One row per paper, matched by DOI, so papers on both lists appear once. Do not modify the
  Step 2.4, 2.5, 3.4 or 3.5 files.
- Keep the Step 2.5 and Step 3.5 ranks, and record which list(s) each paper came from.
- Add a unified rank: papers shortlisted in either step first, in Step 2.5 order, then the
  Step 3.5 papers.

### Step 4.1: Download shortlisted papers
For this step, we will override the python preference, and will allow other software usage. We will also allow you to manipulate other folder directories (for example, the Downloads folder).

You will guide me step by step so we work together in chrome. I can sign in to my institutional account, when the website allows, you can then perform downloads. I will assist when necessary.

Record the final status of each of the manually downloaded papers.

### Step 4.2
Apply step 2.6 and 2.8 to the manually downloaded papers

### Step 5: condense 
We should have a unified list of code sets from step 2.6, 3.6 and 4.2 that incorporates information from each paper only once, avoiding to add papers twice if they are both in Francesca and Danielle Google Scholars. 

The output is a yml file that is almost as simple as francesca_claudio_icdranges01.yaml. Note each item uses a short name for each code set. The new yaml will also include:
* `long_name` a long description of the outcome the codeset represents
* `criteria` for example `"principal"` vs. `"any diagnosis"` or `"not stated"` or others that could make sense like `"secondary"` or whatever
* `paper_id` which will list papers (or the folder names of the papers) that share the same codeset definition and criteria for a given outcome. 
* `treatment` which will take the following values in a list (that can be empty if none apply) `[air_pollution, extreme_weather, long_term, short_term]`. Heat would count as extreme_weather, and greenness, noise or policy papers would get an empty list unless they also fit a listed value.


Leave out group based code sets from outcome-wide papers. For example, do not include the outcomes from Parks 2021 or others that use ALL the CCS groups or CCW as an initial pool. Add CCS/CCW if explicit codes are included in the study and if the approach is not iterating the same model over multiple outcomes.

If icd codes are not available leave the range empty.

Keep ICD-9 only and ICD-10 only sets. 

Source of truth for codes, in this order:
1. The codes printed in the papers, with typos corrected (Step 5.3). These are never replaced by another source, except when a set is split in Step 5.3.
2. For a missing ICD version: the pairing in another paper that prints both ICD-9 and ICD-10 for the same codes, regardless of its criteria.
3. Where a paper names CCW, CCS or CCSR without printing the codes: the official list.
4. Only for an ICD-9-only or ICD-10-only set that cannot be paired with a paper's definition: the ICD-9 to ICD-10 crosswalk (GEMs).

Different criteria, as set in Step 5.1, are different entries.

Each of Steps 5.1 to 5.5 outputs a JSON, with the source of every code and any flags. The simple YAML is created in Step 5.6.

Steps 5.2 and 5.4 may download the official lists and crosswalks (CCW, CCS, CCSR, GEMs) into a git-ignored folder in this project. Record the version of each. Save a machine-readable version of each (CSV or JSON), which is committed with its source and version.

### Step 5.1: Runnable criteria
Each outcome needs a diagnosis position that can be run on the claims.
- Translate each `criteria` into the fields `get_outcomes.py` in `medpar_outcomes` reads:
  - principal diagnosis: `outcome_criteria: first_n`, `first_n: 1`
  - any of the first N diagnosis fields: `outcome_criteria: first_n`, `first_n: N`
  - any diagnosis, or principal or secondary diagnosis: `outcome_criteria: all`
- For `not stated`, use principal diagnosis for acute events and the first 10 fields for conditions often recorded as secondary (e.g. dementia, Parkinson's, CKD). Record that this was assigned, not taken from the paper.

### Step 5.2: Resolve CCS and CCW markers
Markers mean the paper names a definition without printing its codes. Replace them with codes from the official lists, and record the list and version:
- `CCW`: the CMS Chronic Conditions Warehouse algorithm.
- `CCS`: the AHRQ HCUP CCS table for ICD-9-CM.
- `CCSR`: the AHRQ HCUP CCSR table for ICD-10-CM.
- Sets with printed codes are not changed, including printed CCW lists.
- Sets with empty ranges stay out. List them with the reason.


### Step 5.3 Clean icd codes.
- note potential typos, support with some evidence.
- for the author defined icd9 and icd10 mappings, measure ICD-9 and ICD-10 map coverage in both directions. Determine a percentage measure. 
- when coverage is very low (e.g. `heat_illness`), split the set in two, one ICD-9 only and one ICD-10 only, each filled with the GEM mapping in Step 5.4.
- let's fix one by one manually together (like we did with manual downloads), record the decisions.

### Step 5.4: ICD-10 and ICD-9 coverage
Every outcome must have codes for the whole period, because ICD-10 replaced ICD-9 in October 2015.
- For ICD-9-only and ICD-10-only sets, fill only the missing version. First use the pairing from a paper that prints both versions, when its codes in the available version are identical, regardless of its criteria. The set keeps its own criteria. If papers give different pairings, the set takes each one, and the distinct definitions are all kept.
- If no paper gives a pairing, use the CMS General Equivalence Mappings (GEMs).
- Mark filled codes separately, with their source: the paper, or the mapping.
- A set split in Step 5.3 uses the GEM mapping, not a pairing.

### Step 5.5: Remove true duplicates
Merge outcomes with identical codes and criteria, and combine their `paper_id` and `treatment`. Keep every other distinct definition, even when definitions overlap.

### Step 5.6: Final YAML
Format the results of Step 5.5 as a YAML in the same format as `050_codesets.yaml`: short name, `long_name`, `criteria`, `outcome_criteria`, `first_n` (only with `outcome_criteria: first_n`), `paper_id`, `treatment`, `icd9`, `icd10`. Add a `note` only to the entries that need it (e.g. flagged mappings, assigned criteria). Entries without one omit the field.

### Step 6: Bins
Bins are just a reference that helps classify the code sets. Modify the bins definition to include as many relevant outcomes as possible from the condensed codeset yaml. We are interested in air pollution and extreme weather related outcomes overall. The bins should distinguish between "long-term effect" and "short-term effect" related outcomes.

Store the bins in a very simple yaml which should include a short name for each bin to identify each item, and:
* a long name
* a list containing the short names of the icd code sets that belong to the bin. Split them in long_term and short_term lists of code set names to each bin.

### Recommended next steps: Checks after the counts are generated
Run once the counts exist, and report per outcome:
- Continuity across October 2015: flag jumps in the counts at the switch to ICD-10.
- Rare outcomes: national yearly counts and the share of zero ZCTA-days, against a minimum to be agreed.
- Near-identical outcomes: flag pairs that are almost perfectly correlated, for loss weighting and for holding out whole bins in evaluation.
- List the negative controls that the papers themselves use as such, each with its `paper_id`. Do not propose others. Store them in a separate YAML, not with the outcomes.
- We left out Medicaid outcomes, which could be incorporated.