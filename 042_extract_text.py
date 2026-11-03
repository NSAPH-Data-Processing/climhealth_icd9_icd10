"""Step 4.2a: turn the files of the 15 shortlisted papers into plain text with location markers.

Input: 041_status.json (shortlisted papers), every parsable file in papers/<slug>/.
Writes papers/<slug>/text/<file name>.txt (git-ignored, like papers/), with the markers of Step 2.6 (036_extract_text.py).
PDFs are read with PyMuPDF, which keeps two-column pages in reading order. Zip files are not extracted.

Run: .venv/bin/python -I 042_extract_text.py
"""
import importlib.util
import json
import os
import re

import fitz

IN = "041_status.json"

_spec = importlib.util.spec_from_file_location("step36_extract", "036_extract_text.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def open_pdf(path):
    """Open a PDF. A truncated file that shows 0 pages gets a new page tree in memory (the file is not changed)."""
    pdf = fitz.open(path)
    if pdf.page_count:
        return pdf
    raw = open(path, "rb").read()
    found = []
    for m in re.finditer(rb"(\d+) 0 obj\s*<<", raw):
        body = raw[m.start():m.start() + 1500].split(b"endobj")[0]
        if re.search(rb"/Type\s*/Page(?![a-zA-Z])", body):
            found.append((m.start(), int(m.group(1))))
    kids = b" ".join(b"%d 0 R" % n for _, n in sorted(found))
    tail = (b"\nendstream\nendobj\n5001 0 obj\n<</Type/Pages/Count %d/Kids[%s]>>\nendobj\n"
            b"5002 0 obj\n<</Type/Catalog/Pages 5001 0 R>>\nendobj\ntrailer\n<</Root 5002 0 R/Size 5003>>\n%%%%EOF\n"
            % (len(found), kids))
    print("rebuilt page tree (%d pages): %s" % (len(found), path))
    return fitz.open(stream=raw + tail, filetype="pdf")


def pdf_text(path):
    out = []
    with open_pdf(path) as pdf:
        for i, page in enumerate(pdf, 1):
            out.append("=== page %d ===" % i)
            out.append(page.get_text())
    return "\n".join(out)


PARSERS = dict(base.PARSERS, **{".pdf": pdf_text})


def main():
    n = 0
    for item in json.load(open(IN, encoding="utf-8"))["items"]:
        folder = item["folder"]
        tdir = os.path.join(folder, "text")
        os.makedirs(tdir, exist_ok=True)
        for fname in sorted(os.listdir(folder)):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in PARSERS:
                continue
            txt = PARSERS[ext](os.path.join(folder, fname))
            with open(os.path.join(tdir, fname + ".txt"), "w", encoding="utf-8") as fh:
                fh.write(txt + "\n")
            n += 1
            print("%2d %8d chars  %s" % (item["unified_rank"], len(txt), os.path.join(folder, fname)), flush=True)
    print("wrote %d text files" % n)


if __name__ == "__main__":
    main()
