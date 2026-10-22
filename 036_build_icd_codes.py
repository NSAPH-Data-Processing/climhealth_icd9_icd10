"""Step 3.6c: one record per Step 2.4 paper with its data source and, per outcome, the ICD codes.

Inputs
  034_fulltext_manifest.json   the Step 3.4 papers (status, ids, Step 2.3 outcome_names)
  036_labels.json              hand labels (data source, outcomes, codes as written, quotes)
  026_ccs_tables.json          disease groups parsed from supplement tables (026_parse_ccs_tables.py)
  papers/<slug>/text/*.txt     extracted text (036_extract_text.py)

Each evidence quote is searched in the text of its file (case, spaces and punctuation ignored).
The location is the last marker before the match: "page N" for PDFs, "section: ..." or
"table: ..." for JATS XML, "table N" for DOCX. Quotes that are not found are all reported and stop the build.
Papers without full text get status no_fulltext and no outcomes.

Output: 036_icd_codes.json
Run: .venv/bin/python 036_build_icd_codes.py
"""
import json
import os
import re

MANIFEST = "034_fulltext_manifest.json"
LABELS = "036_labels.json"
TABLES = "026_ccs_tables.json"
OUT = "036_icd_codes.json"
STATUSES = {"explicit_codes", "classification_ref", "cites_prior_paper", "not_listed", "in_unfetched_supplement"}
POSITIONS = {"principal", "principal_or_secondary", "any", None}
LIGATURES = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}

_texts = {}
_missing = []


def normalized(text):
    """Lowercase alphanumerics of text, with a map from each kept char to its offset in text."""
    chars, offsets = [], []
    for i, ch in enumerate(text):
        for c in LIGATURES.get(ch, ch):
            if c.isalnum():
                chars.append(c.lower())
                offsets.append(i)
    return "".join(chars), offsets


def text_of(slug, fname):
    key = (slug, fname)
    if key not in _texts:
        path = os.path.join("papers", slug, "text", fname + ".txt")
        raw = open(path, encoding="utf-8").read()
        _texts[key] = (raw,) + normalized(raw)
    return _texts[key]


def locate(slug, ev):
    """{'file', 'location', 'quote'} for ev = [file, quote]; raises if the quote is absent."""
    fname, quote = ev
    raw, norm, offsets = text_of(slug, fname)
    q = normalized(quote)[0]
    i = norm.find(q)
    if not q or i < 0:
        _missing.append("quote not found in %s/%s: %r" % (slug, fname, quote))
        return None
    start = offsets[i]
    marker = None
    for m in re.finditer(r"^=== (.*) ===$", raw[:start], re.M):
        marker = m.group(1)
    loc = marker or "text"
    if loc.startswith("table: "):
        loc = "table: " + re.split(r"(?<=\.)\s|:\s", loc[7:].strip(), 1)[0].strip()
    elif loc.startswith("back: "):
        loc = "back matter"
    return {"file": fname, "location": loc, "quote": quote}


def versions(o):
    return [v for v, k in (("ICD-9", "icd9"), ("ICD-10", "icd10")) if o.get(k)]


def outcome_record(slug, o):
    assert o["codes_status"] in STATUSES, o
    assert o.get("position") in POSITIONS, o
    rec = {"outcome_name": o["name"], "step23_outcome_name": o["step23"], "role": o.get("role", "outcome"),
           "codes_status": o["codes_status"], "classification": o.get("classification"),
           "icd9": o.get("icd9", []), "icd10": o.get("icd10", []), "icd_versions": versions(o),
           "diagnosis_position": o.get("position"), "cites": o.get("cites"),
           "evidence": locate(slug, o["ev"]),
           "position_evidence": locate(slug, o["position_ev"]) if o.get("position_ev") else None,
           "note": o.get("note")}
    return rec


