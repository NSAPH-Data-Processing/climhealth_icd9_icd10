"""Step 3.3a: select the papers whose abstracts need to be read for Medicare outcomes.

Input: 032_abstracts.json. Usable = abstract not null and no flags. Deduplicated by DOI
(first record kept; records without a DOI are kept as-is).

Each usable paper gets a `screen` value:
  "medicare"    title/abstract mentions Medicare, CMS, Medicaid, MedPAR, fee-for-service or beneficiaries
  "older_adult" no Medicare term, but mentions older adults / elderly / aged 65+
  "none"        neither -> coded uses_medicare False without reading
"medicare" and "older_adult" papers are read by hand (labels in 033_labels.json).

Output: 033_candidates.json
Run: .venv/bin/python 033_prefilter.py
"""
import json
import re

IN = "032_abstracts.json"
OUT = "033_candidates.json"

MEDICARE = re.compile(r"medicare|\bCMS\b|centers for medicare|medicaid|fee-for-service|\bMedPAR\b|beneficiar",
                      re.I)
OLDER = re.compile(r"older (adults|americans|population|people|individuals)|aged? (≥|>=|over )?\s?65"
                   r"|65 years|elderly", re.I)


def main():
    recs = json.load(open(IN, encoding="utf-8"))["records"]
    papers, seen = [], {}
    for r in recs:
        if not r["abstract"] or r["flags"]:
            continue
        key = r["doi"] or r["scholar_pub_id"]
        if key in seen:
            seen[key]["duplicate_ids"].append(r["scholar_pub_id"])
            continue
        text = r["title"] + " " + r["abstract"]
        screen = "medicare" if MEDICARE.search(text) else "older_adult" if OLDER.search(text) else "none"
        p = {"key": key, "scholar_pub_id": r["scholar_pub_id"], "duplicate_ids": [],
             "doi": r["doi"], "pmid": r["pmid"], "year": r["year"], "title": r["title"],
             "abstract": r["abstract"], "screen": screen}
        seen[key] = p
        papers.append(p)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"source": IN, "papers": papers}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    counts = {}
    for p in papers:
        counts[p["screen"]] = counts.get(p["screen"], 0) + 1
    print(f"wrote {OUT}: {len(papers)} unique papers; {counts}")


if __name__ == "__main__":
    main()
