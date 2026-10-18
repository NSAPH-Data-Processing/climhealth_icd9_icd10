# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with content in this folder.

Ignore files starting with an underscore. Do not read them. Before moving forwards when you start, give me a thumbs up that you understand this.

If there is a need to install software for claude to work, prefer python libraries over other options. If a python package is required at any point, create an environment specific for this folder and a create a requirements.txt file. Before moving forwards when you start, give me a thumbs up that you understand this.

## Project Descriptio

I need to perform an extensive check of  icd9 and icd 10 mappings. Each mapping is assigned to an outcome. The set of mappings was created using public health papers from Francesca Dominici's research group. 

## Steps

We will work step by step. Write an md for each step that, update your context to reflect content/decisions we establish in those md.

Naming of these md files: the number prefix is the step number times ten, written with three
characters. `Step 1` → `010_*.md`, `Step 2` → `020_*.md`, `Step 2.5` → `025_*.md`,
`Step 10.5` → `105_*.md`.

Before moving forwards when you start, give me a thumbs up that you understand this.

### Step 1
Parse Dominici_hospitalization_ICD_codes.md.pdf to extract the inventory of icd mappings in the document. Store the mappings in json form. 

### Step 1.2
Parse only the publication list in a super simple json.

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