def parks_outcomes(table, slug, names):
    """Outcome records for every CCS level 1 cause and level 3 group of Parks et al. 2021."""
    title = locate(slug, [os.path.basename(table["source_file"]),
                          "Supplementary Table 2. ICD-9-CM codes per CCS Levels 1 and 3 used in analyses"])
    position = locate(slug, ["PMC7943804.1.pdf", "the date and principal ICD-9-CM code for each hospitalization "
                                                 "from the Medicare Provider Analysis and Review (MEDPAR) ﬁle"])

    def step23(level1_name):
        n = level1_name.lower()
        return n if n in names else "13 cause groups"

    def ev(pages):
        e = dict(title)
        e["location"] = "Supplementary Table 2, page%s %s" % ("s" if len(pages) > 1 else "",
                                                               "-".join(str(p) for p in (pages[0], pages[-1])[:len(set(pages))]))
        return e

    out, level1 = [], {}
    for g in table["groups"]:
        level1.setdefault((g["ccs_level1"], g["ccs_level1_name"]), []).append(g)
    for (n1, name1), groups in sorted(level1.items(), key=lambda kv: int(kv[0][0])):
        pages = sorted({p for g in groups for p in g["pages"]})
        out.append({"outcome_name": name1, "step23_outcome_name": step23(name1), "role": "outcome",
                    "codes_status": "explicit_codes", "classification": "AHRQ multi-level CCS level 1, cause %s" % n1,
                    "icd9": [], "icd10": [], "icd_versions": ["ICD-9"], "diagnosis_position": "principal",
                    "cites": None, "components_ccs_level3": [g["ccs_level3"] for g in groups],
                    "evidence": ev(pages), "position_evidence": position,
                    "note": "Codes = all codes of the component CCS level 3 groups listed below."})
        for g in groups:
            note = None
            if not g["in_level3_analysis"]:
                note = "Printed in gray: not used in the secondary CCS level 3 analyses (counted in its level 1 cause)."
            if g["suspect_codes"]:
                s = "; ".join("%s (likely %s)" % (c["printed"], c["likely"]) for c in g["suspect_codes"])
                note = ((note + " ") if note else "") + "Printed codes that seem to lack a leading digit: %s." % s
            out.append({"outcome_name": g["ccs_level3_name"], "step23_outcome_name": step23(name1),
                        "role": "component" if not g["in_level3_analysis"] else "outcome",
                        "codes_status": "explicit_codes",
                        "classification": "AHRQ CCS level 3 group %s (level 1 cause %s)" % (g["ccs_level3"], n1),
                        "icd9": g["icd9_codes"], "icd10": [], "icd_versions": ["ICD-9"],
                        "diagnosis_position": "principal", "cites": None, "evidence": ev(g["pages"]),
                        "position_evidence": position, "note": note})
    return out


def main():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))["papers"]
    labels = json.load(open(LABELS, encoding="utf-8"))["papers"]
    tables = json.load(open(TABLES, encoding="utf-8"))
    out, problems = [], []
    for p in manifest:
        rec = {k: p[k] for k in ("slug", "doi", "pmid", "pmcid", "year", "title")}
        rec.update({"fulltext_status": p["status"], "supplements_missing": p["supplements_missing"],
                    "step23_outcome_names": p["outcome_names"]})
        lab = labels.get(p["slug"])
        if p["status"] == "no_fulltext":
            assert lab is None, p["slug"]
            rec.update({"medpar_or_ffs": None, "data_source": None, "data_source_evidence": None,
                        "outcome_wide": None, "outcomes": []})
            out.append(rec)
            continue
        assert lab is not None, "no label for %s" % p["slug"]
        assert lab["medpar_ffs"] in ("stated", "implied"), p["slug"]
        rec.update({"medpar_or_ffs": lab["medpar_ffs"], "data_source": lab["source"],
                    "data_source_evidence": locate(p["slug"], lab["ev"]), "outcome_wide": lab.get("outcome_wide")})
        outs = [outcome_record(p["slug"], o) for o in lab["outcomes"]]
        if lab.get("ccs_table"):
            outs += parks_outcomes(tables[lab["ccs_table"]], p["slug"], set(p["outcome_names"]))
        for o in outs:
            if o["step23_outcome_name"] not in p["outcome_names"] + [None]:
                problems.append("%s: step23 name %r not in %s" % (p["slug"], o["step23_outcome_name"], p["outcome_names"]))
        rec["outcomes"] = outs
        out.append(rec)
    extra = set(labels) - {p["slug"] for p in manifest}
    assert not extra, extra
    if problems or _missing:
        raise SystemExit("\n".join(problems + _missing))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"sources": [MANIFEST, LABELS, TABLES], "papers": out}, f, ensure_ascii=False, indent=1)
        f.write("\n")

    n_out = [o for r in out for o in r["outcomes"]]
    print("wrote %s: %d papers, %d outcome entries" % (OUT, len(out), len(n_out)))
    print("  medpar_or_ffs:", {k: sum(1 for r in out if str(r["medpar_or_ffs"]) == k) for k in {str(r["medpar_or_ffs"]) for r in out}})
    print("  codes_status:", {k: sum(1 for o in n_out if o["codes_status"] == k) for k in STATUSES})
    print("  diagnosis_position:", {str(k): sum(1 for o in n_out if o["diagnosis_position"] == k) for k in POSITIONS})


if __name__ == "__main__":
    main()
