"""Step 1: build 010_icd_mappings.json from Dominici_hospitalization_ICD_codes.md.pdf.

Rows are transcribed verbatim from the rendered PDF tables (the PDF text layer drops
some dots/dashes, e.g. "9929", "T670-T679"). Each raw ICD cell is then parsed into
structured code specs; cells that are not plain code lists are parsed via explicit
overrides and flagged with a parse_status.

Stdlib only.  Run:  python3 010_extract_mappings.py
"""
import json
import re

SOURCE = "Dominici_hospitalization_ICD_codes.md.pdf"
OUT = "010_icd_mappings.json"

# (outcome, icd9_raw, icd10_raw, publications_raw, page)
SECTION1 = [
    ("Cardiovascular disease (all-cause)", "390–459", "I00–I99",
     "Dominici et al. 2006 JAMA (#57); Peng et al. 2008 JAMA (#78); Bravo et al. 2016 (#172); Chen et al. 2021 (#245, #253); Sun et al. 2024 BMJ (#304); Yazdi et al. 2025 (#323)", 2),
    ("Respiratory disease (all-cause)", "460–519", "J00–J99",
     "Dominici et al. 2006 JAMA (#57); Peng et al. 2008 JAMA (#78); Bell et al. 2009 (#89, #94); Bravo et al. 2016 (#172); Anderson et al. 2013 (#132)", 2),
    ("Ischemic heart disease", "410–414", "I20–I25",
     "Dominici et al. 2006 JAMA (#57)", 2),
    ("Myocardial infarction (acute)", "410", "I21–I22",
     "Barr et al. 2012 (#125, smoking bans); Schwartz et al. 2023 (#284)", 2),
    ("Congestive heart failure", "428", "I50",
     "Symons et al. 2006 (#61); Dominici et al. 2006 JAMA (#57)", 2),
    ("Cardiac arrhythmia", "427", "I47–I49",
     "Dominici et al. 2006 JAMA (#57, cardiovascular admissions category)", 2),
    ("Cerebrovascular disease / stroke", "430–438", "I60–I69",
     "Dominici et al. 2006 JAMA (#57, cardiovascular category)", 2),
    ("Carbon monoxide–associated cardiovascular admissions", "410–414, 427–428, 786.5 (chest pain)", "I20–I25, I47–I50, R07.9",
     "Bell et al. 2009, Circulation (#92)", 2),
    ("Chronic obstructive pulmonary disease (COPD)", "490–492, 494–496", "J40–J44",
     "Peng et al. 2008 JAMA (#78); Bell et al. 2009 (#89, #94)", 2),
    ("Asthma", "493", "J45",
     "Wei et al. 2022, AJRCCM (#271); Bell et al. 2009 (#89, #94)", 2),
    ("Pneumonia / acute respiratory infection", "480–487", "J09–J18",
     "Peng et al. 2008 JAMA (#78, respiratory category)", 2),
    ("Acute respiratory distress syndrome (ARDS)", "518.82", "J80",
     "Rhee et al. 2019 (#202); Rhee et al. 2020 (#229)", 3),
    ("Cardiorespiratory hospitalizations (combined CVD + respiratory)", "390–519", "I00–I99, J00–J99",
     "Yan et al. 2021 (#242, tropical cyclones); Thomas et al. 2020/2022 (#220, #268)", 3),
    ("Diabetes-related hospitalization/ exacerbation", "250", "E10–E14",
     "Zanobetti et al. 2014 (#148)", 3),
    ("Neurological disorders (general)", "320–359", "G00–G99",
     "Zanobetti et al. 2014 (#148)", 3),
    ("Chronic debilitating brain disorders", "290–294, 320–359", "F01–F09, G00–G99",
     "Yitshak-Sade et al. 2020 (#238)", 3),
    ("Dementia / Alzheimer's disease", "290.0, 331.0", "F01–F03, G30",
     "Lee et al. 2019 (#212); Qin et al. 2024 (#311); Dong et al. 2025 (#320); Spoto et al. 2025 (#339)", 3),
    ("Acute kidney injury / kidney disease", "584, 585", "N17, N18",
     "Lee et al. 2023, EHP (#282)", 3),
    ("Psychiatric hospital admissions", "290–319", "F01–F99",
     "Qiu et al. 2022, Lancet Planetary Health (#270)", 3),
    ("Alcohol- and substance-related disorders", "291, 303–305", "F10–F19",
     "Parks et al. 2023, Communications Medicine (#293)", 3),
    ("Psychiatric hospitalizations (boom–bust economic/oil-gas exposure context)", "290–319", "F01–F99",
     "Willis et al. 2025 (#331)", 3),
    ("Interpersonal violence–related visits (assault)", "E960–E969", "X92–Y09",
     "Parks et al. 2026 (#341)", 3),
    ("Self-inflicted violence–related visits", "E950–E959", "X71–X83",
     "Parks et al. 2026 (#341)", 3),
    ("Heat stroke / heat-related illness", "992.0 (heat stroke), 992.0–992.9 (heat illness spectrum)", "T67.0XXA (heatstroke), T67.0–T67.9",
     "Wang et al. 2016 (#171); Bobb et al. 2014, JAMA (#153); Hopp et al. 2018 (#190)", 3),
    ("Heat-related respiratory hospitalization", "460–519", "J00–J99",
     "Anderson et al. 2013, AJRCCM (#132)", 4),
    ("Cause-specific hospitalizations related to extreme heat (renal, respiratory, CVD, diabetes, etc., multi-cause)",
     "Multiple (250, 390–519, 584–586)", "Multiple (E10–E14, I00–I99, J00–J99, N17–N19)",
     "Bobb (Obermeyer) et al. 2014, JAMA \"Cause-Specific Risk of Hospital Admission Related to Extreme Heat\" (#153)", 4),
    ("Wildfire smoke–associated hospital admissions (respiratory/ cardiovascular)", "460–519, 390–459", "J00–J99, I00–I99",
     "Liu et al. 2016 (#173); Liu et al. 2017 (#175)", 4),
    ("Snowstorm-associated, cause-specific hospital admissions", "Varies by cause (injury, cardiovascular, respiratory)", "Varies (S00–T88, I00–I99, J00–J99)",
     "Bobb et al. 2016, AJE \"Time-course of Cause-Specific Hospital Admissions during Snowstorms\" (#177)", 4),
    ("Drought-associated hospital admissions/ mortality (older adults)", "Not cause-specific in abstract; general morbidity", "—",
     "Berman et al. 2017, Lancet Planetary Health (#181)", 4),
    ("Tropical cyclone–associated hospitalization (older adults, general and cardiorespiratory)", "390–519", "I00–I99, J00–J99",
     "Parks et al. 2021, Nature Communications (#240); Yan et al. 2021 (#242); Burrows et al. 2023 (#281)", 4),
    ("Hurricane-associated ED visits (by age and cause)", "Multiple, cause-stratified", "Multiple",
     "Weinberger et al. 2021, AJE (Hurricane Sandy) (#244)", 4),
    ("Volcanic SO2 plume–associated respiratory morbidity", "460–519 (esp. 493 asthma, 490–496 COPD)", "J00–J99 (esp. J45, J40–J44)",
     "Carlsen et al. 2021 (#250, #252)", 4),
    ("Emergency hospital admissions for CVD and ambient CO", "See CVD row above", "See CVD row above",
     "Bell et al. 2009, Circulation (#92)", 4),
    ("Hospital admissions and PM2.5 chemical composition (cardiorespiratory)", "390–519", "I00–I99, J00–J99",
     "Bell et al. 2009 (#89, #94); Bell et al. 2014 (#136)", 4),
    ("Emergency hospital admissions, primary organic particles (elderly, cardiorespiratory)", "390–519", "I00–I99, J00–J99",
     "Kioumourtzoglou et al. 2013 (#134)", 4),
    ("Non-respiratory infection hospital admissions (long-term PM2.5, included for completeness)",
     "001–139, 320–326, 590, etc. (infection-specific)", "A00–B99 and site-specific infection codes",
     "Feng et al. 2024, Nature Communications (#303/#309)", 5),
    ("Second cardiovascular event hospital admissions", "410–414, 428, 430–438", "I20–I25, I50, I60–I69",
     "Yazdi et al. 2025 (#323)", 5),
]

