"""Step 2.2: fetch an abstract for each publication in 020_scholar_publications.json.

Records with a DOI (from 021_scholar_bibtex.json): sources are tried in order
  Europe PMC (MEDLINE/PubMed + preprints) -> OpenAlex -> Semantic Scholar -> Crossref
Records without a DOI: Europe PMC title search, accepted with the Step 2.1 match rule
  (title similarity >= 0.90 AND (Dominici is an author OR |year diff| <= 1 with >= 4 title words)).
abstract is null when no source has one.

Resumable: responses are cached in .cache/022_abstracts_cache.json.
Run with the folder venv:  .venv/bin/python 022_fetch_abstracts.py
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

IN_PUBS = "020_scholar_publications.json"
IN_BIB = "021_scholar_bibtex.json"
OUT = "022_abstracts.json"
CACHE = ".cache/022_abstracts_cache.json"
MIN_SCORE = 0.90
SHORT = 200  # abstracts shorter than this are flagged as possibly truncated
# scraped page text that is not an abstract (author lists, landing-page boilerplate)
SUSPECT = re.compile(r"Author Information|Download a PDF|\b(MD|PhD|MPH|MBA)\b\s*[;,]")
PAUSE = 0.4

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OPENALEX = "https://api.openalex.org/works"
S2 = "https://api.semanticscholar.org/graph/v1/paper/batch"
CROSSREF = "https://api.crossref.org/works"

session = requests.Session()
session.headers["User-Agent"] = "climhealth-icd9-icd10/0.1 (research script)"


def request(method, url, **kw):
    for attempt in range(5):
        try:
            r = session.request(method, url, timeout=60, **kw)
            if r.status_code == 200:
                return r
            if r.status_code in (400, 404):
                return None
        except requests.RequestException:
            pass
        time.sleep(2 ** (attempt + 1))
    return None


def clean(text):
    """Strip JATS/HTML tags and whitespace; None for empty."""
    if not text:
        return None
    t = re.sub(r"<[^>]+>", " ", text)
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    t = re.sub(r"^(abstract|summary)[\s.:]+", "", t, flags=re.I)
    return t or None


def norm(t):
    t = html.unescape(re.sub(r"<[^>]+>", "", t or ""))
    return re.sub(r"[^a-z0-9]", "", t.lower())


def from_inverted(inv):
    if not inv:
        return None
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


# --- sources ---------------------------------------------------------------

def epmc_query(query, page_size):
    r = request("GET", EPMC, params={"query": query, "resultType": "core",
                                     "format": "json", "pageSize": page_size})
    time.sleep(PAUSE)
    return r.json()["resultList"]["result"] if r else None


def epmc_slim(hit):
    return {"pmid": hit.get("pmid"), "doi": (hit.get("doi") or "").lower() or None,
            "title": hit.get("title"), "year": int(hit["pubYear"]) if hit.get("pubYear") else None,
            "authors": hit.get("authorString") or "", "source": hit.get("source"),
            "abstract": clean(hit.get("abstractText"))}


def openalex_batch(dois):
    out = {}
    for i in range(0, len(dois), 50):
        chunk = dois[i:i + 50]
        r = request("GET", OPENALEX, params={"filter": "doi:" + "|".join(chunk), "per-page": 50,
                                             "select": "doi,abstract_inverted_index"})
        time.sleep(PAUSE)
        for w in (r.json()["results"] if r else []):
            d = (w.get("doi") or "").replace("https://doi.org/", "").lower()
            out[d] = clean(from_inverted(w.get("abstract_inverted_index")))
    return out


def s2_batch(dois):
    out = {}
    for i in range(0, len(dois), 400):
        chunk = dois[i:i + 400]
        r = request("POST", S2, params={"fields": "abstract,externalIds"},
                    json={"ids": [f"DOI:{d}" for d in chunk]})
        time.sleep(3)
        for d, p in zip(chunk, r.json() if r else []):
            out[d] = clean(p.get("abstract")) if p else None
    return out


def crossref_one(doi):
    r = request("GET", f"{CROSSREF}/{doi}")
    time.sleep(1.0)
    return clean(r.json()["message"].get("abstract")) if r else None


def title_match(pub, hits):
    target = norm(pub["title"])
    best = None
    for h in hits:
        score = difflib.SequenceMatcher(None, target, norm(h["title"])).ratio()
        dom = "dominici" in h["authors"].lower()
        key = (round(score, 3), dom, h["abstract"] is not None)
        if best is None or key > best[0]:
            best = (key, {**h, "score": round(score, 3), "dominici_in_authors": dom})
    if not best:
        return None, None
    c = best[1]
    ok = c["score"] >= MIN_SCORE and (
        c["dominici_in_authors"]
        or (pub["year"] is not None and c["year"] is not None and abs(pub["year"] - c["year"]) <= 1
            and len(pub["title"].split()) >= 4))
    return ok, c


# --- main --------------------------------------------------------------------

def main():
    pubs = json.load(open(IN_PUBS, encoding="utf-8"))["publications"]
    bib = {r["scholar_pub_id"]: r for r in json.load(open(IN_BIB, encoding="utf-8"))["records"]}
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    for k in ("epmc_doi", "epmc_title", "openalex", "s2", "crossref"):
        cache.setdefault(k, {})

    def save():
        json.dump(cache, open(CACHE, "w"))

    dois = sorted({bib[p["scholar_pub_id"]]["doi"].lower() for p in pubs
                   if bib[p["scholar_pub_id"]]["doi"]})
    no_doi = [p for p in pubs if not bib[p["scholar_pub_id"]]["doi"]]
    print(f"{len(dois)} unique DOIs, {len(no_doi)} records without DOI", flush=True)

    # 1. Europe PMC by DOI
    for i, d in enumerate(dois, 1):
        if d not in cache["epmc_doi"]:
            hits = epmc_query(f'DOI:"{d}"', 5)
            hit = next((h for h in hits or [] if (h.get("doi") or "").lower() == d), None)
            cache["epmc_doi"][d] = epmc_slim(hit) if hit else None
        if i % 50 == 0:
            save()
            print(f"epmc doi {i}/{len(dois)}", flush=True)
    save()

    def abstract_for(d):
        """(abstract, source) from cached sources in priority order."""
        e = cache["epmc_doi"].get(d)
        if e and e["abstract"]:
            return e["abstract"], "europepmc"
        for src in ("openalex", "s2", "crossref"):
            if cache[src].get(d):
                return cache[src][d], src
        return None, None

    # 2-4. fallbacks, only for DOIs still missing an abstract
    todo = [d for d in dois if not abstract_for(d)[0] and d not in cache["openalex"]]
    cache["openalex"].update({**{d: None for d in todo}, **openalex_batch(todo)})
    save()
    todo = [d for d in dois if not abstract_for(d)[0] and d not in cache["s2"]]
    cache["s2"].update({**{d: None for d in todo}, **s2_batch(todo)})
    save()
    for d in [d for d in dois if not abstract_for(d)[0] and d not in cache["crossref"]]:
        cache["crossref"][d] = crossref_one(d)
    save()

    # 5. Europe PMC title search for records without a DOI
    for i, p in enumerate(no_doi, 1):
        pid = p["scholar_pub_id"]
        if pid not in cache["epmc_title"]:
            words = re.sub(r"[^\w\s-]", " ", html.unescape(p["title"])).split()
            hits = epmc_query("TITLE:(" + " ".join(words) + ")", 10) if len(words) >= 2 else []
            cache["epmc_title"][pid] = [epmc_slim(h) for h in hits or []] if hits is not None else None
        if i % 50 == 0:
            save()
            print(f"epmc title {i}/{len(no_doi)}", flush=True)
    save()

    records = []
    for p in pubs:
        pid = p["scholar_pub_id"]
        doi = bib[pid]["doi"]
        rec = {"scholar_pub_id": pid, "title": p["title"], "year": p["year"],
               "doi": doi, "pmid": None, "via": None, "abstract_source": None,
               "abstract": None, "title_match": None, "flags": []}
        if doi:
            d = doi.lower()
            rec["via"] = "doi"
            rec["pmid"] = (cache["epmc_doi"].get(d) or {}).get("pmid")
            rec["abstract"], rec["abstract_source"] = abstract_for(d)
        else:
            ok, c = title_match(p, cache["epmc_title"].get(pid) or [])
            if c:
                rec["title_match"] = {**{k: c[k] for k in ("title", "year", "score", "dominici_in_authors",
                                                           "pmid", "doi")}, "accepted": ok}
            if ok:
                rec["via"] = "title"
                rec["pmid"], rec["doi"] = c["pmid"], c["doi"]
                if c["abstract"]:
                    rec["abstract"], rec["abstract_source"] = c["abstract"], "europepmc"
        if rec["abstract"] and len(rec["abstract"]) < SHORT:
            rec["flags"].append("short_abstract")
        if rec["abstract"] and SUSPECT.search(rec["abstract"]):
            rec["flags"].append("suspect_abstract")
        records.append(rec)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"sources": [IN_PUBS, IN_BIB],
                   "method": "Europe PMC -> OpenAlex -> Semantic Scholar -> Crossref by DOI; "
                             "Europe PMC title search when no DOI",
                   "records": records}, f, ensure_ascii=False, indent=2)
        f.write("\n")

    n = sum(r["abstract"] is not None for r in records)
    by = {}
    for r in records:
        k = (r["via"], r["abstract_source"])
        by[k] = by.get(k, 0) + 1
    print(f"wrote {OUT}: {n}/{len(records)} with abstract; {by}")


if __name__ == "__main__":
    main()
