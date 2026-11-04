"""Step 5.3: apply the decisions in 053_decisions.json to the code sets of Step 5.2. Applies nothing else.

Each typo replaces the printed code in its code set's list, and records the change on the set under 'typo_fixes'.

Input: 052_outcomes.json, 053_decisions.json
Output: 053_outcomes.json
Run: .venv/bin/python 053_apply_decisions.py
"""
import importlib.util
import json

IN = "052_outcomes.json"
DECISIONS = "053_decisions.json"
OUT = "053_outcomes.json"

_spec = importlib.util.spec_from_file_location("step52", "052_resolve_markers.py")
STEP52 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(STEP52)


def main():
    sets = json.load(open(IN, encoding="utf-8"))
    decisions = json.load(open(DECISIONS, encoding="utf-8"))["decisions"]
    ccs, ccsr = STEP52.load_tables()
    for d in decisions:
        assert d["type"] in ("typo", "ambiguous", "marker_typo", "keep", "split"), d["type"]
        s = sets[d["code_set"]]
        if d["type"] == "split":  # one ICD-9-only and one ICD-10-only set; Step 5.4 fills each with the GEMs, not a pairing
            for version, other, label in (("icd9", "icd10", "ICD-9"), ("icd10", "icd9", "ICD-10")):
                part = dict(s, **{other: [], other + "_source": "none", "split_from": d["code_set"]})
                part["long_name"] = "%s, as printed in %s" % (s["long_name"], label)
                part["decision_notes"] = s.get("decision_notes", []) + ["%s (decision %d)" % (d["note"], d["id"])]
                sets["%s__%s" % (d["code_set"], version)] = part
            del sets[d["code_set"]]
            continue
        if d["type"] == "keep":  # no code changes, only the note travels with the set
            assert d["printed"] in s[d["version"]], (d["code_set"], d["printed"])
            s.setdefault("decision_notes", []).append("%s (decision %d)" % (d["note"], d["id"]))
            continue
        if d["type"] == "ambiguous":  # the code changes, and the ambiguity travels with the set
            s.setdefault("decision_notes", []).append("%s (decision %d)" % (d["note"], d["id"]))
        if d["type"] in ("typo", "ambiguous"):
            codes = s[d["version"]]
            assert d["printed"] in codes, (d["code_set"], d["printed"], codes)
            s[d["version"]] = [d["used"] if c == d["printed"] else c for c in codes]
        else:  # the printed code is a marker: resolve the corrected marker list again from the official list
            markers = s[d["version"] + "_marker"]
            assert d["printed"] in markers, (d["code_set"], d["printed"], markers)
            s[d["version"] + "_marker"] = [d["used"] if m == d["printed"] else m for m in markers]
            found = [c for m in s[d["version"] + "_marker"] for c in STEP52.resolve(m, d["version"], ccs, ccsr)[0]]
            excluded = {c for x in STEP52.CCSR_EXCLUDE.get(d["code_set"], ()) for c in ccsr.get(x, [])}
            s[d["version"]] = sorted(set(found) - excluded)
        if d["type"] != "ambiguous":
            s.setdefault("typo_fixes", []).append("%s prints %s, read as %s (decision %d)" % (d["paper_id"], d["printed"], d["used"], d["id"]))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(sets, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote %s: %d sets, %d decisions applied" % (OUT, len(sets), len(decisions)))
    for d in decisions:
        if d["type"] in ("split", "keep"):
            print("  %d %s: %s" % (d["id"], d["code_set"], d["type"]))
            continue
        s = sets[d["code_set"]]
        print("  %d %s: %s -> %s; %s now %d codes: %s" % (d["id"], d["code_set"], d["printed"], d["used"], d["version"], len(s[d["version"]]), s[d["version"]][:4]))


if __name__ == "__main__":
    main()
