"""Step 5.3: list potential typos and measure coverage, for review one by one. Changes no codes.

Typo scan, on the codes as printed in 026, 036 and 042 (before any correction), for the entries kept in Step 5:
  invalid_range     the range runs backwards
  invalid_code      no valid code in the official lists (CCS 2015 + GEM 2018 for ICD-9, CCSR v2023.1 + GEM 2018 for ICD-10)
  outside_chapter   a cardiovascular or respiratory composite with codes outside that ICD chapter
  outlier_range     a printed range that differs in its upper end from a more common range with the same start, in the same version

Coverage, on sets with both versions after Step 5.2: the share of GEM-mapped codes that fall inside the other version,
in each direction, sorted from lowest. It counts codes, not admissions.

Input: 026, 036, 042 _icd_codes.json, 050_left_out.json, 052_outcomes.json, official_lists/
Output: 053_scan.json
Run: .venv/bin/python 053_scan_codes.py
"""
import collections
import importlib.util
import json
import re

OUT = "053_scan.json"
CODES = ["026_icd_codes.json", "036_icd_codes.json", "042_icd_codes.json"]
CHAPTERS = [(re.compile(r"cardiovascular|\bcvd\b|circulatory", re.I), "390", "459", "I"), (re.compile(r"respiratory", re.I), "460", "519", "J")]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STEP5 = load_module("step5", "050_build_codesets.py")
STEP54 = load_module("step54", "054_icd_coverage.py")


def kept_entries():
    papers = {}
    for fn in CODES:
        for p in json.load(open(fn, encoding="utf-8"))["papers"]:
            if p["slug"] not in papers or p["outcomes"]:
                papers[p["slug"]] = p
    left = {(i["slug"], i["outcome_name"]) for i in json.load(open("050_left_out.json", encoding="utf-8"))["items"]}
    for slug, p in papers.items():
        for o in p["outcomes"]:
            if (slug, o["outcome_name"]) not in left:
                yield slug, o


def scan_code(printed, version):
    """Issues for one printed code, tested before any correction."""
    if "union of" in printed:
        return []
    universe = STEP54.ALL9 if version == "icd9" else STEP54.ALL10
    issues = []
    for token in STEP5.normalize(printed):
        if "-" in token:
            a, b = token.split("-")
            if a > b:
                issues.append("invalid_range")
                continue
        if not STEP54.expand([token], universe):
            issues.append("invalid_code")
    return issues


def chapter_issue(printed, version, name):
    for pat, lo, hi, letter in CHAPTERS:
        if not pat.search(name) or "union of" in printed:
            continue
        for token in STEP5.normalize(printed):
            for end in token.split("-"):
                if version == "icd9" and end[:3].isdigit() and not lo <= end[:3] <= hi:
                    return "outside_chapter"
                if version == "icd10" and end[0].isalpha() and end[0] != letter:
                    return "outside_chapter"
    return None


def main():
    typos, ranges = [], collections.Counter()
    entries = list(kept_entries())
    for slug, o in entries:
        for version in ("icd9", "icd10"):
            for printed in o[version]:
                for token in STEP5.normalize(printed) if "union of" not in printed else []:
                    if "-" in token:
                        ranges[token] += 1
    by_start = collections.defaultdict(collections.Counter)
    for token, n in ranges.items():
        by_start[token.split("-")[0]][token.split("-")[1]] += n
    for slug, o in entries:
        for version in ("icd9", "icd10"):
            for printed in o[version]:
                issues = scan_code(printed, version)
                chapter = chapter_issue(printed, version, o["outcome_name"])
                if chapter:
                    issues.append(chapter)
                detail = None
                for token in STEP5.normalize(printed) if "union of" not in printed else []:
                    if "-" in token:
                        a, b = token.split("-")
                        best, n = by_start[a].most_common(1)[0]
                        if b != best and n >= 2 * by_start[a][b]:
                            issues.append("outlier_range")
                            detail = "more common with this start: %s-%s (%d entries, this one %d)" % (a, best, n, by_start[a][b])
                if issues:
                    typos.append({"paper_id": slug, "outcome": o["outcome_name"], "version": version, "printed": printed,
                                  "issues": sorted(set(issues)), "detail": detail, "evidence": o.get("evidence"), "note": o.get("note")})

    sets = json.load(open("052_outcomes.json", encoding="utf-8"))  # before any decision: this is what the decisions reviewed
    coverage = []
    for key, s in sets.items():
        if s["icd9"] and s["icd10"]:
            c = STEP54.coverage(s)
            values = [v for v in c.values() if v is not None]
            coverage.append({"code_set": key, "long_name": s["long_name"], "icd9_source": s["icd9_source"], "icd10_source": s["icd10_source"],
                             "paper_id": s["paper_id"], "icd9_to_icd10": c["icd9_to_icd10"], "icd10_to_icd9": c["icd10_to_icd9"],
                             "lowest": min(values) if values else None, "icd9": s["icd9"], "icd10": s["icd10"]})
    coverage.sort(key=lambda x: (x["lowest"] is None, x["lowest"]))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"n_entries_scanned": len(entries), "potential_typos": typos, "coverage": coverage}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote %s: %d entries scanned, %d potential typos, %d sets with coverage" % (OUT, len(entries), len(typos), len(coverage)))
    print("\nPOTENTIAL TYPOS")
    for t in typos:
        print("  %s | %s | %s | %s | %s | %s" % (t["paper_id"], t["outcome"][:45], t["version"], t["printed"], ",".join(t["issues"]), t["detail"] or ""))
    print("\nCOVERAGE")
    for c in coverage:
        print("  %-28s 9>10 %-5s 10>9 %-5s %s | 9=%s | 10=%s" % (c["code_set"], c["icd9_to_icd10"], c["icd10_to_icd9"], len(c["paper_id"]), ",".join(c["icd9"])[:48], ",".join(c["icd10"])[:48]))


if __name__ == "__main__":
    main()
