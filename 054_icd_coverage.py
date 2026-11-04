"""Step 5.4: give every outcome ICD-9 and ICD-10 codes for the whole period.

Input: 053_outcomes.json, official_lists/.
For a set with one ICD version, in this order (a set split in Step 5.3 goes straight to the GEMs):
  1. Pairing: the other version from every set whose codes in the available version are identical, whatever its criteria.
     Different pairings each give an entry. The set keeps its own criteria.
  2. GEMs: the CMS 2018 General Equivalence Mappings, with counts of approximate, one-to-many and unmapped codes.
Records coverage for sets not filled by GEMs: expanded to codes and passed through the GEMs, the share of mapped codes that fall
inside the other version, in each direction. It adds no flag, because sets at or below COVERAGE were decided in Step 5.3.

Output: 054_outcomes.json
Run: .venv/bin/python 054_icd_coverage.py
"""
import csv
import json

IN = "053_outcomes.json"
OUT = "054_outcomes.json"
COVERAGE = 0.5  # the review cutoff of Step 5.3, for reference


def load_gem(fn, src, dst):
    gem = {}
    for r in csv.DictReader(open(fn, encoding="utf-8")):
        gem.setdefault(r[src], []).append(r)
    return gem, dst


GEM9, _ = load_gem("official_lists/gem_2018_icd9_to_icd10.csv", "icd9", "icd10")
GEM10, _ = load_gem("official_lists/gem_2018_icd10_to_icd9.csv", "icd10", "icd9")
ALL9 = sorted(set(GEM9) | {r["icd9"] for r in csv.DictReader(open("official_lists/ccs_icd9_2015.csv", encoding="utf-8"))})
ALL10 = sorted(set(GEM10) | {r["icd10"] for r in csv.DictReader(open("official_lists/ccsr_icd10_v2023_1.csv", encoding="utf-8"))})


def expand(tokens, universe):
    """Canonical codes and ranges -> valid codes. '428' covers 4280, 42821, ...; '410-414' compares the first 3 characters."""
    out = set()
    for t in tokens:
        if "-" in t:
            a, b = t.split("-")
            out.update(c for c in universe if a <= c[:len(a)] <= b)
        else:
            out.update(c for c in universe if c.startswith(t))
    return out


def gem_fill(tokens, version):
    gem, universe, dst = (GEM9, ALL9, "icd10") if version == "icd9" else (GEM10, ALL10, "icd9")
    codes = expand(tokens, universe)
    targets, approx, one_many, no_map, combination = set(), 0, 0, 0, 0
    for c in codes:
        rows = gem.get(c, [])
        mapped = [r for r in rows if r["no_map"] == "0"]
        if not mapped:
            no_map += 1
            continue
        targets.update(r[dst] for r in mapped)
        approx += any(r["approximate"] == "1" for r in mapped)
        combination += any(r["combination"] == "1" for r in mapped)
        one_many += len({r[dst] for r in mapped}) > 1
    return sorted(targets), {"n_source_codes": len(codes), "n_approximate": approx, "n_one_to_many": one_many,
                             "n_no_map": no_map, "n_combination": combination, "n_target_codes": len(targets)}


def coverage(s):
    """Share of mapped codes that fall inside the other version, in each direction."""
    i9, i10 = expand(s["icd9"], ALL9), expand(s["icd10"], ALL10)
    out = {}
    for name, codes, gem, dst, other in (("icd9_to_icd10", i9, GEM9, "icd10", i10), ("icd10_to_icd9", i10, GEM10, "icd9", i9)):
        mapped = {r[dst] for c in codes for r in gem.get(c, []) if r["no_map"] == "0"}
        out[name] = round(len(mapped & other) / len(mapped), 2) if mapped else None
    return out


def main():
    sets = json.load(open(IN, encoding="utf-8"))
    both = {k: s for k, s in sets.items() if s["icd9"] and s["icd10"]}
    out, n_pair, n_gem = {}, 0, 0
    for key, s in sets.items():
        s["from_codesets"] = [key]
        s["flags"] = list(s.get("typo_fixes", []))
        if key in both:
            out[key] = s
            continue
        have, need = ("icd9", "icd10") if s["icd9"] else ("icd10", "icd9")
        pairs = {}
        for k, b in both.items():
            if b[have] == s[have] and not s.get("split_from"):  # a set split in Step 5.3 uses the GEMs
                pairs.setdefault(tuple(b[need]), []).append(k)
        if pairs:
            n_pair += 1
            for i, (codes, sources) in enumerate(sorted(pairs.items()), 1):
                e = dict(s, **{need: list(codes), need + "_source": "paper pairing: " + ", ".join(sources), "flags": list(s["flags"])})
                out[key if len(pairs) == 1 else "%s__pair%d" % (key, i)] = e
        else:
            n_gem += 1
            codes, stats = gem_fill(s[have], have)
            assert codes, key
            s[need] = codes
            s[need + "_source"] = "GEM 2018"
            s["gem"] = stats
            if stats["n_approximate"] or stats["n_one_to_many"] or stats["n_no_map"]:
                s["flags"].append("review GEM mapping: %(n_source_codes)d source codes, %(n_approximate)d approximate, "
                                  "%(n_one_to_many)d one-to-many, %(n_no_map)d with no map" % stats)
            out[key] = s
    for key, s in out.items():
        if s.get("gem"):
            continue
        s["coverage"] = coverage(s)  # numbers only: sets at or below COVERAGE were decided one by one in Step 5.3
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote %s: %d entries; %d sets paired from a paper, %d filled by GEMs, %d flagged" % (OUT, len(out), n_pair, n_gem, sum(bool(s["flags"]) for s in out.values())))
    for k, s in out.items():
        print("  %-36s 9=%-34s 10=%-34s %s" % (k, str(s["icd9_source"])[:34], str(s["icd10_source"])[:34], "; ".join(f[:95] for f in s["flags"])))


if __name__ == "__main__":
    main()
