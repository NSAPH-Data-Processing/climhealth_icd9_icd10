"""Step 2: fetch Francesca Dominici's publication list from her Google Scholar profile
into 020_scholar_publications.json. Independent of the Step 1 mappings.

Uses the profile list view only (title, year, venue, citation count); author lists
would need one request per publication and are not fetched.

Requires the folder venv:  .venv/bin/python 020_fetch_scholar.py
"""
import collections
import datetime
import json
import re
import warnings

warnings.filterwarnings("ignore")
from scholarly import scholarly  # noqa: E402

SCHOLAR_ID = "RSwElNMAAAAJ"
OUT = "020_scholar_publications.json"

author = scholarly.fill(scholarly.search_author_id(SCHOLAR_ID),
                        sections=["basics", "indices", "publications"])
pubs = []
for p in author["publications"]:
    bib = p.get("bib", {})
    year = bib.get("pub_year")
    pubs.append({
        "scholar_pub_id": p.get("author_pub_id"),
        "title": bib.get("title"),
        "year": int(year) if year and year.isdigit() else None,
        "venue": bib.get("citation") or None,
        "num_citations": p.get("num_citations", 0),
    })
pubs.sort(key=lambda x: (-(x["year"] or 0), x["title"] or ""))

# Flag (never drop) records that later steps may want to exclude.
JUNK = re.compile(r"europe pmc|publish ahead of print|^final[–-]|workshop", re.I)
title_n = collections.Counter((p["title"] or "").lower().strip() for p in pubs)
for p in pubs:
    t = p["title"] or ""
    flags = []
    if p["year"] is None:
        flags.append("no_year")
    if p["venue"] is None:
        flags.append("no_venue")
    if title_n[t.lower().strip()] > 1:
        flags.append("duplicate_title")
    if len(t.split()) < 4 or JUNK.search(t):
        flags.append("suspect_title")
    p["flags"] = flags

doc = {
    "source": f"https://scholar.google.com/citations?user={SCHOLAR_ID}",
    "retrieved": datetime.date.today().isoformat(),
    "author": author["name"],
    "affiliation": author.get("affiliation"),
    "total_citations": author.get("citedby"),
    "h_index": author.get("hindex"),
    "n_publications": len(pubs),
    "flag_definitions": {
        "no_year": "Scholar gives no publication year.",
        "no_venue": "Scholar gives no venue/citation string.",
        "duplicate_title": "Same title (case-insensitive) appears more than once in the profile.",
        "suspect_title": "Title has < 4 words or looks like a non-article artifact "
                         "(e.g. 'Europe PMC free article', 'Publish Ahead of Print', workshop listings).",
    },
    "publications": pubs,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"wrote {OUT}: {len(pubs)} publications")
