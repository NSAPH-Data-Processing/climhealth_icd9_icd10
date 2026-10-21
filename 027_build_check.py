"""Step 2.7: one check row per Step 1 mapping: Step 1 codes vs the codes of the papers it cites.

Inputs
  010_icd_mappings.json   Step 1 rows (codes parsed into {type: code|range})
  012_publications.json   Step 1 CV numbers and the rows citing them
  026_icd_codes.json      Step 2.6 outcomes and codes per paper
  027_crosswalk.json      hand crosswalk: CV -> papers; row -> 026 outcomes compared

Comparison (separately for ICD-9 and ICD-10, only for versions present on both sides)
  Codes are reduced to 3-character categories (410.xx -> 410, 4280 -> 428, I21.x -> I21,
  E9500 -> E950); ranges are expanded (390-459 -> 390..459, I00-I99 -> I00..I99).
  Codes more specific than a category (518.82, 427.3) are also kept as exact codes.
  match            same categories, and the same exact codes when either side gives them
  match_category   same categories, but the exact codes differ (e.g. 518.82 vs 518.51-518.82)
  differs          categories differ; 'missing' = in Step 1 only, 'extra' = in the paper only
  not_comparable   the paper gives only classification groups (CCS) or no codes in that version
  no_evidence      no full text, codes in an unfetched supplement, not listed, or paper not in set
  not_applicable   a CV number maps to two papers and this one has no outcome for the row
Paper verdict = the worse of its ICD-9 / ICD-10 verdicts. Row verdict (cited papers only):
  supported (a paper matches), match_category, differs, not_comparable, no_evidence.
Papers under 'context' are shown with their verdicts but never change the row verdict.

Output: 027_step1_check.json, 027_step1_check.csv
Run: .venv/bin/python 027_build_check.py
"""
import csv
import json
import re

OUT_JSON = "027_step1_check.json"
OUT_CSV = "027_step1_check.csv"
RANK = ["match", "match_category", "differs", "not_comparable", "no_evidence", "not_applicable"]  # best -> worst
ROW_VERDICT = {"match": "supported", "match_category": "match_category", "differs": "differs",
               "not_comparable": "not_comparable", "no_evidence": "no_evidence", "not_applicable": "no_evidence"}
DASH = re.compile(r"\s*(?:–|—|-|\bto\b)\s*")
CODE = re.compile(r"^([A-Z]?)(\d+)(?:\.?([0-9X]*))?[A-Z]*$")


# ---------- code parsing ----------

def category(code):
    """('410', exact or None) for one code as written; None if it is not an ICD code."""
    c = code.strip().upper().replace("·", ".").replace("×", "X").replace(" ", "")
    m = CODE.match(c)
    if not m:
        return None
    letter, digits, rest = m.groups()
    if letter == "E":            # ICD-9 E codes: E950.x -> E950
        head, tail = digits[:3], digits[3:]
    elif letter:                 # ICD-10 / V codes: I21.4 -> I21
        head, tail = digits[:2], digits[2:]
    else:
        head, tail = digits[:3], digits[3:]
    if letter not in ("", "E") and len(digits) < 2 or letter in ("", "E") and len(digits) < 3:
        return None
    detail = (tail + (rest or "")).rstrip("X")
    cat = letter + head
    exact = None
    if detail and "X" not in detail:
        exact = cat + "." + detail
    return cat, exact


def expand(start, end):
    a, b = category(start), category(end)
    if not a or not b:
        return set(), set()
    (ca, ea), (cb, eb) = a, b
    la, lb = re.match(r"[A-Z]?", ca).group(), re.match(r"[A-Z]?", cb).group()
    if la != lb:
        return set(), set()
    n0, n1 = int(ca[len(la):]), int(cb[len(lb):])
    width = len(ca) - len(la)
    cats = {"%s%0*d" % (la, width, n) for n in range(n0, n1 + 1)}
    exact = set()
    if ca == cb and ea and eb:   # e.g. 992.0-992.9 or J67.0-J67.9: same category, keep both ends
        exact |= {ea, eb}
    return cats, exact


def parse_tokens(tokens):
    """Codes as written (list of strings) -> (categories, exact codes, unparsed tokens)."""
    cats, exact, bad = set(), set(), []
    for tok in tokens:
        t = re.sub(r"\([^)]*\)", "", tok).strip()
        m = re.match(r'codes beginning with "([A-Z])"', t)
        if m:
            cats |= {"%s%02d" % (m.group(1), n) for n in range(100)}
            continue
        for part in re.split(r"[,;]|\band\b|\bor\b", t):
            part = re.sub(r"^ICD-?\d+(-CM)?:?|except.*$", "", part.strip(), flags=re.I).strip()
            if not part:
                continue
            ends = DASH.split(part)
            if len(ends) == 2 and all(ends):
                c, e = expand(*ends)
            elif len(ends) == 1 and category(part):
                cat, ex = category(part)
                c, e = {cat}, ({ex} if ex else set())
            else:
                c, e = set(), set()
            if not c:
                bad.append(part)
            cats |= c
            exact |= e
    return cats, exact, bad


