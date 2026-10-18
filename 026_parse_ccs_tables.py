"""Step 2.6b: parse supplement tables that list the ICD codes of every disease group.

Outcome-wide papers (Step 2.6 rule: extract every group). Each parser reads a supplement file in
papers/ and returns one record per group: ids, names, the ICD codes as printed, and the page.

  parks2021  Parks et al. 2021 Nat Commun, Supplementary Table 2 (MOESM1, pp. 3-): CCS level 1
             and level 3 groups with their ICD-9-CM codes. Table cells are bounded by thin
             rectangles; a row that crosses a page break is merged. Level-3 groups printed in
             gray were not used in the paper's secondary CCS level 3 analyses (in_level3_analysis
             False); all of them count towards their level 1 cause. Codes are printed without
             the decimal point (e.g. 01000 = 010.00). suspect_codes flags printed codes that seem
             to have lost a leading digit.

Output: 026_ccs_tables.json (codes are factual lists; no copyrighted prose).
Run: .venv/bin/python 026_parse_ccs_tables.py
"""
import json
import re

import pdfplumber

OUT = "026_ccs_tables.json"
PARKS = "papers/10_1038_s41467_021_21777_1/41467_2021_21777_MOESM1_ESM.pdf"
CODE = re.compile(r"^(\d{3,5}|V\d{2,4}|E\d{3,4})$")
GRAY = (0.8509804, 0.8509804, 0.8509804)
STEP = 10000.0  # global y = page index * STEP + top


def hsep(p, x0, x1):
    """y positions of thin horizontal rectangles spanning [x0, x1] (table row borders)."""
    return sorted({round(r["top"], 1) for r in p.rects
                   if r["bottom"] - r["top"] < 2 and r["x0"] <= x0 + 2 and r["x1"] >= x1 - 2})


def rows_between(seps, items):
    """Group (y, item) by the interval between consecutive separators."""
    out = [[] for _ in range(len(seps) - 1)]
    for y, it in items:
        for i in range(len(seps) - 1):
            if seps[i] < y < seps[i + 1]:
                out[i].append(it)
                break
    return out


def suspect_codes(codes):
    """Codes that look like they lost a leading digit in print: their 3-character category is not
    shared by any other code of the group, but adding one leading digit gives the category of the
    next code (e.g. "4660" before "34661"). Kept as printed; listed here with the likely code."""
    out = []
    for i, c in enumerate(codes):
        if c[:3] in {o[:3] for j, o in enumerate(codes) if j != i} or i + 1 == len(codes):
            continue
        cand = [d + c for d in "0123456789" if (d + c)[:3] == codes[i + 1][:3]]
        if cand:
            out.append({"printed": c, "likely": cand[0]})
    return out


def merged_rows(seps, words, nx0, nx1):
    """Table rows with codes, each holding exactly one row number (x in [nx0, nx1)).

    A row that crosses a page break is split by the page border: a fragment without a number is
    joined to the row across the break (the previous row when the fragment starts a page, the
    next row when it ends one)."""
    cells, pending = [], []
    for i, cell in enumerate(rows_between(seps, words)):
        if not any(w["x0"] >= 352 and CODE.match(w["text"]) for w in cell):
            continue
        has_num = any(nx0 <= w["x0"] < nx1 and w["text"].isdigit() for w in cell)
        starts_page = int(seps[i] // STEP) != int(seps[i + 1] // STEP)
        if has_num:
            cells.append(pending + cell)
            pending = []
        elif starts_page and cells:
            cells[-1] += cell
        else:
            pending += cell
    assert not pending
    for cell in cells:
        cell.sort(key=lambda w: w["gy"] * 1000 + w["x0"])
    return cells


def parks2021():
    pdf = pdfplumber.open(PARKS)
    sep3, sep1, words = [], [], []
    for pi, p in enumerate(pdf.pages[2:], 2):
        text = p.extract_text() or ""
        if pi > 2 and "Supplementary Table" in text and "ICD9-CM" not in text:
            break  # next table
        g = pi * STEP
        sep3 += [g + y for y in hsep(p, 245, 352)]
        sep1 += [g + y for y in hsep(p, 72, 115)]
        for w in p.extract_words(extra_attrs=["non_stroking_color"]):
            w["page"], w["gy"] = pi + 1, g + w["top"] + 1
            words.append((w["gy"], w))
    sep3, sep1 = sorted(sep3), sorted(sep1)

    groups = []
    for cell in merged_rows(sep3, words, 200, 245):
        num = [w["text"] for w in cell if 200 <= w["x0"] < 245 and w["text"].isdigit()]
        desc = " ".join(w["text"] for w in cell if 245 <= w["x0"] < 352)
        codes = [w for w in cell if w["x0"] >= 352 and CODE.match(w["text"])]
        assert len(num) == 1, (num, desc)
        gray = {tuple(round(c, 4) for c in (w["non_stroking_color"] or ())) == tuple(round(c, 4) for c in GRAY)
                for w in codes}
        assert len(gray) == 1, "mixed gray/black codes in group %s" % num
        groups.append({"ccs_level3": num[0], "ccs_level3_name": re.sub(r"(\w)- (\w)", r"\1\2", desc),
                       "icd9_codes": [w["text"] for w in codes],
                       "in_level3_analysis": not gray.pop(),
                       "pages": sorted({w["page"] for w in codes}), "_y": min(w["gy"] for w in codes)})

    level1 = []
    for cell in merged_rows(sep1, words, 72, 115):
        num = [w["text"] for w in cell if 72 <= w["x0"] < 115 and w["text"].isdigit()]
        desc = " ".join(w["text"] for w in cell if 115 <= w["x0"] < 202)
        ys = [w["gy"] for w in cell]
        level1.append((num[0], re.sub(r"(\w)- (\w)", r"\1\2", desc), min(ys), max(ys)))
    for g in groups:
        for n, d, lo, hi in level1:
            if lo <= g["_y"] <= hi:
                g["ccs_level1"], g["ccs_level1_name"] = n, d
        del g["_y"]
    for g in groups:
        g["suspect_codes"] = suspect_codes(g["icd9_codes"])
    return {"source_file": PARKS, "table": "Supplementary Table 2", "groups": groups}


def main():
    out = {"parks2021": parks2021()}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for k, v in out.items():
        g = v["groups"]
        print("%s: %d groups, %d codes, %d in level-3 analysis, level1 %s"
              % (k, len(g), sum(len(x["icd9_codes"]) for x in g), sum(x["in_level3_analysis"] for x in g),
                 sorted({x.get("ccs_level1") for x in g}, key=lambda s: int(s or 0))))


if __name__ == "__main__":
    main()