# (outcome, icd9_raw, icd10_raw, typical_exposure_raw, page)
SECTION2 = [
    ("Hypertensive crisis / hypertension", "401–405", "I10–I16", "Air pollution, heat", 6),
    ("Atrial fibrillation (specific arrhythmia)", "427.31", "I48.0–I48.9", "Air pollution, temperature", 6),
    ("Cardiac arrest", "427.5", "I46.2, I46.8, I46.9", "Ozone, PM2.5, extreme heat/cold", 6),
    ("Chronic bronchitis", "491", "J41–J42", "Air pollution", 6),
    ("Acute bronchitis", "466", "J20–J21", "Air pollution, cold weather", 6),
    ("Upper respiratory tract infection", "460–465", "J00–J06", "Cold weather, air pollution", 6),
    ("Otitis media", "381–382", "H65–H67", "Air pollution (pediatric)", 6),
    ("Conjunctivitis / eye irritation", "372.0", "H10", "Ozone, particulate matter, wildfire smoke", 6),
    ("Allergic rhinitis", "477", "J30", "Pollen, air pollution interaction", 6),
    ("Dehydration", "276.51", "E86.0", "Extreme heat", 6),
    ("Heat exhaustion / heat cramps", "992.3, 992.5–992.7", "T67.3, T67.2, T67.6–T67.8", "Extreme heat", 6),
    ("Hypothermia", "991.6", "T68", "Extreme cold", 6),
    ("Frostbite", "991.0–991.3", "T33–T34", "Extreme cold", 6),
    ("Cold exposure–related cardiovascular events", "410–414, 427–428", "I20–I25, I47–I50", "Cold weather", 6),
    ("Renal colic / kidney stones", "592", "N20", "Extreme heat, dehydration", 6),
    ("Sepsis / urinary tract infection (heat-related renal stress)", "038, 599.0", "A41, N39.0", "Extreme heat", 6),
    ("Rhabdomyolysis", "728.88", "M62.82", "Extreme heat", 6),
    ("Falls / weather-related injury (ice, snow)", "800–959 (injury codes), E880–E888", "S00–T88, W00–W19", "Snow/ice storms", 6),
    ("Carbon monoxide poisoning", "986", "T58", "Cold weather (heating equipment use), power outages", 6),
    ("Preterm birth / adverse birth outcomes", "644.2, 765", "O60, P07", "Air pollution (PM2.5, NO2), heat", 7),
    ("Low birth weight", "764", "P05", "Air pollution", 7),
    ("Vector-borne disease hospitalizations (e.g., dengue, West Nile virus)", "061, 066.4", "A90–A91, A92.3", "Temperature/climate variability", 7),
    ("Gastroenteritis / diarrheal disease", "558.9, 009", "A09, K52.9", "Extreme heat, flooding", 7),
    ("Mental health crisis visits (general, beyond psychiatric admission category)", "300–316", "F40–F48, F90–F98", "Heat, air pollution", 7),
    ("Suicide attempt–related ED visits", "E950–E959", "X71–X83, T14.91", "Heat", 7),
    ("Anxiety/mood disorder exacerbation", "296, 300", "F30–F39, F40–F41", "Air pollution, heat", 7),
    ("Wildfire smoke–specific asthma/ COPD exacerbation", "493, 491–492, 496", "J45, J41–J44", "Wildfire PM2.5", 7),
    ("All-cause emergency department visits (non-specific)", "—", "—", "Heat, air pollution (used as sensitivity outcome)", 7),
]

