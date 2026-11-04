"""Step 5.6: format the results of Step 5.5 as the final YAML, in the format of 050_codesets.yaml.

Input: 055_outcomes.json. Adds outcome_criteria, first_n (only with outcome_criteria: first_n) and a note (only where needed).

Output: 056_outcomes.yaml
Run: .venv/bin/python 056_final_yaml.py
"""
import json
import re

import yaml

IN = "055_outcomes.json"
OUT = "056_outcomes.yaml"


def note(m):
    """Only the Step 5.3 decisions and assigned criteria. The source of every code and the GEM counts stay in 055_outcomes.json."""
    decisions = {re.sub(r" \(decision \d+\)$", "", n) for n in m["decision_notes"]}  # the same note from merged sets appears once
    parts = ["Typo corrected: %s." % f for f in m["typo_fixes"]] + sorted(decisions)
    if m["criteria_assigned_for"]:
        parts.append("Criteria not stated by %d paper(s), assigned here." % len(m["criteria_assigned_for"]))
    return " ".join(parts)


def main():
    out = {}
    for key, m in json.load(open(IN, encoding="utf-8")).items():
        e = {"long_name": m["long_name"], "criteria": m["criteria"], "outcome_criteria": m["outcome_criteria"]}
        if m["outcome_criteria"] == "first_n":
            e["first_n"] = m["first_n"]
        e.update(paper_id=m["paper_id"], treatment=m["treatment"], icd9=m["icd9"], icd10=m["icd10"])
        n = note(m)
        if n:
            e["note"] = n
        out[key] = e
    with open(OUT, "w", encoding="utf-8") as f:
        blocks = []
        for key, e in out.items():
            lines = ["%s:" % key]
            for k in ("long_name", "criteria", "outcome_criteria", "first_n"):
                if k in e:
                    lines.append("  %s: %s" % (k, json.dumps(e[k], ensure_ascii=False)))
            lines.append("  paper_id:")
            lines += ["    - %s" % json.dumps(p) for p in e["paper_id"]]
            lines += ["  %s: %s" % (k, json.dumps(e[k], ensure_ascii=False)) for k in ("treatment", "icd9", "icd10")]
            if "note" in e:
                lines.append("  note: %s" % json.dumps(e["note"], ensure_ascii=False))
            blocks.append("\n".join(lines))
        f.write("\n\n".join(blocks) + "\n")
    assert yaml.safe_load(open(OUT, encoding="utf-8")) == out, "the YAML does not read back the same"
    assert all(e["icd9"] and e["icd10"] for e in out.values())
    print("wrote %s: %d outcomes, %d with a note; all have ICD-9 and ICD-10" % (OUT, len(out), sum("note" in e for e in out.values())))
    for c in sorted({e["criteria"] for e in out.values()}):
        print("  %-40s %d" % (c, sum(e["criteria"] == c for e in out.values())))


if __name__ == "__main__":
    main()
