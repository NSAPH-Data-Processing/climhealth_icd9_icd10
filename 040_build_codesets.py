"""Step 4c: unified code sets: outcomes for which we have ICD codes.

Inputs: 040_outcomes.json (outcome ids, flags), 026/036_icd_codes.json (codes), 026_ccs_tables.json
(Parks 2021 table: ICD-9 codes of every single-level AHRQ CCS group).

Three kinds of code sets (source_type):
  author_defined  the paper lists ICD codes (explicit_codes; Parks table excluded)
  ccs_table       a Parks 2021 CCS group (level 3) or cause (level 1 = union of its groups)
  ccs_resolved    an outcome named only by single-level CCS group number(s) (classification_ref,
                  e.g. Wei 2019 'septicemia (CCS 2)'); its ICD-9 codes are the Parks table's codes
                  for those groups. Bobb 2014 names groups without numbers; CCS_BY_NAME maps them.
                  Multi-level CCS (Thomas 2022) and whole-classification scans are not resolved.
Flags per code set: ccs, ccs_groups, ccs_level, parks_analyzed (Parks group used in its own
level-3 analysis), icd9/icd10 availability, diagnosis_position, role, outcome_wide_scan,
suspect (printed codes that look wrong), code_format (CCS-derived codes are printed without the
decimal point, e.g. 4280 = 428.0), and the paper's exposure flags.

Output: 040_codesets.json
Run: .venv/bin/python 040_build_codesets.py
"""
import json
import re

PARKS = "10_1038_s41467_021_21777_1"
BOBB = "10_1001_jama_2014_15715"
CCS_BY_NAME = {  # Bobb 2014: CCS names given, numbers not given
    (BOBB, "fluid and electrolyte disorders"): ["55"], (BOBB, "renal failure"): ["157"],
    (BOBB, "urinary tract infection"): ["159"], (BOBB, "septicemia"): ["2"],
    (BOBB, "congestive heart failure"): ["108"],
}
SUSPECT = {  # outcome id -> note (codes kept as printed; see the Step 2.6/3.6 notes)
    "10_1038_jes_2013_39::emergency respiratory disease hospital admissions":
        "printed 490-448 and 480-497 (likely 490-492 and 480-487)",
    "10_1097_ede_0000000000001265::CVD-related hospitalizations (first)": "printed 390 to 495 (likely 390-459)",
    "10_1016_j_scitotenv_2020_142524::urinary tract infection": "printed 559 (likely 599.0)",
    "10_1016_j_envint_2025_109617::second admission with ischemic stroke": "ICD-10 printed I163 (likely I63)",
    "10_1016_j_envres_2025_122779::ischemic stroke": "ICD-10 printed I163 (likely I63)",
    "10_1097_ee9_0000000000000395::heat-related illness":
        "ICD-10 printed T67.3-67.5, narrower than its ICD-9 992.0-992.9 (T67.0-T67.9)",
    "10_1016_j_envint_2021_106737::all CVD": "'all CVD' printed as 390-429 subsets only (no 430-459)",
}


def ccs_numbers(cls):
    """Single-level CCS group numbers in a classification string, or None if not resolvable."""
    if not cls or "multi-level" in cls or "not given" in cls or "CCS" not in cls:
        return None
    part = re.split(r";\s*(?:ICD-10|CCSR)", cls)[0]
    part = re.sub(r"ICD-?\d+(-CM)?", "", part)
    nums = []
    for a, b in re.findall(r"(\d+)\s*[–-]\s*(\d+)", part):
        nums += [str(n) for n in range(int(a), int(b) + 1)]
    part = re.sub(r"\d+\s*[–-]\s*\d+", "", part)
    nums += re.findall(r"\d+", part)
    return nums or None


