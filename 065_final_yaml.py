"""Step 6.5: format the results of Step 6.4 as the final YAML, in the format of 050_codesets.yaml.

Input: 064_outcomes.json. Adds outcome_criteria, first_n (only with outcome_criteria: first_n) and a note (only where needed).

Output: 065_outcomes.yaml
Run: .venv/bin/python 065_final_yaml.py
"""
import json

import yaml

IN = "064_outcomes.json"
OUT = "065_outcomes.yaml"
# typos corrected in Step 5 (FIXES in 050_build_codesets.py): paper, printed code, code used
STEP5_TYPOS = [("10_1038_jes_2013_39", "490-448", "490-492"), ("10_1038_jes_2013_39", "480-497", "480-487"),
               ("10_1097_ede_0000000000001265", "390 to 495", "390-459"), ("10_1016_j_scitotenv_2020_142524", "559", "5990"),
               ("10_1016_j_envint_2025_109617", "I163", "I63"), ("10_1016_j_envres_2025_122779", "I163", "I63"),
               ("10_1097_ee9_0000000000000519", "332/332.0", "3320")]


def step5_typos(m):
    """Step 5 corrections for an outcome: its paper is in paper_id, and its code list has the corrected code."""
    hits = [t for t in STEP5_TYPOS if t[0] in m["paper_id"] and t[2] in m["icd9"] + m["icd10"]]
    return ["Typo corrected: %s prints %s, read as %s." % (slug, printed, used) for slug, printed, used in hits], hits


def note(m):
    parts = step5_typos(m)[0]
    for version, label in (("icd9", "ICD-9"), ("icd10", "ICD-10")):
        sources = m[version + "_sources"]
        if "printed" in sources:
            continue
        parts.append("%s codes not printed; source: %s." % (label, "; ".join(sources)))
    if m["criteria_assigned_for"]:
        parts.append("Criteria not stated by %d paper(s), assigned here." % len(m["criteria_assigned_for"]))
    parts += ["Flag: %s." % f for f in m["flags"]]
    return " ".join(parts)


def main():
    out, found = {}, []
    for key, m in json.load(open(IN, encoding="utf-8")).items():
        found += step5_typos(m)[1]
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
    assert sorted(set(found)) == sorted(STEP5_TYPOS), "a Step 5 typo is not in any note: %s" % (set(STEP5_TYPOS) - set(found))
    print("  Step 5 typos in notes: %d placements of %d corrections" % (len(found), len(STEP5_TYPOS)))
    print("wrote %s: %d outcomes, %d with a note; all have ICD-9 and ICD-10" % (OUT, len(out), sum("note" in e for e in out.values())))
    print("  printed in both versions:", sum("note" not in e or "not printed" not in e["note"] for e in out.values()))
    for c in sorted({e["criteria"] for e in out.values()}):
        print("  %-40s %d" % (c, sum(e["criteria"] == c for e in out.values())))


if __name__ == "__main__":
    main()
