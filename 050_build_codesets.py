"""Step 5: condense the code sets of Steps 2.6, 3.6 and 4.2 into one YAML, in the format of francesca_claudio_icdranges01.yaml.

Inputs
  026_icd_codes.json, 036_icd_codes.json, 042_icd_codes.json   code sets per paper; each paper counts once, the later step wins
  028_exposures.json, 038_exposures.json, 042_exposures.json   exposure per paper, for treatment
  050_names.json       hand names: signature (ICD-9 | ICD-10) -> short name and long name; names of sets with no codes

Rules (CLAUDE.md)
  Kept: role 'outcome', not group_based. Left out (listed in 050_left_out.json): Parks 2021, papers that fit the same model
  over a CCS pool, and scans of CCS groups. CCW sets that print their codes are kept. Chosen CCS or CCW outcomes without
  printed codes are kept with a marker in the code lists ('markers' in 050_names.json), for example "CCW" or "CCS 157".
  Codes are normalized in format only, and typos stay as printed until Step 5.3. Two entries are one code set when ICD-9, ICD-10 and criteria all match.
  treatment is the union over the set's papers. Papers with no air pollution, heat or weather exposure add nothing.

Output: 050_codesets.yaml, 050_left_out.json, 050_treatment_by_paper.csv
Run: .venv/bin/python 050_build_codesets.py
"""
import csv
import json
import re

import yaml

CODES =["026_icd_codes.json", "036_icd_codes.json", "042_icd_codes.json"]
EXPOSURES = ["028_exposures.json", "038_exposures.json", "042_exposures.json"]
NAMES = "050_names.json"
OUT = "050_codesets.yaml"
OUT_LEFT = "050_left_out.json"
OUT_TREATMENT = "050_treatment_by_paper.csv"

PARKS = "10_1038_s41467_021_21777_1"
LEFT_OUT_CLASS = re.compile(r"\bCCSR?\b|CCW|Chronic Conditions")
# papers that fit the same model over each diagnosis of a CCS pool, even where the codes are explicit
LEFT_OUT_PAPERS = {"10_1016_j_ypmed_2018_02_001": "same model over each diagnosis in 6 CCS categories"}
# entries with role 'outcome' that are not outcomes of their own, or that take a CCS definition from a cited paper
LEFT_OUT_HAND = {("10_1161_circheartfailure_118_005407", "heart failure or cardiomyopathy (component)"): "component of the amyloidosis definition",
                 ("10_1093_aje_kwag087", "hospitalization without ADRD"): "every other hospitalization, not a code set",
                 ("10_1609_aaai_v39i27_35009", "not-obviously heat-related (NOHR) hospitalizations: septicemia, peripheral vascular disease, urinary tract infections, diabetes mellitus with complications"): "CCS groups, taken from Bobb 2014"}
# X stands for a digit; only the valid codes are listed
WILDCARDS = {"410X0": ["410%d0" % d for d in range(10)],
             "410X1": ["410%d1" % d for d in range(10)],
             "433X1": ["433%d1" % d for d in (0, 1, 2, 3, 8, 9)],
             "434X1": ["434%d1" % d for d in (0, 1, 9)],
             "A37X1": ["A37%d1" % d for d in (0, 1, 8, 9)]}
LITERAL = {"codes beginning with \"I\"": ["I00-I99"], "codes beginning with \"J\"": ["J00-J99"], "410.xx excluding 410.x2": ["410X0", "410X1"],
           "410.xx, except 410.x2": ["410X0", "410X1"]}
CRITERIA = {"principal": "principal diagnosis", "principal_or_secondary": "principal or secondary diagnosis",
            "any": "any diagnosis", None: "not stated"}


def endpoint(code):
    """'410.xx' -> '410', '296.2x' -> '2962', 'G21·11' -> 'G2111', '410. X0' -> '410X0'; a literal J09.X1 is a real code."""
    c = re.sub(r"\s", "", code).replace("·", ".").replace("×", "X")
    if c.upper() != "J09.X1":
        c = re.sub(r"\.?[xX]+$", "", c)
    return c.replace(".", "").upper()


