"""Step 6: outcome bins over the final YAML, split into long-term and short-term, using its short names.

Inputs: 060_bin_map.json (bin -> Step 5 code sets), 055_outcomes.json (outcome -> Step 5 code sets it came from), 056_outcomes.yaml.
An outcome merged from several code sets is in the bin of each. long_term and short_term come from its treatment.

Output: 060_bins.yaml
Run: .venv/bin/python 060_build_bins.py
"""
import json
import re

import yaml

MAP = "060_bin_map.json"
OUTCOMES = "055_outcomes.json"
FINAL = "056_outcomes.yaml"
OUT = "060_bins.yaml"


def main():
    spec = json.load(open(MAP, encoding="utf-8"))["bins"]
    origin = json.load(open(OUTCOMES, encoding="utf-8"))
    final = yaml.safe_load(open(FINAL, encoding="utf-8"))
    for m in origin.values():  # the two parts of a set split in Step 5.3 belong to the bin of that set
        m["from_codesets"] = sorted({re.sub(r"__icd(9|10)$", "", c) for c in m["from_codesets"]})
    mapped = {c for _, members in spec.values() for c in members}
    missing = sorted({c for m in origin.values() for c in m["from_codesets"]} - mapped)
    assert not missing, "no bin for: %s" % missing
    bins, dropped, unlisted = {}, [], []
    for short, (long_name, members) in spec.items():
        keys = [k for k, m in origin.items() if set(m["from_codesets"]) & set(members)]
        lt = [k for k in keys if "long_term" in final[k]["treatment"]]
        st = [k for k in keys if "short_term" in final[k]["treatment"]]
        unlisted += [k for k in keys if k not in lt and k not in st]
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
    assert yaml.safe_load(open(OUT, encoding="utf-8")) == bins
    print("wrote %s: %d bins" % (OUT, len(bins)))
    print("  in neither list (%d):" % len(unlisted), unlisted)
    print("  bins not written:", dropped)
    print("  both:", sum(bool(b["long_term"]) and bool(b["short_term"]) for b in bins.values()),
          "| long-term only:", [k for k, b in bins.items() if b["long_term"] and not b["short_term"]],
          "| short-term only:", [k for k, b in bins.items() if b["short_term"] and not b["long_term"]])
    print("  outcomes listed: %d of %d" % (len({c for b in bins.values() for c in b["long_term"] + b["short_term"]}), len(final)))
    for k, b in bins.items():
        print("  %-22s L %2d  S %2d" % (k, len(b["long_term"]), len(b["short_term"])))


if __name__ == "__main__":
    main()
