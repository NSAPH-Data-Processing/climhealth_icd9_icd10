"""Step 3.1: look up a BibTeX entry for each publication in 030_scholar_publications.json.

Method: search Crossref by title, pick the best title match among the top hits, accept it
only if it passes the match rule below, then fetch BibTeX for its DOI from Crossref.
bib is null when no confident match is found.

Match rule (see 031_bibtex.md):
  title similarity >= MIN_SCORE  AND
  (Braun is an author  OR  (Scholar year known, |year diff| <= 1, title has >= 4 words))

Resumable: Crossref responses are cached in .cache/031_crossref.json.
Requires the folder venv:  .venv/bin/python 031_fetch_bibtex.py
"""
import difflib
import html
import json
import os
import re
import time
import warnings

warnings.filterwarnings("ignore")
import requests  # noqa: E402

IN = "030_scholar_publications.json"
OUT_JSON = "031_scholar_bibtex.json"
OUT_BIB = "031_scholar_publications.bib"
CACHE = ".cache/031_crossref.json"
API = "https://api.crossref.org/works"
ROWS = 5
MIN_SCORE = 0.90
SKIP_TYPES = {"component", "peer-review", "grant", "dataset"}
PAUSE = 1.0  # Crossref public pool: ~1 request/second

session = requests.Session()
session.headers["User-Agent"] = "climhealth-icd9-icd10/0.1 (research script)"


def get(url, **params):
    for attempt in range(5):
        try:
            r = session.get(url, params=params, timeout=60)
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                return None
        except requests.RequestException:
            pass
        time.sleep(PAUSE * 2 ** (attempt + 1))
    return None


def norm(t):
    t = html.unescape(re.sub(r"<[^>]+>", "", t or ""))
    return re.sub(r"[^a-z0-9]", "", t.lower())


def candidates_titles(item):
    title = (item.get("title") or [""])[0]
    subs = item.get("subtitle") or []
    out = [title]
    if subs:
        out.append(f"{title}: {subs[0]}")
    return out


def year_of(item):
    for k in ("published-print", "published-online", "issued"):
        dp = (item.get(k) or {}).get("date-parts") or [[None]]
        if dp[0] and dp[0][0]:
            return dp[0][0]
    return None


def best_match(pub, items):
    target = norm(pub["title"])
    best = None
    for it in items:
        if it.get("type") in SKIP_TYPES:
            continue
        score = max(difflib.SequenceMatcher(None, target, norm(t)).ratio()
                    for t in candidates_titles(it))
        dom = any((a.get("family") or "").lower() == "braun" for a in it.get("author", []))
        cand = {"doi": it["DOI"], "crossref_title": candidates_titles(it)[-1],
                "crossref_year": year_of(it), "crossref_type": it.get("type"),
                "score": round(score, 3), "braun_in_authors": dom}
        # prefer higher score, then Braun authorship, then non-preprint
        key = (round(score, 3), dom, it.get("type") != "posted-content")
        if best is None or key > best[0]:
            best = (key, cand)
    return best[1] if best else None


def accept(pub, c):
    if c is None or c["score"] < MIN_SCORE:
        return False
    if c["braun_in_authors"]:
        return True
    y, cy = pub["year"], c["crossref_year"]
    return (y is not None and cy is not None and abs(y - cy) <= 1
            and len(pub["title"].split()) >= 4)


def main():
    pubs = json.load(open(IN, encoding="utf-8"))["publications"]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {"search": {}, "bib": {}}

    def save_cache():
        json.dump(cache, open(CACHE, "w"))

    records = []
    for i, pub in enumerate(pubs, 1):
        pid = pub["scholar_pub_id"]
        if pid not in cache["search"]:
            r = get(API, **{"query.bibliographic": pub["title"], "rows": ROWS,
                            "select": "DOI,title,subtitle,author,issued,published-print,published-online,type"})
            cache["search"][pid] = r.json()["message"]["items"] if r else None
            time.sleep(PAUSE)
        items = cache["search"][pid]
        cand = best_match(pub, items or [])
        ok = accept(pub, cand)
        bib = None
        if ok:
            doi = cand["doi"]
            if doi not in cache["bib"]:
                r = get(f"{API}/{doi}/transform/application/x-bibtex")
                cache["bib"][doi] = r.text.strip() if r else None
                time.sleep(PAUSE)
            bib = cache["bib"][doi]
        if items is None:
            status = "search_failed"
        elif not ok:
            status = "no_confident_match"
        elif bib is None:
            status = "bibtex_failed"
        else:
            status = "found"
        records.append({
            "scholar_pub_id": pid, "title": pub["title"], "year": pub["year"],
            "status": status,
            "doi": cand["doi"] if ok else None,
            "match": cand,  # best Crossref candidate, kept even when rejected (for review)
            "bib": bib,
        })
        if i % 25 == 0:
            save_cache()
            print(f"{i}/{len(pubs)}", flush=True)
    save_cache()

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"source": IN, "method": "Crossref title search + DOI BibTeX transform",
                   "min_score": MIN_SCORE, "records": records}, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # .bib file: unique keys (Crossref keys like Braun_2006 collide), Scholar id as a field
    seen = {}
    with open(OUT_BIB, "w", encoding="utf-8") as f:
        for r in records:
            if not r["bib"]:
                continue
            m = re.match(r"\s*@(\w+)\{([^,]*),", r["bib"])
            if not m:
                f.write(r["bib"] + "\n\n")
                continue
            key = m.group(2) or "item"
            n = seen.get(key, 0)
            seen[key] = n + 1
            newkey = key if n == 0 else f"{key}_{chr(ord('a') + n - 1) if n <= 26 else n}"
            entry = r["bib"][:m.start(2)] + newkey + f", scholar_pub_id={{{r['scholar_pub_id']}}}" + r["bib"][m.end(2):]
            f.write(entry + "\n\n")

    counts = {}
    for r in records:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"wrote {OUT_JSON} and {OUT_BIB}: {counts}")


if __name__ == "__main__":
    main()