def normalize(code):
    """One printed code or range -> list of canonical codes."""
    code = code.strip()
    if code in LITERAL:
        return [c for x in LITERAL[code] for c in normalize(x)]
    m = re.match(r"^(\S+?)\s*(?:–|-|\bto\b)\s*(\S+)$", code)
    if m and not code.upper().startswith("J09"):
        a, b = endpoint(m.group(1)), endpoint(m.group(2))
        if a[0].isalpha() and b[0].isdigit():  # J40-42, T67.3-67.5
            b = a[0] + b
        return [a if a == b else "%s-%s" % (a, b)]
    c = endpoint(code)
    return WILDCARDS.get(c, [c])


def split_range(c):
    return c.split("-") if "-" in c else [c, c]


def sort_key(c):
    return (c[0].isalpha(), split_range(c)[0], split_range(c)[1])


def next_code(c):
    """The code after c at the same length: 429 -> 430, I25 -> I26. None for anything else."""
    m = re.match(r"^([A-Z]?)(\d{2,3})$", c)
    if not m:
        return None
    return m.group(1) + str(int(m.group(2)) + 1).zfill(len(m.group(2)))


def merge(codes):
    """Sort and join contiguous 3-character ranges, so that equal definitions compare equal: 410-414 + 415-417 -> 410-417."""
    out = []
    for c in sorted(set(codes), key=sort_key):
        a, b = split_range(c)
        if out:
            pa, pb = split_range(out[-1])
            same = len(pa) == len(pb) == len(a) == len(b) == 3 and pa[0].isalpha() == a[0].isalpha() and (not a[0].isalpha() or pa[0] == a[0])
            forward = pa <= pb and a <= b  # a printed backwards range such as 490-448 is left as it is
            if same and forward and (a <= pb or next_code(pb) == a):
                hi = max(pb, b)
                out[-1] = pa if pa == hi else "%s-%s" % (pa, hi)
                continue
        out.append(c)
    return out


def canon(slug, codes):
    return merge([c for x in codes for c in normalize(x)])


def criteria(o, paper):
    """Free text from the labeled position; the number of diagnosis fields is added when a quote or note of the paper states it."""
    ev = " ".join(" ".join([(x.get("position_evidence") or {}).get("quote", ""), (x.get("evidence") or {}).get("quote", ""),
                            x.get("note") or ""]) for x in paper["outcomes"] if x["role"] == "outcome").replace("ﬁ", "fi")
    if o["diagnosis_position"] in ("any", "principal_or_secondary"):
        if re.search(r"first (10|ten)\b|fields 1-10\b", ev):
            return "any of the first 10 diagnosis fields"
        if "up to 25" in ev:
            return "any of up to 25 diagnosis fields"
    return CRITERIA[o["diagnosis_position"]]


def treatment(e):
    weather = e["extreme_weather"] or e["extreme_heat"]
    if not (e["air_pollution"] or weather):
        return []
    return [k for k, on in (("air_pollution", e["air_pollution"]), ("extreme_weather", weather),
                            ("long_term", e["long_term"]), ("short_term", e["short_term"])) if on]


def load():
    papers = {}
    for fn in CODES:
        for p in json.load(open(fn, encoding="utf-8"))["papers"]:
            if p["slug"] not in papers or p["outcomes"]:
                papers[p["slug"]] = p
    exposure = {}
    for fn in EXPOSURES:
        exposure.update(json.load(open(fn, encoding="utf-8"))["papers"])
    return papers, exposure


def composite_union(p):
    """A composite printed as 'union of the seven subtypes' gets the codes of its subtypes."""
    for o in p["outcomes"]:
        if o["icd9"] and "union of" in o["icd9"][0]:
            parts = [x for x in p["outcomes"] if x is not o and x["role"] == "outcome"]
            o["icd9"] = [c for x in parts for c in x["icd9"]]
            o["icd10"] = [c for x in parts for c in x["icd10"]]


