"""Step 5.1: give each Step 5 code set a diagnosis position that can be run on the claims.

Input: 050_codesets.yaml. Translates criteria into the outcome_criteria and first_n fields of medpar_outcomes/src/get_outcomes.py.
'not stated' is assigned: principal diagnosis, or the first 10 fields for conditions often recorded as secondary.

Output: 051_outcomes.json
Run: .venv/bin/python 051_runnable_criteria.py
"""
import json

import yaml

IN = "050_codesets.yaml"
OUT = "051_outcomes.json"
# code sets with criteria 'not stated' for conditions often recorded as secondary
SECONDARY = {"cerebral_degenerations", "dementia_no_codes"}
RUN = {"principal diagnosis": ("principal diagnosis", "first_n", 1),
       "any of the first 10 diagnosis fields": ("any of the first 10 diagnosis fields", "first_n", 10),
       "any of up to 25 diagnosis fields": ("any diagnosis", "all", None),
       "principal or secondary diagnosis": ("any diagnosis", "all", None),
       "any diagnosis": ("any diagnosis", "all", None)}


def main():
    out = {}
    for key, s in yaml.safe_load(open(IN, encoding="utf-8")).items():
        assigned = s["criteria"] == "not stated"
        printed = "any of the first 10 diagnosis fields" if assigned and key in SECONDARY else "principal diagnosis" if assigned else s["criteria"]
        criteria, outcome_criteria, first_n = RUN[printed]
        out[key] = {"long_name": s["long_name"], "criteria_in_step5": s["criteria"], "criteria": criteria, "criteria_assigned": assigned,
                    "outcome_criteria": outcome_criteria, "first_n": first_n, "paper_id": s["paper_id"], "treatment": s["treatment"],
                    "icd9": s["icd9"], "icd10": s["icd10"]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote %s: %d sets, %d with assigned criteria" % (OUT, len(out), sum(s["criteria_assigned"] for s in out.values())))
    for c in sorted({s["criteria"] for s in out.values()}):
        print("  %-40s %d" % (c, sum(s["criteria"] == c for s in out.values())))


if __name__ == "__main__":
    main()