def main():
    outcomes = {o["id"]: o for o in json.load(open("040_outcomes.json", encoding="utf-8"))["outcomes"]}
    codes = {}
    for f in ("026_icd_codes.json", "036_icd_codes.json"):
        for p in json.load(open(f, encoding="utf-8"))["papers"]:
            if p["fulltext_status"] != "no_fulltext":
                codes[p["slug"]] = {o["outcome_name"]: o for o in p["outcomes"]}
    groups = {g["ccs_level3"]: g for g in json.load(open("026_ccs_tables.json", encoding="utf-8"))["parks2021"]["groups"]}

    sets, unresolved = [], []
    for oid, o in outcomes.items():
        if o["codes_status"] not in ("explicit_codes", "classification_ref"):
            continue
        src = codes[o["paper"]][o["outcome_name"]]
        base = {"outcome_id": oid, "paper": o["paper"], "paper_label": o["paper_label"],
                "outcome_name": o["outcome_name"], "role": o["role"], "outcome_wide_scan": o["outcome_wide_scan"],
                "diagnosis_position": src["diagnosis_position"], "flags": o["flags"]}
        if o["codes_status"] == "explicit_codes":
            icd9, icd10 = list(src["icd9"]), list(src["icd10"])
            rec = dict(base, id=oid, source_type="author_defined", ccs=False, ccs_groups=[], ccs_level=None,
                       parks_analyzed=None)
            if o["paper"] == PARKS:
                m = re.match(r"AHRQ (?:multi-level )?CCS level (\d)(?: group|, cause) (\d+)", src["classification"])
                level, num = m.group(1), m.group(2)
                comps = src.get("components_ccs_level3") or []
                for g in comps:
                    icd9 += groups[g]["icd9_codes"]
                rec.update(source_type="ccs_table", ccs=True, ccs_level=int(level),
                           ccs_groups=comps if level == "1" else [num],
                           parks_analyzed=groups[num]["in_level3_analysis"] if level == "3" else True)
            notes = [SUSPECT[oid]] if oid in SUSPECT else []
            if src.get("note") and "lack a leading digit" in src["note"]:
                notes.append(src["note"][src["note"].index("Printed codes"):])
            rec.update(icd9=icd9, icd10=icd10, suspect=notes, evidence=src["evidence"])
        else:
            nums = CCS_BY_NAME.get((o["paper"], o["outcome_name"])) or ccs_numbers(src["classification"])
            if not nums:
                unresolved.append({"outcome_id": oid, "classification": src["classification"]})
                continue
            missing = [n for n in nums if n not in groups]
            icd9 = [c for n in nums if n in groups for c in groups[n]["icd9_codes"]]
            rec = dict(base, id=oid + "::ccs", source_type="ccs_resolved", ccs=True, ccs_groups=nums, ccs_level=3,
                       parks_analyzed=None, icd9=icd9, icd10=[],
                       resolved_by="name" if (o["paper"], o["outcome_name"]) in CCS_BY_NAME else "number",
                       ccs_groups_not_in_table=missing,
                       suspect=["CCS groups not in the Parks table: %s" % missing] if missing else [],
                       evidence=src["evidence"])
        rec["code_format"] = "ICD-9 without decimal point (Parks table)" if rec["ccs"] else "as written in the paper"
        rec["icd_versions"] = [v for v, k in (("ICD-9", "icd9"), ("ICD-10", "icd10")) if rec[k]]
        rec["n_icd9"], rec["n_icd10"] = len(rec["icd9"]), len(rec["icd10"])
        sets.append(rec)

    assert len({s["id"] for s in sets}) == len(sets)
    with open("040_codesets.json", "w", encoding="utf-8") as f:
        json.dump({"sources": ["040_outcomes.json", "026_icd_codes.json", "036_icd_codes.json", "026_ccs_tables.json"],
                   "unresolved_classification_outcomes": unresolved, "codesets": sets}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    cnt = {}
    for s in sets:
        cnt[s["source_type"]] = cnt.get(s["source_type"], 0) + 1
    print("wrote 040_codesets.json: %d code sets %s; %d classification outcomes not resolved"
          % (len(sets), cnt, len(unresolved)))
    au = [s for s in sets if s["source_type"] == "author_defined" and s["role"] == "outcome"]
    print("  author-defined (role outcome): %d from %d papers; with ICD-10: %d; suspect: %d"
          % (len(au), len({s["paper"] for s in au}), sum(bool(s["icd10"]) for s in au), sum(bool(s["suspect"]) for s in sets)))
    for u in unresolved:
        print("  unresolved:", u["outcome_id"][:70], "|", u["classification"])


if __name__ == "__main__":
    main()
