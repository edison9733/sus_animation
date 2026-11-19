"""gbvcheck02_dhs.py - independent check of DHS rows in data/gambella_safety_gbv.csv against a fresh
DHS API download (raw/gbvcheck/dhs_{sub,nat}.json from gbvcheck01_redownload.sh). Also compares sha256 of
re-downloaded files with the earlier copies in raw/gbv3/web. Run: python -I scripts/gbvcheck02_dhs.py"""
import json, csv, os, hashlib, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
sub = json.load(open(R("raw/gbvcheck/dhs_sub.json"), encoding="utf-8"))["Data"]
nat = json.load(open(R("raw/gbvcheck/dhs_nat.json"), encoding="utf-8"))["Data"]
print("fresh API rows", len(sub), len(nat))
print("surveys with DV data:", sorted({r["SurveyId"] for r in nat}))
print("Gambela labels:", sorted({r["CharacteristicLabel"] for r in sub if "gamb" in r["CharacteristicLabel"].lower()}))
rows = list(csv.DictReader(open(R("data/gambella_safety_gbv.csv"), encoding="utf-8-sig")))
bad = 0; checked = 0
for i, r in enumerate(rows, start=2):
    if not r["source"].startswith("DHS Program API"): continue
    ind = re.search(r"\[(DV_\w+)\]", r["indicator"]).group(1)
    sid = re.search(r"(ET\d{4}DHS)", r["source"]).group(1)
    data = sub if r["admin_level"] == "region" else nat
    cand = [d for d in data if d["IndicatorId"] == ind and d["SurveyId"] == sid and d["IsPreferred"] == 1 and
            (("gamb" in d["CharacteristicLabel"].lower()) if r["admin_level"] == "region" else d["CharacteristicCategory"].startswith("Total"))]
    checked += 1
    if len(cand) != 1 or str(cand[0]["Value"]) != str(float(r["value"])) and float(cand[0]["Value"]) != float(r["value"]):
        bad += 1; print("MISMATCH line", i, ind, sid, r["value"], [(c["Value"], c["CharacteristicLabel"]) for c in cand])
    else:
        c = cand[0]
        if f"n={c['DenominatorUnweighted']} unweighted (weighted {c['DenominatorWeighted']})" not in r["sample"]:
            bad += 1; print("SAMPLE MISMATCH line", i, r["sample"], c["DenominatorUnweighted"], c["DenominatorWeighted"])
print("DHS rows checked", checked, "problems", bad)
# which DV indicators exist for Gambela per survey but are missing from the CSV
have = {(re.search(r"(ET\d{4}DHS)", r["source"]).group(1), re.search(r"\[(DV_\w+)\]", r["indicator"]).group(1), r["admin_level"])
        for r in rows if r["source"].startswith("DHS")}
for lvl, data, test in (("region", sub, lambda d: "gamb" in d["CharacteristicLabel"].lower()), ("national", nat, lambda d: d["CharacteristicCategory"].startswith("Total"))):
    avail = {(d["SurveyId"], d["IndicatorId"], lvl) for d in data if d["IsPreferred"] == 1 and test(d)}
    print(lvl, "available but missing from CSV:", sorted(avail - have))
# hashes vs earlier copies
for f in sorted(os.listdir(R("raw/gbvcheck"))):
    old = R("raw/gbv3/web", f)
    if os.path.exists(old) and not f.endswith(".txt"):
        h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
        print(f, "same" if h(old) == h(R("raw/gbvcheck", f)) else "DIFFERENT")