CODE = r"[A-Z]?\d{2,3}(?:\.[0-9A-Z]{1,4})?"
CODE_RE = re.compile(rf"^{CODE}$")
RANGE_RE = re.compile(rf"^({CODE})\s*[–-]\s*({CODE})$")
LABEL_RE = re.compile(r"^(.*?)\s*\(([^()]*)\)$")


def split_top(s):
    """Split on commas not inside parentheses."""
    out, depth, cur = [], 0, ""
    for ch in s:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def parse_item(item):
    label = None
    m = LABEL_RE.match(item)
    if m:
        item, label = m.group(1).strip(), m.group(2).strip()
    if CODE_RE.match(item):
        spec = {"type": "code", "code": item}
    elif RANGE_RE.match(item):
        a, b = RANGE_RE.match(item).groups()
        spec = {"type": "range", "start": a, "end": b}
    else:
        return None
    if label:
        spec["label"] = label
    return spec


def parse_cell(raw):
    """Return (specs, status). status: parsed | none."""
    if raw.strip() in {"—", ""}:
        return [], "none"
    specs = [parse_item(i) for i in split_top(raw)]
    if any(s is None for s in specs):
        return None, None
    return specs, "parsed"


def s(text):
    return parse_cell(text)[0]


# Cells that are not plain code lists: (specs, status, note)
OVERRIDES = {
    "Multiple (250, 390–519, 584–586)":
        (s("250, 390–519, 584–586"), "qualified", "Cell reads 'Multiple (...)'; codes listed are examples of multiple cause groups."),
    "Multiple (E10–E14, I00–I99, J00–J99, N17–N19)":
        (s("E10–E14, I00–I99, J00–J99, N17–N19"), "qualified", "Cell reads 'Multiple (...)'; codes listed are examples of multiple cause groups."),
    "Varies by cause (injury, cardiovascular, respiratory)":
        ([], "unspecified", "No ICD-9 codes given; varies by cause (injury, cardiovascular, respiratory)."),
    "Varies (S00–T88, I00–I99, J00–J99)":
        (s("S00–T88, I00–I99, J00–J99"), "qualified", "Cell reads 'Varies (...)'; codes varied by cause."),
    "Not cause-specific in abstract; general morbidity":
        ([], "unspecified", "Not cause-specific in abstract; general morbidity."),
    "Multiple, cause-stratified":
        ([], "unspecified", "Multiple, cause-stratified; no codes given."),
    "Multiple":
        ([], "unspecified", "Multiple; no codes given."),
    "460–519 (esp. 493 asthma, 490–496 COPD)":
        ([{"type": "range", "start": "460", "end": "519",
           "emphasis": [{"type": "code", "code": "493", "label": "asthma"},
                        {"type": "range", "start": "490", "end": "496", "label": "COPD"}]}],
         "parsed", "Emphasis codes are a subset of the main range."),
    "J00–J99 (esp. J45, J40–J44)":
        ([{"type": "range", "start": "J00", "end": "J99",
           "emphasis": [{"type": "code", "code": "J45"},
                        {"type": "range", "start": "J40", "end": "J44"}]}],
         "parsed", "Emphasis codes are a subset of the main range."),
    "See CVD row above":
        ([], "reference", "Refers to another row ('See CVD row above'); ambiguous whether the all-cause CVD row or the CO-associated CVD row."),
    "001–139, 320–326, 590, etc. (infection-specific)":
        (s("001–139, 320–326, 590"), "partial", "List is open-ended ('etc.'); described as infection-specific."),
    "A00–B99 and site-specific infection codes":
        (s("A00–B99"), "partial", "Plus unspecified 'site-specific infection codes'."),
    "800–959 (injury codes), E880–E888":
        ([{"type": "range", "start": "800", "end": "959", "label": "injury codes"},
          {"type": "range", "start": "E880", "end": "E888"}], "parsed", None),
}


