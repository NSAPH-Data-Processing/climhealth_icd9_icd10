"""Step 5.1: outcome bins over the condensed code sets, split into long-term and short-term.

Inputs
  050_codesets.yaml   the code sets and their treatment
  051_bin_map.json    hand map: bin short name -> long name, code sets (every code set must be in exactly one bin)

A code set goes in long_term and/or short_term from its treatment. A code set with neither (exposure is none of the
listed ones) is in no list, and a bin with no listed code set is not written; both are printed.

Output: 051_bins.yaml
Run: .venv/bin/python 051_build_bins.py
"""
import json

import yaml

CODESETS = "050_codesets.yaml"
MAP = "051_bin_map.json"
OUT = "051_bins.yaml"


def main():
    sets = yaml.safe_load(open(CODESETS, encoding="utf-8"))
    spec = json.load(open(MAP, encoding="utf-8"))["bins"]
    mapped = [c for _, members in spec.values() for c in members]
    assert sorted(mapped) == sorted(sets), "not mapped once: %s" % sorted(set(mapped) ^ set(sets) | {c for c in mapped if mapped.count(c) > 1})

    bins, dropped, unlisted = {}, [], []
    for short, (long_name, members) in spec.items():
        lt = [c for c in members if "long_term" in sets[c]["treatment"]]
        st = [c for c in members if "short_term" in sets[c]["treatment"]]
        unlisted += [c for c in members if c not in lt and c not in st]
        if lt or st:
            bins[short] = {"long_name": long_name, "long_term": lt, "short_term": st}
        else:
            dropped.append(short)

    with open(OUT, "w", encoding="utf-8") as f:
        blocks = []
        for short, b in bins.items():
            lines = ["%s:" % short, "  long_name: %s" % json.dumps(b["long_name"], ensure_ascii=False)]
            lines += ["  %s: %s" % (k, json.dumps(b[k])) for k in ("long_term", "short_term")]
            blocks.append("\n".join(lines))
        f.write("\n\n".join(blocks) + "\n")
    assert yaml.safe_load(open(OUT, encoding="utf-8")) == bins, "the YAML does not read back the same"

    print("wrote %s: %d bins from %d code sets" % (OUT, len(bins), len(sets)))
    print("  both:", sum(bool(b["long_term"]) and bool(b["short_term"]) for b in bins.values()),
          "| long-term only:", [k for k, b in bins.items() if b["long_term"] and not b["short_term"]],
          "| short-term only:", [k for k, b in bins.items() if b["short_term"] and not b["long_term"]])
    print("  code sets in neither list (%d):" % len(unlisted), unlisted)
    print("  bins not written:", dropped)
    for k, b in bins.items():
        print("  %-22s L %2d  S %2d" % (k, len(b["long_term"]), len(b["short_term"])))


if __name__ == "__main__":
    main()
