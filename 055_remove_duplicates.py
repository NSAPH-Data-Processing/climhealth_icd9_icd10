"""Step 5.5: merge outcomes with identical codes and criteria, and combine their paper_id and treatment.

Input: 054_outcomes.json. Codes are compared after expansion to valid codes, so F04-F05 equals F04 + F05.
Keeps the codes as printed when any merged entry has them. Short names lose their version and criteria suffixes unless
that makes two outcomes share a name.

Output: 055_outcomes.json
Run: .venv/bin/python 055_remove_duplicates.py
"""
import importlib.util
import json
import re

IN = "054_outcomes.json"
OUT = "055_outcomes.json"
TREATMENT = ["air_pollution", "extreme_weather", "long_term", "short_term"]
# Step 5 names that describe a printed code corrected in Step 5.3
CORRECTED_NAMES = {"cvd_390_495", "stroke_ischemic_i163", "resp_printed_490_448", "parkinson_332_or_3320", "uti_559"}
RENAME = {"uti_559": ("uti", "Urinary tract infection (ICD-9 599.0)")}

_spec = importlib.util.spec_from_file_location("step54", "054_icd_coverage.py")
step54 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(step54)


def rank(key, s):
    """Prefer entries with more printed code versions as the one that names the merged outcome, and not a name for a corrected code."""
    return (-sum(s[v + "_source"] == "printed" for v in ("icd9", "icd10")), key in CORRECTED_NAMES)


def base_name(key):
    if re.search(r"__icd(9|10)$", key):  # the two parts of a set split in Step 5.3 keep their names
        return key
    key = re.sub(r"__pair\d+$", "", key)
    key = re.sub(r"_(principal|not_stated|prim_sec|any|first10)$", "", key)
    return re.sub(r"_icd(9|10)$", "", key)


def criteria_suffix(s):
    return "first%d" % s["first_n"] if s["first_n"] and s["first_n"] > 1 else "principal" if s["first_n"] == 1 else "any"


def main():
    sets = json.load(open(IN, encoding="utf-8"))
    groups = {}
    for key, s in sets.items():
        sig = (frozenset(step54.expand(s["icd9"], step54.ALL9)), frozenset(step54.expand(s["icd10"], step54.ALL10)),
               s["outcome_criteria"], s["first_n"])
        groups.setdefault(sig, []).append((key, s))

    merged = []
    for members in groups.values():
        members.sort(key=lambda kv: rank(kv[0], kv[1]))
        key, first = members[0]
        m = dict(first)
        m["merged_keys"] = [k for k, _ in members]
        m["from_codesets"] = sorted({c for _, s in members for c in s["from_codesets"]})
        m["paper_id"] = sorted({p for _, s in members for p in s["paper_id"]})
        m["treatment"] = [t for t in TREATMENT if any(t in s["treatment"] for _, s in members)]
        m["flags"] = sorted({f for _, s in members for f in s["flags"]})
        m["criteria_assigned_for"] = sorted({p for _, s in members if s["criteria_assigned"] for p in s["paper_id"]})
        m["icd9_sources"] = sorted({s["icd9_source"] for _, s in members})
        m["icd10_sources"] = sorted({s["icd10_source"] for _, s in members})
        m["typo_fixes"] = sorted({f for _, s in members for f in s.get("typo_fixes", [])})
        m["decision_notes"] = sorted({f for _, s in members for f in s.get("decision_notes", [])})
        m["long_name"] = re.sub(r", ICD-(9|10) only$", "", re.sub(r", ICD-9 332 only$", ", ICD-9 332", first["long_name"]))
        merged.append(m)
    merged.sort(key=lambda m: list(sets).index(m["merged_keys"][0]))

    names = {}
    for m in merged:
        names.setdefault(base_name(m["merged_keys"][0]), []).append(m)
    out = {}
    for base, ms in names.items():
        for m in ms:
            name = base if len(ms) == 1 else "%s_%s" % (base, criteria_suffix(m))
            if m["merged_keys"][0] in RENAME:
                name, m["long_name"] = RENAME[m["merged_keys"][0]]
            assert name not in out, name
            out[name] = m
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote %s: %d outcomes from %d entries" % (OUT, len(out), len(sets)))
    for k, m in out.items():
        if len(m["merged_keys"]) > 1:
            print("  %-30s <- %s" % (k, ", ".join(m["merged_keys"])))


if __name__ == "__main__":
    main()
