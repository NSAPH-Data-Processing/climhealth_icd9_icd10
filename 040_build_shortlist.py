"""Step 4b: one download shortlist for the gaps of the unified paper set.

Gaps are taken from 040_papers.json (current status): papers with no_fulltext or with
supplements_missing. Ranks and reasons are reused from the hand tables PRIORITY in
025_build_shortlist.py (Dominici) and 035_build_shortlist.py (Braun):
  - Step 2.5 order is kept; items that are no longer gaps (e.g. Qin 2025, now open access) drop out;
  - Braun-only items are inserted after Step 2.5 rank BRAUN_AFTER (they are not cited in the
    Step 1 PDF but add ADRD code lists for heat and long-term pollution studies).
The first SHORTLIST_SIZE items are the shortlist; the rest are optional.

Output: 040_shortlist.json
Run: .venv/bin/python 040_build_shortlist.py
"""
import importlib.util
import json

SHORTLIST_SIZE = 11
BRAUN_AFTER = 10


def priority(path):
    spec = importlib.util.spec_from_file_location("m", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PRIORITY


def link(p):
    out = []
    if p["pmcid"]:
        out.append("https://pmc.ncbi.nlm.nih.gov/articles/%s/" % p["pmcid"])
    if p["doi"]:
        out.append("https://doi.org/%s" % p["doi"])
    if not out and p["pmid"]:
        out.append("https://pubmed.ncbi.nlm.nih.gov/%s/" % p["pmid"])
    return out


def main():
    papers = {p["slug"]: p for p in json.load(open("040_papers.json", encoding="utf-8"))["papers"]}
    gaps = {s for s, p in papers.items() if p["fulltext_status"] == "no_fulltext" or p["supplements_missing"]}
    p25, p35 = priority("025_build_shortlist.py"), priority("035_build_shortlist.py")
    order = [s for s in sorted(p25, key=lambda s: p25[s][0])]
    braun_only = [s for s in sorted(p35, key=lambda s: p35[s][0]) if s not in p25]
    cut = sum(1 for s in order if p25[s][0] <= BRAUN_AFTER)
    order = order[:cut] + braun_only + order[cut:]
    resolved = [s for s in order if s not in gaps]
    order = [s for s in order if s in gaps]
    missing = gaps - set(order)
    assert not missing, "gaps without a priority entry: %s" % missing

    items = []
    for rank, s in enumerate(order, 1):
        p = papers[s]
        _, cv, doc, why = p25[s] if s in p25 else p35[s]
        items.append({"rank": rank, "shortlist": rank <= SHORTLIST_SIZE, "slug": s, "label": p["label"],
                      "gap": "no_fulltext" if p["fulltext_status"] == "no_fulltext" else "supplements_missing",
                      "step25_rank": p25[s][0] if s in p25 else None, "step35_rank": p35[s][0] if s in p35 else None,
                      "in_dominici_scholar": p["in_dominici_scholar"], "in_braun_scholar": p["in_braun_scholar"],
                      "step1_cv": cv, "document": doc, "links": link(p), "why": why,
                      "year": p["year"], "title": p["title"], "save_to": "papers/%s/" % s})
    with open("040_shortlist.json", "w", encoding="utf-8") as f:
        json.dump({"sources": ["040_papers.json", "025_build_shortlist.py", "035_build_shortlist.py"],
                   "shortlist_size": SHORTLIST_SIZE, "resolved_since_step25": resolved, "items": items},
                  f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote 040_shortlist.json: %d gaps, %d shortlisted; resolved: %s"
          % (len(items), sum(i["shortlist"] for i in items), resolved))
    for i in items[:SHORTLIST_SIZE]:
        print("  %2d %-22s %-60s %s" % (i["rank"], i["gap"], i["label"][:60], i["links"][0]))


if __name__ == "__main__":
    main()