def main():
    papers, exposure = load()
    names = json.load(open(NAMES, encoding="utf-8"))
    groups, left, used_markers = {}, [], set()
    for slug, p in papers.items():
        composite_union(p)
        for o in p["outcomes"]:
            cl = o.get("classification") or ""
            marker = names["markers"].get("%s | %s" % (slug, o["outcome_name"]))
            used_markers.add("%s | %s" % (slug, o["outcome_name"]))
            why = (None if marker else "Parks 2021" if slug == PARKS else
                   "role %s" % o["role"] if o["role"] != "outcome" else
                   "group-based" if o.get("group_based") else
                   LEFT_OUT_PAPERS.get(slug) or
                   LEFT_OUT_HAND.get((slug, o["outcome_name"])) or
                   ("scan of CCS groups, no explicit codes" if LEFT_OUT_CLASS.search(cl) and not (o["icd9"] or o["icd10"]) else None))
            if why:
                left.append({"slug": slug, "outcome_name": o["outcome_name"], "reason": why, "classification": cl or None})
                continue
            i9, i10 = (marker["icd9"], marker["icd10"]) if marker else (canon(slug, o["icd9"]), canon(slug, o["icd10"]))
            sig ="%s | %s" % (",".join(i9), ",".join(i10)) if i9 or i10 else "no codes: " + o["outcome_name"]
            g = groups.setdefault((sig, criteria(o, p)), {"icd9": i9, "icd10": i10, "papers": set(), "printed": set()})
            g["papers"].add(slug)
            g["printed"].add(o["outcome_name"])

    assert not set(names["markers"]) - used_markers, set(names["markers"]) - used_markers
    missing = sorted({sig for sig, _ in groups} - set(names["sets"]))
    if missing:
        for (sig, crit), g in sorted(groups.items()):
            if sig in missing:
                print(json.dumps({"sig": sig, "criteria": crit, "n": len(g["papers"]), "printed": sorted(g["printed"])[:3]}, ensure_ascii=False))
        raise SystemExit("%d of %d signatures have no name in %s" % (len(missing), len({s for s, _ in groups}), NAMES))
    stale = sorted(set(names["sets"]) - {sig for sig, _ in groups})
    assert not stale, stale

    n_crit = {}
    for sig, _ in groups:
        n_crit[sig] = n_crit.get(sig, 0) + 1
    suffix = names["criteria_suffix"]
    items, rows = {}, []
    for (sig, crit), g in sorted(groups.items(), key=lambda kv: list(names["sets"]).index(kv[0][0])):
        short, long_name = names["sets"][sig]
        key = short if n_crit[sig] == 1 else "%s_%s" % (short, suffix[crit])
        assert key not in items, key
        papers_sorted = sorted(g["papers"])
        tr = [k for k in ("air_pollution", "extreme_weather", "long_term", "short_term")
              if any(k in treatment(exposure[s]) for s in papers_sorted)]
        items[key] = {"long_name": long_name, "criteria": crit, "paper_id": papers_sorted, "treatment": tr,
                      "icd9": g["icd9"], "icd10": g["icd10"]}
        rows += [[key, s] + [k in treatment(exposure[s]) for k in ("air_pollution", "extreme_weather", "long_term", "short_term")]
                 + [exposure[s].get("other_exposure") or ""] for s in papers_sorted]

    with open(OUT, "w", encoding="utf-8") as f:
        blocks = []
        for key, it in items.items():
            lines = ["%s:" % key]
            lines += ["  %s: %s" % (k, json.dumps(it[k], ensure_ascii=False)) for k in ("long_name", "criteria")]
            lines.append("  paper_id:")
            lines += ["    - %s" % json.dumps(s) for s in it["paper_id"]]  # quoted: 10_1080_..._1722134 reads as an integer otherwise
            lines += ["  %s: %s" % (k, json.dumps(it[k], ensure_ascii=False)) for k in ("treatment", "icd9", "icd10")]
            blocks.append("\n".join(lines))
        f.write("\n\n".join(blocks) + "\n")
    assert yaml.safe_load(open(OUT, encoding="utf-8")) == items, "the YAML does not read back the same"
    with open(OUT_LEFT, "w", encoding="utf-8") as f:
        json.dump({"n": len(left), "items": left}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(OUT_TREATMENT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code_set", "paper_id", "air_pollution", "extreme_weather", "long_term", "short_term", "other_exposure"])
        w.writerows(rows)
    print("wrote %s: %d code sets from %d papers; %d entries left out" % (OUT, len(items), len({r[1] for r in rows}), len(left)))
    print("  no ICD codes:", sum(not (i["icd9"] or i["icd10"]) for i in items.values()),
          "| ICD-9 only:", sum(bool(i["icd9"]) and not i["icd10"] for i in items.values()),
          "| ICD-10 only:", sum(bool(i["icd10"]) and not i["icd9"] for i in items.values()),
          "| both:", sum(bool(i["icd9"]) and bool(i["icd10"]) for i in items.values()))
    print("  shared by more than one paper:", sum(len(i["paper_id"]) > 1 for i in items.values()))


if __name__ == "__main__":
    main()
