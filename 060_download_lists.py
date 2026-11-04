"""Step 6: download the official lists used by Steps 6.2 and 6.3, and save a machine-readable version of each.

Raw files go to official_lists/raw/ (git-ignored), with URL, date, size and sha256 in official_lists/downloads.json.
A failed download stops the build of the tables.

Output (committed):
  official_lists/ccw_adrd_27cc_2022.json    CCW ADRD algorithm, the version the papers cite (1999-2021, revised 02/2022)
  official_lists/ccs_icd9_2015.csv          ICD-9-CM code -> CCS category
  official_lists/ccsr_icd10_v2023_1.csv     ICD-10-CM code -> CCSR categories
  official_lists/gem_2018_icd9_to_icd10.csv, official_lists/gem_2018_icd10_to_icd9.csv   CMS GEMs, with flags

Run: .venv/bin/python 060_download_lists.py
"""
import csv
import hashlib
import io
import json
import os
import re
import time
import zipfile

import fitz
import requests

ROOT = "official_lists"
RAW = os.path.join(ROOT, "raw")
LOG = os.path.join(ROOT, "downloads.json")
CCW = "ccw_alzdisorders_archive_2022.pdf"
FILES = {
    # the cited link is dead (404), so this is the Internet Archive copy of that exact document
    CCW: "https://web.archive.org/web/20240228082945/https://www2.ccwdata.org/documents/10280/19139608/ccw-cond-algo-alzdisorders.pdf",
    "ccs_single_level_2015.zip": "https://hcup-us.ahrq.gov/toolssoftware/ccs/Single_Level_CCS_2015.zip",
    "ccsr_dx_v2023_1.zip": "https://hcup-us.ahrq.gov/toolssoftware/ccsr/DXCCSR_v2023-1.zip",
    "gem_2018.zip": "https://www.cms.gov/medicare/coding/icd10/downloads/2018-ICD-10-CM-General-Equivalence-Mappings.zip",
}


def download():
    os.makedirs(RAW, exist_ok=True)
    log = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else {}
    log = {k: v for k, v in log.items() if k in FILES}
    for name, url in FILES.items():
        path = os.path.join(RAW, name)
        if os.path.exists(path) and name in log:
            continue
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (research data download)"}, timeout=180)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        log[name] = {"url": url, "downloaded": time.strftime("%Y-%m-%d"), "bytes": len(r.content),
                     "sha256": hashlib.sha256(r.content).hexdigest()}
    with open(LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=1)
        f.write("\n")


def write_csv(name, header, rows):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print("wrote %s: %d rows" % (name, len(rows)))


def build_ccw():
    with fitz.open(os.path.join(RAW, CCW)) as doc:
        text = re.sub(r"\s+", " ", doc[0].get_text())
    i10 = re.search(r"Valid ICD-10 Codes2?: (.*?) \(any DX", text).group(1)
    i9 = re.search(r"Valid ICD-9 Codes2?: (.*?) \(any DX", text).group(1)
    out = {"name": "Alzheimer's Disease and Related Disorders or Senile Dementia", "version": "27 CCW Chronic Conditions, revised 02/2022",
           "source": FILES[CCW], "icd9": [c.strip().replace(".", "") for c in i9.split(",")],
           "icd10": [c.strip().replace(".", "") for c in i10.split(",")]}
    assert (len(out["icd9"]), len(out["icd10"])) == (24, 22), out
    with open(os.path.join(ROOT, "ccw_adrd_27cc_2022.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("wrote ccw_adrd_27cc_2022.json: %d ICD-9, %d ICD-10" % (len(out["icd9"]), len(out["icd10"])))


def build_ccs():
    with zipfile.ZipFile(os.path.join(RAW, "ccs_single_level_2015.zip")) as z:
        raw = z.read("$dxref 2015.csv").decode("latin-1")
    rows = []
    for r in csv.reader(io.StringIO(raw), quotechar="'"):
        if len(r) > 3 and r[0].strip() and r[0].strip() != "ICD-9-CM CODE" and r[1].strip().isdigit():
            rows.append([r[0].strip(), int(r[1].strip()), r[2].strip()])
    write_csv("ccs_icd9_2015.csv", ["icd9", "ccs", "ccs_description"], rows)


def build_ccsr():
    with zipfile.ZipFile(os.path.join(RAW, "ccsr_dx_v2023_1.zip")) as z:
        raw = z.read("DXCCSR_v2023-1.csv").decode("latin-1")
    reader = csv.reader(io.StringIO(raw))  # codes are in single quotes; only descriptions with commas use double quotes
    header = [h.strip("' ") for h in next(reader)]
    code_i, cat_i = header.index("ICD-10-CM CODE"), [header.index("CCSR CATEGORY %d" % i) for i in range(1, 7)]
    rows = []
    for r in reader:
        cats = [r[i].strip("' ") for i in cat_i]
        rows.append([r[code_i].strip("' "), " ".join(c for c in cats if c)])
    write_csv("ccsr_icd10_v2023_1.csv", ["icd10", "ccsr_categories"], rows)


def build_gem():
    with zipfile.ZipFile(os.path.join(RAW, "gem_2018.zip")) as z:
        for member, out, src, dst in (("2018_I9gem.txt", "gem_2018_icd9_to_icd10.csv", "icd9", "icd10"),
                                      ("2018_I10gem.txt", "gem_2018_icd10_to_icd9.csv", "icd10", "icd9")):
            rows = []
            for line in z.read(member).decode("latin-1").splitlines():
                p = line.split()
                if len(p) == 3:
                    rows.append([p[0], p[1]] + list(p[2]))
            write_csv(out, [src, dst, "approximate", "no_map", "combination", "scenario", "choice_list"], rows)


def main():
    download()
    build_ccw()
    build_ccs()
    build_ccsr()
    build_gem()


if __name__ == "__main__":
    main()
