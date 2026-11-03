"""Step 4: build the unified download shortlist from Step 2.5 (Francesca Dominici) and Step 3.5 (Danielle Braun).

Input: 025_shortlist.json, 035_shortlist.json (read only).
One row per paper, matched by DOI (save_to folder when a paper has no DOI). Unified rank: papers shortlisted in either step first, then the rest;
within each group, papers on the Step 2.5 list in Step 2.5 order, then Step 3.5-only papers in Step 3.5 order.
Fields that can differ between the lists (document, why) are kept per list; step1_cv is the union.

Output: 040_shortlist.json
Run: .venv/bin/python 040_build_shortlist.py
"""
import json

IN_25 = "025_shortlist.json"
IN_35 = "035_shortlist.json"
OUT = "040_shortlist.json"


def load(fn):
    items = json.load(open(fn, encoding="utf-8"))["items"]
    by_key = {(i["doi"] or i["save_to"]).lower(): i for i in items}  # one Step 2.5 item has no DOI
    assert len(by_key) == len(items), "%s: duplicate paper" % fn
    return by_key


def merge(a, b):
    first = a or b
    if a and b:
        for k in ("gap", "save_to"):
            assert a[k] == b[k], "%s differs for %s: %r vs %r" % (k, a["doi"], a[k], b[k])
    return {
        "shortlist": bool((a and a["shortlist"]) or (b and b["shortlist"])),
        "lists": [n for n, x in (("025", a), ("035", b)) if x],
        "step25_rank": a["rank"] if a else None,
        "step35_rank": b["rank"] if b else None,
        "step25_shortlist": a["shortlist"] if a else None,
        "step35_shortlist": b["shortlist"] if b else None,
        "gap": first["gap"], "year": first["year"], "title": first["title"], "doi": first["doi"],
        "pmid": first["pmid"], "pmcid": first["pmcid"],
        "step1_cv": sorted(set((a["step1_cv"] if a else []) + (b["step1_cv"] if b else []))),
        "document_step25": a["document"] if a else None,
        "document_step35": b["document"] if b else None,
        "why_step25": a["why"] if a else None,
        "why_step35": b["why"] if b else None,
        "links": first["links"], "save_to": first["save_to"],
    }


def order(x):
    on_25 = x["step25_rank"] is not None
    return (not x["shortlist"], not on_25, x["step25_rank"] if on_25 else x["step35_rank"])


def main():
    s25, s35 = load(IN_25), load(IN_35)
    rows = [merge(s25.get(d), s35.get(d)) for d in set(s25) | set(s35)]
    rows.sort(key=order)
    items = [dict(unified_rank=n, **r) for n, r in enumerate(rows, 1)]
    n_both = sum(len(i["lists"]) == 2 for i in items)
    n_short = sum(i["shortlist"] for i in items)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"source": [IN_25, IN_35], "n_step25": len(s25), "n_step35": len(s35), "n_on_both": n_both,
                   "n_papers": len(items), "n_shortlisted": n_short, "items": items},
                  f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s: %d papers, %d on both lists, %d shortlisted" % (OUT, len(items), n_both, n_short))
    for i in items:
        print(i["unified_rank"], i["shortlist"], i["lists"], i["step25_rank"], i["step35_rank"], i["gap"], i["year"],
              i["doi"], i["step1_cv"], "| same_doc" if i["document_step25"] == i["document_step35"] else "",
              "|", i["title"][:60])


if __name__ == "__main__":
    main()
