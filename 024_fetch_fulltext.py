"""Step 2.4: fetch full text and supplements for the papers whose ICD codes will be checked.

Scope: unique papers (by DOI, or Scholar id when there is no DOI) in 023_outcomes.json with
uses_medicare True, outcome True and uncertain False, minus conference abstracts.

Sources, in order (automated only; no Unpaywall, no manual downloads):
  1. PMC Article Datasets on AWS (public bucket pmc-oa-opendata): JATS XML, PDF and supplementary
     files, for the PMC open-access subset and NIH author manuscripts. PMCID resolved via Europe PMC.
  2. Europe PMC REST: fullTextXML and the supplementaryFiles zip (when the article is not on AWS).
  3. OpenAlex: open-access PDF (oa_locations[].pdf_url). No supplements from this source.
Figures (images) are not downloaded. Files go to papers/<slug>/ (git-ignored); the committed
output is the manifest 024_fulltext_manifest.json.

Requires the folder venv:  .venv/bin/python 024_fetch_fulltext.py
Already-downloaded files and API responses are reused (.cache/024_api.json), so re-runs resume.
"""
import io
import json
import os
import re
import time
import warnings
import zipfile
from xml.etree import ElementTree

warnings.filterwarnings("ignore")
import requests  # noqa: E402

IN = "023_outcomes.json"
OUT = "024_fulltext_manifest.json"
PAPERS = "papers"
CACHE = ".cache/024_api.json"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
S3 = "https://pmc-oa-opendata.s3.amazonaws.com"
OPENALEX = "https://api.openalex.org/works"
PAUSE = 0.5
IMAGE_EXT = {".jpg", ".jpeg", ".gif", ".png", ".tif", ".tiff", ".bmp", ".svg", ".webp"}

# Conference abstracts (no full paper exists): (DOI regex, reason)
CONFERENCE = [
    (r"^10\.1289/(isee|isesisee)\.", "ISEE conference abstract (EHP abstract DOI)"),
    (r"^10\.1097/01\.ee9\.", "Environmental Epidemiology meeting abstract (ISEE supplement)"),
    (r"^10\.1097/00001648-\d{6}001-", "Epidemiology journal supplement abstract (ISEE meeting)"),
]

session = requests.Session()
session.headers["User-Agent"] = "climhealth-icd9-icd10/0.1 (research script)"


def get(url, params=None, timeout=120):
    for attempt in range(4):
        try:
            r = session.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                return r
            if r.status_code in (403, 404, 410):
                return None
        except requests.RequestException:
            pass
        time.sleep(PAUSE * 2 ** (attempt + 1))
    return None


def slug_of(p):
    base = p["doi"] or "scholar_" + p["scholar_pub_id"]
    return re.sub(r"[^A-Za-z0-9]+", "_", base).strip("_")


