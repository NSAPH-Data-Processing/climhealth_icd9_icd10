"""Step 2.3b: merge hand labels into one outcome record per Google Scholar publication.

Inputs
  022_abstracts.json    all 687 Scholar records (abstract or null)
  023_candidates.json   unique usable papers with `screen` (023_prefilter.py)
  023_labels.json       hand labels for papers with screen "medicare" / "older_adult"

Rules
  - no usable abstract (null or flagged in Step 2.2) -> uses_medicare/outcome null, label_source "no_abstract"
  - screen "none" (no Medicare/older-adult term)      -> False/False, label_source "keyword_rule"
  - otherwise                                          -> hand label, label_source "hand"
  - a hand label with override_keyword_rule replaces the keyword rule -> label_source "hand_override"
    (papers that are Medicare studies but never name Medicare in the abstract)
  - duplicates (same DOI) inherit the label of the first record
evidence = the full sentence of the title/abstract containing the label's evidence_phrase
(case-insensitive). A phrase that is not found is reported and evidence is left null.

Output: 023_outcomes.json
Run: .venv/bin/python 023_build_outcomes.py
"""
import json
import re

IN_ABS = "022_abstracts.json"
IN_CAND = "023_candidates.json"
IN_LAB = "023_labels.json"
OUT = "023_outcomes.json"


def sentence_with(text, phrase):
    i = text.lower().find(phrase.lower())
    if i < 0:
        return None
    start = max(text.rfind(". ", 0, i) + 2, 0) if text.rfind(". ", 0, i) >= 0 else 0
    end = text.find(". ", i + len(phrase))
    return text[start:end + 1 if end >= 0 else len(text)].strip()


def main():
    recs = json.load(open(IN_ABS, encoding="utf-8"))["records"]
    papers = json.load(open(IN_CAND, encoding="utf-8"))["papers"]
    labels = {l["key"]: l for l in json.load(open(IN_LAB, encoding="utf-8"))["labels"]}

    by_id, missing = {}, []
    for p in papers:
        base = {"paper_key": p["key"], "screen": p["screen"]}
        if p["screen"] == "none" and p["key"] not in labels:
            lab = {**base, "label_source": "keyword_rule", "uses_medicare": False, "outcome": False,
                   "outcome_names": [], "cohort_names": [], "uncertain": False, "evidence": None,
                   "note": "no Medicare/CMS/older-adult term in title or abstract"}
        else:
            l = labels[p["key"]]
            ev = sentence_with(p["title"] + ". " + p["abstract"], l["evidence_phrase"])
            if ev is None:
                missing.append((p["key"], l["evidence_phrase"]))
            src = "hand_override" if l.get("override_keyword_rule") else "hand"
            lab = {**base, "label_source": src, "uses_medicare": l["uses_medicare"],
                   "outcome": l["outcome"], "outcome_names": l["outcome_names"],
                   "cohort_names": l["cohort_names"], "uncertain": l["uncertain"],
                   "evidence": ev, "note": l["note"] or None}
        for pid in [p["scholar_pub_id"]] + p["duplicate_ids"]:
            by_id[pid] = lab

    out = []
    for r in recs:
        lab = by_id.get(r["scholar_pub_id"])
        if lab is None:
            lab = {"paper_key": r["doi"] or r["scholar_pub_id"], "screen": None,
                   "label_source": "no_abstract", "uses_medicare": None, "outcome": None,
                   "outcome_names": [], "cohort_names": [], "uncertain": None, "evidence": None,
                   "note": "flagged abstract" if r["abstract"] else "no abstract"}
        out.append({"scholar_pub_id": r["scholar_pub_id"], "title": r["title"], "year": r["year"],
                    "doi": r["doi"], "pmid": r["pmid"], **lab})

    unlabeled = [p["key"] for p in papers if p["screen"] != "none" and p["key"] not in labels]
    assert not unlabeled, f"unlabeled candidates: {unlabeled}"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"sources": [IN_ABS, IN_CAND, IN_LAB], "records": out}, f, ensure_ascii=False, indent=2)
        f.write("\n")

    for k, ph in missing:
        print(f"evidence phrase not found: {k}: {ph!r}")
    counts = {}
    for r in out:
        k = (r["label_source"], r["uses_medicare"], r["outcome"])
        counts[k] = counts.get(k, 0) + 1
    print(f"wrote {OUT}: {len(out)} records")
    for k in sorted(counts, key=str):
        print(" ", k, counts[k])


if __name__ == "__main__":
    main()