def step1_codes(field):
    """Step 1 icd9cm / icd10cm -> (categories, exact, raw); categories empty if unspecified."""
    toks = []
    for c in field.get("codes") or []:
        toks.append(c["code"] if c["type"] == "code" else "%s–%s" % (c["start"], c["end"]))
    cats, exact, _ = parse_tokens(toks)
    return cats, exact, field.get("raw")


def compact(cats):
    """Sorted categories as short ranges: ['410-414', '429']."""
    def key(c):
        m = re.match(r"([A-Z]?)(\d+)", c)
        return (m.group(1), int(m.group(2)))
    out, run = [], []
    for c in sorted(cats, key=key):
        if run and key(c)[0] == key(run[-1])[0] and key(c)[1] == key(run[-1])[1] + 1:
            run.append(c)
            continue
        if run:
            out.append(run[0] if len(run) == 1 else "%s-%s" % (run[0], run[-1]))
        run = [c]
    if run:
        out.append(run[0] if len(run) == 1 else "%s-%s" % (run[0], run[-1]))
    return out


# ---------- comparison ----------

def compare(s1, paper):
    """Verdict of one ICD version: s1 and paper are (cats, exact)."""
    (sc, se), (pc, pe) = s1, paper
    if not sc or not pc:
        return {"verdict": "not_comparable"}
    if sc != pc:
        return {"verdict": "differs", "missing": compact(sc - pc), "extra": compact(pc - sc),
                "overlap": bool(sc & pc)}
    if (se or pe) and se != pe:
        return {"verdict": "match_category", "step1_exact": sorted(se), "paper_exact": sorted(pe)}
    return {"verdict": "match"}


def worst(verdicts):
    vs = [v for v in verdicts if v != "not_comparable"] or verdicts
    return max(vs, key=RANK.index) if vs else "not_comparable"


def paper_codes(paper, names):
    """Union of the codes of the named outcomes of one 026 paper record."""
    by_name = {o["outcome_name"]: o for o in paper["outcomes"]}
    level3 = {}
    for o in paper["outcomes"]:
        m = re.match(r"AHRQ CCS level 3 group (\d+) ", o.get("classification") or "")
        if m:
            level3[m.group(1)] = o
    out = {"icd9": [], "icd10": [], "status": set(), "position": set(), "evidence": []}
    for n in names:
        o = by_name[n]  # KeyError = crosswalk out of sync with 026
        icd9 = list(o["icd9"])
        for g in o.get("components_ccs_level3") or []:
            icd9 += level3[g]["icd9"]
        if icd9 == ["union of the seven subtypes"]:
            icd9 = []
        out["icd9"] += icd9
        out["icd10"] += o["icd10"]
        out["status"].add(o["codes_status"])
        out["position"].add(o["diagnosis_position"])
        out["evidence"].append("%s, %s" % (o["evidence"]["file"], o["evidence"]["location"]))
    return out


def judge(row_codes, paper, names):
    codes = paper_codes(paper, names)
    status = codes["status"]
    if status & {"in_unfetched_supplement", "not_listed"} and not (codes["icd9"] or codes["icd10"]):
        return {"verdict": "no_evidence", "reason": "/".join(sorted(status)), "codes": codes}
    if not (codes["icd9"] or codes["icd10"]):
        return {"verdict": "not_comparable", "reason": "/".join(sorted(status)), "codes": codes}
    res, verdicts = {}, []
    for v in ("icd9", "icd10"):
        pc, pe, bad = parse_tokens(codes[v])
        c = compare(row_codes[v][:2], (pc, pe)) if codes[v] else {"verdict": "not_comparable"}
        if bad:
            c["unparsed_paper_codes"] = bad
        res[v] = c
        verdicts.append(c["verdict"])
    return {"verdict": worst(verdicts), "icd9": res["icd9"], "icd10": res["icd10"], "codes": codes}


def describe(label, j):
    """One-line text for the CSV."""
    v = j["verdict"]
    parts = [v]
    for k, name in (("icd9", "ICD-9"), ("icd10", "ICD-10")):
        c = j.get(k)
        if not c or c["verdict"] == "not_comparable":
            continue
        if c["verdict"] == "differs":
            parts.append("%s missing %s; extra %s" % (name, ",".join(c["missing"]) or "-", ",".join(c["extra"]) or "-"))
        elif c["verdict"] == "match_category":
            parts.append("%s exact codes %s vs %s" % (name, ",".join(c["step1_exact"]) or "-", ",".join(c["paper_exact"]) or "-"))
    if j.get("reason"):
        parts.append(j["reason"])
    return "%s: %s" % (label, "; ".join(parts))


