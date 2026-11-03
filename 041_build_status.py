"""Step 4.1: record the status of each shortlisted paper's manual download. Re-run after each download.

Input: 040_shortlist.json (shortlisted papers), DOWNLOADS below (hand record), files in papers/<slug>/.
A paper is "downloaded" when it is in DOWNLOADS and every listed file is on disk, otherwise "pending".

Output: 041_status.json
Run: .venv/bin/python 041_build_status.py
"""
import json
import os

IN = "040_shortlist.json"
OUT = "041_status.json"

# unified rank -> (source, access, article file, supplement files, note)
DOWNLOADS = {
    1: ("JAMA", "harvard_signin", "article.pdf", [], "No supplement link found on the page."),
    2: ("JAMA", "harvard_signin", "article.pdf", [], "No supplement link found on the page."),
    3: ("Oxford Academic", "user_download", "article.pdf", ["kws267-kws267_web_material.pdf"], None),
    4: ("Chest journal site", "user_download", "article.pdf", ["mmc1.pdf"], None),
    5: ("The Lancet Planetary Health", "open_access", "article.pdf", ["supplement_mmc1.pdf"], None),
    6: ("Oxford Academic", "user_download", "article.pdf", ["web_material_kwae133.zip", "Causal_AD_ADRD Supp.pdf"],
        "The zip also holds latex.zip, left unextracted."),
    7: ("PMC", "user_download", "article.pdf", ["NIHMS823701-supplement-Supplemental.docx"], None),
    8: ("PMC", "user_download", "article.pdf", ["NIHMS944332-supplement.docx"], None),
    9: ("PMC", "user_download", "article.pdf",
        ["NIHMS657527-supplement-Hospitalizations_and_heat_waves_-_Supplemental_Material.pdf"], None),
    10: ("Taylor & Francis", "harvard_signin", "article.pdf",
         ["uasa_a_1722134_sm0458.pdf", "uasa_a_1722134_sm0459.pdf"], "The supplements are free."),
    11: ("PMC", "user_download", "PMC8852365.1.xml",
         ["NIHMS1763059-supplement-eAppendix_1.pdf", "NIHMS1763059-supplement-eAppendix_2.pdf",
          "NIHMS1763059-supplement-eAppendix_3.pdf"], "Supplements only; the full text is from Step 2.4."),
    12: ("PMC", "user_download", "article.pdf", ["NIHMS1662172-supplement-Supplemental_Digital_Content.pdf"], None),
    13: ("ScienceDirect", "user_download", "article.pdf", ["1-s2.0-S0160412023001174-mmc1.docx"], None),
    14: ("JAMA Network", "harvard_signin", "article.pdf", ["ioi240093supp1_prod_1743791974.59513.pdf"],
         "Supplement 2 (data sharing statement) skipped."),
    15: ("Oxford Academic", "harvard_signin", "article.pdf",
         ["web_material_kwag087.zip", "Supplementary_materials_kwag087.pdf"],
         "The PDF is the only file in the zip."),
}


def record(i):
    r = {"unified_rank": i["unified_rank"], "title": i["title"], "year": i["year"], "doi": i["doi"],
         "folder": i["save_to"], "gap": i["gap"], "status": "pending", "source": None, "access": None,
         "article": None, "supplements": [], "note": None}
    if i["unified_rank"] in DOWNLOADS:
        source, access, article, supps, note = DOWNLOADS[i["unified_rank"]]
        missing = [f for f in [article] + supps if not os.path.exists(os.path.join(i["save_to"], f))]
        assert not missing, "rank %d: not on disk: %s" % (i["unified_rank"], missing)
        r.update(status="downloaded", source=source, access=access, article=article, supplements=supps, note=note)
    return r


def main():
    items = [record(i) for i in json.load(open(IN, encoding="utf-8"))["items"] if i["shortlist"]]
    counts = {s: sum(r["status"] == s for r in items) for s in ("downloaded", "pending")}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"source": IN, "n_shortlisted": len(items), "counts": counts, "items": items},
                  f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s: %s" % (OUT, counts))


if __name__ == "__main__":
    main()