def save(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


def is_pdf(b):
    return b[:5] == b"%PDF-"


def epmc_lookup(p, cache):
    """Europe PMC core record (pmcid, pmid) by DOI, else PMID."""
    key = p["doi"] or "PMID:%s" % p["pmid"]
    if key not in cache["epmc"]:
        if p["doi"]:
            q = 'DOI:"%s"' % p["doi"]
        elif p["pmid"]:
            q = "EXT_ID:%s AND SRC:MED" % p["pmid"]
        else:
            cache["epmc"][key] = None
            return None
        r = get(EPMC + "/search", {"query": q, "format": "json", "resultType": "core"})
        res = r.json()["resultList"]["result"] if r else []
        cache["epmc"][key] = ({k: res[0].get(k) for k in ("pmcid", "pmid", "isOpenAccess", "hasSuppl")}
                              if res else None)
        time.sleep(PAUSE)
    return cache["epmc"][key]


def s3_keys(pmcid):
    """Keys of the latest version folder of pmcid in the PMC AWS bucket."""
    r = get(S3 + "/", {"list-type": "2", "prefix": pmcid + "."})
    if not r:
        return []
    keys = re.findall(r"<Key>([^<]+)</Key>", r.text)
    versions = sorted({k.split("/")[0] for k in keys}, key=lambda v: int(v.split(".")[-1]))
    return [k for k in keys if versions and k.startswith(versions[-1] + "/")]


def referenced_supplements(xml_bytes):
    """Supplementary file names referenced in JATS XML (external URLs excluded)."""
    try:
        root = ElementTree.fromstring(xml_bytes)
    except ElementTree.ParseError:
        return []
    out = []
    for sm in root.iter("supplementary-material"):
        for el in sm.iter():
            href = el.get("{http://www.w3.org/1999/xlink}href")
            if href and not re.match(r"https?://", href) and os.path.splitext(href)[1].lower() not in IMAGE_EXT:
                out.append(href)
    return sorted(set(out))


def from_s3(pmcid, d):
    keys = s3_keys(pmcid)
    if not keys:
        return None
    folder = keys[0].split("/")[0]
    files = {"xml": None, "pdf": None, "supplements": []}
    for k in keys:
        name = k.split("/", 1)[1]
        ext = os.path.splitext(name)[1].lower()
        if ext in IMAGE_EXT or name in (folder + ".json", folder + ".txt"):
            continue
        local = os.path.join(d, name)
        if not os.path.exists(local):
            r = get(S3 + "/" + k)
            if not r:
                continue
            save(local, r.content)
        if name == folder + ".xml":
            files["xml"] = local
        elif name == folder + ".pdf":
            files["pdf"] = local
        else:
            files["supplements"].append(local)
    return files if (files["xml"] or files["pdf"]) else None


def from_epmc(pmcid, d, suppl_only=False):
    files = {"xml": None, "pdf": None, "supplements": []}
    local = os.path.join(d, pmcid + ".xml")
    if not suppl_only and not os.path.exists(local):
        r = get("%s/%s/fullTextXML" % (EPMC, pmcid))
        if r and r.content.lstrip()[:1] == b"<":
            save(local, r.content)
    if os.path.exists(local):
        files["xml"] = local
    zdone = os.path.join(d, ".epmc_suppl_done")
    if not os.path.exists(zdone):
        r = get("%s/%s/supplementaryFiles" % (EPMC, pmcid))
        if r and r.content[:2] == b"PK":
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                for n in z.namelist():
                    if n.endswith("/") or os.path.splitext(n)[1].lower() in IMAGE_EXT:
                        continue
                    save(os.path.join(d, os.path.basename(n)), z.read(n))
        save(zdone, b"")
    for n in sorted(os.listdir(d)):
        path = os.path.join(d, n)
        if n.startswith(".") or os.path.isdir(path) or n.endswith(".xml") and n.startswith(pmcid + "."):
            continue
        files["supplements"].append(path)
    return files if (files["xml"] or suppl_only) else None


def from_openalex(doi, d, cache):
    if doi not in cache["openalex"]:
        r = get("%s/doi:%s" % (OPENALEX, doi))
        w = r.json() if r else {}
        locs = [w.get("best_oa_location") or {}] + (w.get("locations") or [])
        urls = []
        for l in locs:
            if l.get("is_oa") and l.get("pdf_url") and l["pdf_url"] not in urls:
                urls.append(l["pdf_url"])
        cache["openalex"][doi] = urls
        time.sleep(PAUSE)
    local = os.path.join(d, "fulltext.pdf")
    if os.path.exists(local):
        return {"xml": None, "pdf": local, "supplements": [], "url": None}
    for url in cache["openalex"][doi]:
        r = get(url)
        if r and is_pdf(r.content):
            save(local, r.content)
            return {"xml": None, "pdf": local, "supplements": [], "url": url}
        time.sleep(PAUSE)
    return None


def scope():
    recs = json.load(open(IN, encoding="utf-8"))["records"]
    papers = {}
    for r in recs:
        if r["uses_medicare"] is True and r["outcome"] is True and not r["uncertain"]:
            p = papers.setdefault(r["paper_key"], dict(r, scholar_pub_ids=[]))
            p["scholar_pub_ids"].append(r["scholar_pub_id"])
    kept, dropped = [], []
    for p in papers.values():
        reason = next((why for rx, why in CONFERENCE if p["doi"] and re.match(rx, p["doi"])), None)
        (dropped if reason else kept).append((p, reason))
    return [p for p, _ in kept], [dict(p, reason=why) for p, why in dropped]


def main():
    kept, dropped = scope()
    os.makedirs(".cache", exist_ok=True)
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    cache.setdefault("epmc", {})
    cache.setdefault("openalex", {})

    manifest = []
    for i, p in enumerate(sorted(kept, key=lambda p: (p["year"] or 0, p["title"])), 1):
        slug = slug_of(p)
        d = os.path.join(PAPERS, slug)
        os.makedirs(d, exist_ok=True)
        info = epmc_lookup(p, cache) or {}
        pmcid = info.get("pmcid")
        pmid = p["pmid"] or info.get("pmid")
        files, source, url = None, None, None
        if pmcid:
            files = from_s3(pmcid, d)
            source = "pmc_aws" if files else None
            if files and not files["supplements"]:
                # some AWS author manuscripts carry only XML/text; try the Europe PMC supplement zip
                extra = from_epmc(pmcid, d, suppl_only=True)
                if extra:
                    files["supplements"] = [f for f in extra["supplements"]
                                            if f not in (files["xml"], files["pdf"])]
                    if files["supplements"]:
                        source = "pmc_aws+europepmc_suppl"
            if not files:
                files = from_epmc(pmcid, d)
                source = "europepmc" if files else None
        if not files and p["doi"]:
            files = from_openalex(p["doi"], d, cache)
            if files:
                source, url = "openalex_oa_pdf", files.pop("url")
        if not files:
            files = {"xml": None, "pdf": None, "supplements": []}
            if not os.listdir(d):
                os.rmdir(d)

        refs = []
        if files["xml"]:
            refs = referenced_supplements(open(files["xml"], "rb").read())
        got = {os.path.basename(f) for f in files["supplements"]}
        status = ("no_fulltext" if not (files["xml"] or files["pdf"])
                  else "fulltext" if files["supplements"] else "fulltext_no_supplements")
        manifest.append({
            "slug": slug, "doi": p["doi"], "pmid": pmid, "pmcid": pmcid,
            "year": p["year"], "title": p["title"], "scholar_pub_ids": p["scholar_pub_ids"],
            "outcome_names": p["outcome_names"],
            "status": status, "source": source, "source_url": url,
            "fulltext_xml": files["xml"], "fulltext_pdf": files["pdf"],
            "supplements": sorted(files["supplements"]),
            "supplements_referenced": refs,
            "supplements_missing": [r for r in refs if os.path.basename(r) not in got],
        })
        json.dump(cache, open(CACHE, "w"))
        print("%d/%d %s %s" % (i, len(kept), status, slug), flush=True)

    counts = {}
    for m in manifest:
        k = "%s/%s" % (m["status"], m["source"])
        counts[k] = counts.get(k, 0) + 1
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({
            "source": IN,
            "scope": "uses_medicare True, outcome True, uncertain False; unique by DOI; conference abstracts dropped",
            "n_in_scope": len(kept) + len(dropped), "n_dropped": len(dropped), "n_papers": len(manifest),
            "counts": counts,
            "dropped": [{"doi": p["doi"], "year": p["year"], "title": p["title"],
                         "scholar_pub_ids": p["scholar_pub_ids"], "reason": p["reason"]}
                        for p in sorted(dropped, key=lambda p: p["doi"])],
            "papers": manifest,
        }, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s: %d papers, %d dropped; %s" % (OUT, len(manifest), len(dropped), counts))


if __name__ == "__main__":
    main()
