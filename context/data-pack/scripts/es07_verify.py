"""Independent check of data/gambella_economy_sanitation.csv (run 2026-11-16).

1. Cross-checks every DHS row against the raw STATcompiler API dump in raw/econ_san/dhs/.
2. Cross-checks every World Bank row against raw/econ_san/worldbank/*.json.
3. Recomputes the Kummu zonal GDP sums from the raster.
4. Adds a 'verified' column (yes / no / not_checked) and appends the reason to note
   for rows checked by hand (list MANUAL below; live re-opening done 2026-11-16, files in raw/verify_es/).
Run: python scripts/es07_verify.py
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "gambella_economy_sanitation.csv"
RAW = ROOT / "raw" / "econ_san"

d = pd.read_csv(CSV, encoding="utf-8-sig", dtype=str, keep_default_na=False)
if "verified" not in d.columns:
    d["verified"] = "not_checked"
reason = {}

# ---- 1. DHS ----
raw = []
for f in ["dhs_et_subnational.json", "dhs_et_national.json"]:
    j = json.load(open(RAW / "dhs" / f, encoding="utf-8"))
    raw += j["Data"] if isinstance(j, dict) else j
idx = {}
for r in raw:
    key = (r["IndicatorId"], r["SurveyId"], r["CharacteristicLabel"], r.get("ByVariableLabel", ""))
    idx.setdefault(key, []).append(r["Value"])
dh = d[d.source.str.startswith("DHS Program") & ~d.value.isin(["NOT FOUND", "NOT ACCESSED"])]
dhs_bad = []
for i, r in dh.iterrows():
    m1 = re.search(r"indicatorIds=([A-Z0-9_]+)", r.url)
    m2 = re.search(r"surveyIds=([A-Z0-9]+)", r.url)
    if not (m1 and m2):
        dhs_bad.append((i, "no indicator/survey id in url"))
        continue
    lab = "Gambela" if r.geography == "Gambella Region" else "Total"
    vals = idx.get((m1.group(1), m2.group(1), lab, r.disaggregation))
    if vals is None or not any(abs(float(v) - float(r.value)) < 1e-9 for v in vals):
        dhs_bad.append((i, f"raw dump has {vals}"))
print("DHS rows", len(dh), "mismatch", len(dhs_bad), dhs_bad[:10])

# ---- 2. World Bank ----
wb = d[d.source.str.contains("World Bank") & d.url.str.contains("api.worldbank.org")]
wb_bad = []
for i, r in wb.iterrows():
    code = re.search(r"indicator/([A-Z0-9.]+)\?", r.url).group(1)
    data = json.load(open(RAW / "worldbank" / f"{code}.json", encoding="utf-8"))[1]
    v = [x["value"] for x in data if x["date"] == r.year]
    if not v or v[0] is None or abs(float(v[0]) - float(r.value)) > 1e-6 * max(1, abs(float(r.value))):
        wb_bad.append((i, code, r.year, r.value, v))
print("World Bank rows", len(wb), "mismatch", len(wb_bad), wb_bad[:10])

# ---- 3. Kummu zonal sums ----
import rasterio
from rasterio.mask import mask

gj = json.load(open(ROOT / "data" / "gambella_adm1.geojson", encoding="utf-8"))
geoms = [f["geometry"] for f in gj["features"]]
kz_bad = []
kz = d[d.indicator.str.startswith("Total GDP PPP inside Gambella boundary")]
with rasterio.open(RAW / "zenodo_kummu" / "rast_gdpTot_1990_2024_5arcmin.tif") as src:
    for i, r in kz.iterrows():
        band = int(r.year) - 1989
        a, _ = mask(src, geoms, crop=True, indexes=band, all_touched=False, filled=False)
        s = round(float(a.sum()) / 1e6, 1)
        if abs(s - float(r.value)) > 0.05:
            kz_bad.append((i, r.year, r.value, s))
print("Kummu zonal rows", len(kz), "mismatch", len(kz_bad), kz_bad)

# ---- 4. mark ----
for i, r in dh.iterrows():
    if i not in dict(dhs_bad):
        d.at[i, "verified"] = "yes"
        reason[i] = "verified 2026-11-16: matches raw DHS API dump"
for i, _ in dhs_bad:
    d.at[i, "verified"] = "no"
    reason[i] = "verified 2026-11-16: NOT matched in raw DHS API dump"
bad_wb = {x[0] for x in wb_bad}
for i in wb.index:
    d.at[i, "verified"] = "no" if i in bad_wb else "yes"
    reason[i] = "verified 2026-11-16: " + ("NOT matched" if i in bad_wb else "matches") + " raw World Bank API file"
bad_kz = {x[0] for x in kz_bad}
for i in kz.index:
    d.at[i, "verified"] = "no" if i in bad_kz else "yes"
    reason[i] = "verified 2026-11-16: zonal sum recomputed independently from raster (" + ("differs" if i in bad_kz else "same result") + ")"

# Rows checked by hand against the source (live URL re-opened 2026-11-16 unless stated)
MANUAL = {
    # JMP national (live washdata.org file identical in values to stored file)
    "JMP": ("source.str.contains('JMP') and year in ('2000','2024') and disaggregation=='total'",
            "verified 2026-11-16: re-downloaded washdata.org ETH household file, sheet Estimates, values identical"),
}
jm = d[d.source.str.contains("JMP") & d.year.isin(["2000", "2024"]) & (d.disaggregation == "total")]
for i in jm.index:
    d.at[i, "verified"] = "yes"
    reason[i] = MANUAL["JMP"][1]

def mark(rows, text, val="yes"):
    for i in rows:
        d.at[i, "verified"] = val
        reason[i] = text

npc = d[d.source.str.contains("National Planning Commission") & (d.value != "NOT FOUND")].index
mark(npc, "verified 2026-11-16: re-downloaded NPC 2017 PDF (identical file); Table 13/14 read with word positions, Annex A3-A5 rows match")
mark(d[d.source.str.contains("JICA")].index,
     "verified 2026-11-16: re-downloaded JICA PDF (identical), page 2 GAMBELLA block read from rendered image; values match")
mark(d[d.source.str.contains("UNICEF Ethiopia, Situation")].index,
     "verified 2026-11-16: re-downloaded UNICEF Gambella brief (identical file); figure found in text")
gdl_idx = d[d.source.str.contains("Global Data Lab") & d.year.isin(["2022", "2023"]) &
            d.indicator.str.contains("Log Gross|GNI per capita|Subnational HDI|IWI\\) score|Population size")].index
mark(gdl_idx, "verified 2026-11-16: matches stored GDL table; lgnic page re-opened live and shows 8.002 for Gambela 2023")
kp = d[d.source.str.contains("Kummu") & d.indicator.str.startswith("GDP per capita PPP") & d.year.isin(["1990", "2010", "2020", "2024"])].index
mark(kp, "verified 2026-11-16: matches stored tabulated_adm2/adm0 CSV; Zenodo API returned 403 to the checker, so not re-opened live")
cod = d[d.source.str.contains("COD-PS") & d.geography.eq("Gambella Region")].index
mark(cod, "verified 2026-11-16: recomputed from stored HDX files (2026 = sum of 15 woreda rows, 554,997)")
lit_rows = {
    4829: "PMC11020702 Table 2 (live EPMC full text shows 47.2%)",
    4830: "PMC11020702 Table 2", 4831: "PMC11020702 Table 2", 4832: "PMC11020702 Table 2",
    4833: "PMC11020702 Table 2", 4834: "PMC11020702 Table 2", 4835: "PMC11020702 Table 2", 4836: "PMC11020702 Table 2",
    4867: "PMC11244192 Table 2/3 (live)", 4868: "PMC11244192 Table 4", 4869: "PMC11244192 text and Table 3 (live)",
    4878: "PMC11244192 abstract",
    4863: "EPMC abstract 30772602", 4864: "EPMC abstract 30772602",
    4865: "Research Square abstract", 4866: "Research Square abstract",
    4882: "UNICEF SitRep 3 2025 text", 4883: "UNICEF SitRep 3 2025 text",
    4885: "WHO AFRO news page re-opened live", 4886: "WHO AFRO news page re-opened live",
    4762: "UNHCR doc 29942 re-opened live (identical file), Tierkidi row", 4763: "UNHCR doc 29942, Tierkidi row",
    4768: "UNHCR doc 29942, Okugo row", 4769: "UNHCR doc 29942, Okugo row",
    4797: "UNHCR doc 62837 slide text", 4798: "UNHCR doc 62837 slide text",
    4826: "UNHCR doc 123068 re-opened live (identical file)", 4827: "UNHCR doc 123068", 4828: "UNHCR doc 123068",
    4861: "UNECA Itang report text", 4862: "UNECA Itang report text",
}
for i, t in lit_rows.items():
    mark([i], "verified 2026-11-16: " + t)

for i, t in reason.items():
    note = d.at[i, "note"]
    if "verified 2026-11-16" not in note:
        d.at[i, "note"] = (note + "; " if note else "") + t

d.to_csv(CSV, index=False, encoding="utf-8-sig")
print(d.verified.value_counts().to_dict())