# ---------- main ----------

def main():
    rows = json.load(open("010_icd_mappings.json", encoding="utf-8"))["mappings"]
    pubs = {str(p["cv"]): p for p in json.load(open("012_publications.json", encoding="utf-8"))}
    papers = {p["slug"]: p for p in json.load(open("026_icd_codes.json", encoding="utf-8"))["papers"]}
    cw = json.load(open("027_crosswalk.json", encoding="utf-8"))
    labels, cvmap, rowmap = cw["labels"], cw["cv"], cw["rows"]

    assert set(cvmap) == set(pubs), set(pubs) ^ set(cvmap)
    for cv, e in cvmap.items():
        for s in e["slugs"]:
            assert s in papers and s in labels, (cv, s)
    by_id = {r["id"]: r for r in rows}
    unmatched, out = [], []
    for r in rows:
        rec = {"id": r["id"], "section": r["section"], "outcome": r["outcome"],
               "step1_icd9": r["icd9cm"]["raw"], "step1_icd10": r["icd10cm"]["raw"],
               "publications": r.get("publications_raw")}
        if r["section"] != 1:
            rec.update({"row_verdict": "not_checked", "note": "Section 2: broader literature, not Dominici papers",
                        "papers": [], "context": []})
            out.append(rec)
            continue
        spec = rowmap.get(r["id"], {})
        ref = by_id[spec.get("compare_to", r["id"])]
        codes = {"icd9": step1_codes(ref["icd9cm"]), "icd10": step1_codes(ref["icd10cm"])}
        rec["compared_with"] = ref["id"] if ref is not r else None
        rec["step1_unspecified"] = not (codes["icd9"][0] or codes["icd10"][0])
        cvs = [cv for p in r["publications"] for cv in p["cv_numbers"]]
        items = []
        for cv in dict.fromkeys(cvs):
            entry = cvmap[cv]
            if not entry["slugs"]:
                items.append({"cv": cv, "paper": pubs[cv]["citation"], "slug": None,
                              "verdict": "no_evidence", "reason": entry["reason"]})
                continue
            for s in entry["slugs"]:
                done = [i for i in items if i["slug"] == s]
                if done:  # same paper cited under two CV numbers (e.g. #220, #268)
                    done[0]["cv"] += "/" + cv
                    continue
                p = papers[s]
                cited = spec.get("cited", {})
                names = next((cited[c][s] for c in cited if s in cited[c]), None)
                if p["fulltext_status"] == "no_fulltext":
                    j = {"verdict": "no_evidence", "reason": "no full text (Step 2.5 shortlist)"}
                elif names is None:
                    unmatched.append((r["id"], cv, s))
                    j = {"verdict": "not_applicable", "reason": "paper has no outcome matching this row"}
                elif rec["step1_unspecified"]:
                    j = judge(codes, p, names)
                    j = {"verdict": "not_comparable", "reason": "Step 1 gives no codes", "codes": j.get("codes")}
                else:
                    j = judge(codes, p, names)
                j.update({"cv": cv, "paper": labels[s], "slug": s, "outcomes": names})
                items.append(j)
        ctx = []
        for s, names in spec.get("context", {}).items():
            j = judge(codes, papers[s], names)
            j.update({"paper": labels[s], "slug": s, "outcomes": names})
            ctx.append(j)
        best = min((i["verdict"] for i in items), key=RANK.index) if items else "no_evidence"
        rec.update({"row_verdict": ROW_VERDICT[best], "papers": items, "context": ctx})
        out.append(rec)

    for k in rowmap:
        assert k in by_id, k
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"sources": ["010_icd_mappings.json", "012_publications.json", "026_icd_codes.json",
                               "027_crosswalk.json"], "rows": out},
                  f, ensure_ascii=False, indent=1, default=sorted)
        f.write("\n")

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "outcome", "step1_icd9", "step1_icd10", "row_verdict", "cited_papers", "context_papers"])
        for rec in out:
            w.writerow([rec["id"], rec["outcome"], rec["step1_icd9"], rec["step1_icd10"], rec["row_verdict"],
                        " | ".join(describe("#%s %s" % (i["cv"], i["paper"]), i) for i in rec["papers"]),
                        " | ".join(describe(i["paper"], i) for i in rec["context"])])

    print("wrote %s and %s: %d rows" % (OUT_JSON, OUT_CSV, len(out)))
    counts = {}
    for rec in out:
        counts[rec["row_verdict"]] = counts.get(rec["row_verdict"], 0) + 1
    print("  row verdicts:", counts)
    for u in unmatched:
        print("  not applicable (CV maps to another paper for this row):", u)


if __name__ == "__main__":
    main()
