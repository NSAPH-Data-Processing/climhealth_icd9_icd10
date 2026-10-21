"""Step 1.3a: parse the numbered journal articles of Dominici_CV_updated_10132026.pdf.

The "Journal Articles (peer reviewed)" section numbers each article ("78. Peng R, ... (2008).
Title. Journal, vol:pages. PMID ...; doi:..."). Text comes from poppler's pdftotext -layout;
entries are joined across lines, with words hyphenated at a line end rejoined.

Output: 013_cv_articles.json — one record per article: n, authors, first_author, year, title,
journal_etc (the rest of the entry), doi, pmid, page.
Run: .venv/bin/python 013_parse_cv.py
"""
import json
import re
import subprocess

PDF = "Dominici_CV_updated_10132026.pdf"
OUT = "013_cv_articles.json"
START = "Journal Articles (peer reviewed"
END = "Books"
ENTRY = re.compile(r"^\s{0,3}(\d{1,3})\.\s+(\S.*)$")


def main():
    raw = subprocess.run(["pdftotext", "-layout", PDF, "-"], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, check=True).stdout.decode("utf-8")
    entries, cur, inside, page = [], None, False, 1
    for line in raw.split("\n"):
        page += line.count("\f")
        line = line.replace("\f", "")
        if START in line:
            inside = True
            continue
        if inside and line.strip() == END:
            break
        if not inside or not line.strip():
            continue
        m = ENTRY.match(line)
        if m and (cur is None or int(m.group(1)) == cur["n"] + 1):
            cur = {"n": int(m.group(1)), "text": m.group(2).strip(), "page": page}
            entries.append(cur)
        elif cur is not None and re.match(r"^\s{3,}\S", line):
            t = line.strip()
            cur["text"] = cur["text"][:-1] + t if cur["text"].endswith("-") and t[:1].islower() \
                else cur["text"] + " " + t

    out = []
    for e in entries:
        m = re.match(r"(.*?)\s*\((\d{4})[a-z]?\)\.?\s*(.*)", e["text"])
        if m:   # "Authors (2008). Title. Journal ..."
            authors, year, rest = m.group(1), int(m.group(2)), m.group(3)
            title, _, journal = rest.partition(". ")
        else:   # a few late entries: "Authors. Title. Journal. 2025;vol:pages."
            authors, _, rest = e["text"].partition(". ")
            title, _, journal = re.sub(r"^(?<=\.)(\S)", r" \1", rest).partition(". ")
            y = re.search(r"\b(20\d{2});", journal)
            year = int(y.group(1)) if y else None
        # a DOI broken at a hyphen across lines ("S2542- 5196(21)...") is rejoined
        doi = re.search(r"doi:\s*(10\.[^\s;]+?(?:-\s+[^\s;]+?)?)\.?(?:\s|$)", e["text"], re.I)
        pmid = re.search(r"PMID:\s*(\d+)", e["text"])
        first = re.split(r",| and ", authors)[0].strip()
        out.append({"n": e["n"], "first_author": first.split(" ")[0] if first else None,
                    "authors": authors, "year": year, "title": title.strip(), "journal_etc": journal.strip(),
                    "doi": re.sub(r"\s+", "", doi.group(1)).lower() if doi else None, "pmid": pmid.group(1) if pmid else None,
                    "page": e["page"], "text": e["text"]})
    nums = [o["n"] for o in out]
    assert nums == list(range(1, len(nums) + 1)), "numbering gap"
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"source": PDF, "section": START + ")", "articles": out}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote %s: %d articles (1-%d), %d with DOI, %d without year"
          % (OUT, len(out), nums[-1], sum(1 for o in out if o["doi"]), sum(1 for o in out if not o["year"])))


if __name__ == "__main__":
    main()