def build_cell(raw):
    if raw in OVERRIDES:
        specs, status, note = OVERRIDES[raw]
    else:
        specs, status = parse_cell(raw)
        note = None
        if specs is None:
            raise ValueError(f"Unparsed cell, add override: {raw!r}")
    cell = {"raw": raw, "parse_status": status, "codes": specs}
    if note:
        cell["note"] = note
    return cell


def split_pubs(raw):
    pubs = []
    for p in [x.strip() for x in raw.split(";") if x.strip()]:
        pubs.append({"citation": p, "cv_numbers": re.findall(r"#(\d+)", p)})
    return pubs


def main():
    mappings = []
    for i, (outcome, i9, i10, pubs, page) in enumerate(SECTION1, 1):
        mappings.append({
            "id": f"S1-{i:02d}", "section": 1, "row": i, "page": page,
            "outcome": outcome,
            "icd9cm": build_cell(i9), "icd10cm": build_cell(i10),
            "publications_raw": pubs, "publications": split_pubs(pubs),
        })
    for i, (outcome, i9, i10, exposure, page) in enumerate(SECTION2, 1):
        mappings.append({
            "id": f"S2-{i:02d}", "section": 2, "row": i, "page": page,
            "outcome": outcome,
            "icd9cm": build_cell(i9), "icd10cm": build_cell(i10),
            "typical_exposure_raw": exposure,
            "typical_exposure": [x.strip() for x in split_top(exposure)],
        })

    doc = {
        "source": SOURCE,
        "title": "Causes of Hospitalization Linked to Short-Term Air Pollution / Weather Exposure",
        "subtitle": "Based on Dr. Francesca Dominici's peer-reviewed publications (last 15 years, 2011–2026)",
        "sections": {
            "1": "From Dr. Dominici's Publications",
            "2": "Additional ICD-9/ICD-10 Codes Associated with Short-Term Air Pollution or Weather "
                 "(Broader Environmental Epidemiology Literature — Not Necessarily in the CV)",
        },
        "schema": {
            "code_spec": "{type: 'code', code} | {type: 'range', start, end}; optional 'label' (parenthetical text "
                         "in the source) and 'emphasis' (subset codes flagged with 'esp.').",
            "parse_status": {
                "parsed": "All codes in the cell were captured.",
                "qualified": "Codes captured, but the cell qualifies them ('Multiple', 'Varies').",
                "partial": "Some codes captured; the cell is open-ended ('etc.', 'site-specific ...').",
                "unspecified": "No codes given in the cell.",
                "reference": "Cell refers to another row.",
                "none": "Cell is an em dash (—).",
            },
            "notation": "Codes and range dashes (–) kept exactly as printed; no normalization or expansion.",
        },
        "document_notes": [
            "Section 1 note: Several of these papers (e.g., #57, #78, #92, #89/#94, #136) report cardiovascular and "
            "respiratory hospital admissions as broad, pre-specified diagnostic categories (often built from CMS/Medicare "
            "claims) rather than single ICD codes — the ranges above reflect the standard groupings used in that literature "
            "(e.g., NMMAPS/Medicare cardiovascular and respiratory admission definitions).",
            "ICD-9-CM vs. ICD-10-CM: U.S. claims data (Medicare/Medicaid) transitioned from ICD-9-CM to ICD-10-CM on "
            "October 1, 2015. Papers using data before this date use ICD-9; papers using more recent data use ICD-10 or a crosswalk.",
            "\"Cardiovascular\" and \"respiratory\" admissions in air pollution epidemiology are frequently defined using "
            "standardized code groupings from the NMMAPS/Medicare literature (often built off the AHRQ Clinical "
            "Classifications Software or the ICD-9 ranges 390–459 and 460–519, respectively) rather than single diagnosis "
            "codes — this is the convention in most of Dr. Dominici's cardiorespiratory papers.",
            "Where a paper's exact ICD code list was not published in the abstract/title, the codes shown reflect standard "
            "definitions used in equivalent published methods (e.g., Medicare claims-based hospitalization studies).",
        ],
        "mappings": mappings,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {OUT}: {len(mappings)} mappings "
          f"(S1={len(SECTION1)}, S2={len(SECTION2)})")


if __name__ == "__main__":
    main()
