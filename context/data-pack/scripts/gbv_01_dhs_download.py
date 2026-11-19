"""GBV/safety theme: download DHS Program API domestic-violence indicators for Ethiopia (all surveys),
national + subnational. Usage: python gbv_01_dhs_download.py <raw/gbv dir>
Writes dhs_indicators.json, dhs_et_dv_national.json, dhs_et_dv_subnational.json"""
import json, sys, os, time, urllib.request
out = sys.argv[1]
def get(u):
    for a in range(4):
        try:
            return json.load(urllib.request.urlopen(u, timeout=120))
        except Exception as e:
            print("retry", e); time.sleep(5)
    raise SystemExit("failed " + u)
ind = get("https://api.dhsprogram.com/rest/dhs/indicators?f=json&perpage=5000")
allind = ind["Data"]
p = 1
while p < ind["TotalPages"]:
    p += 1
    allind += get("https://api.dhsprogram.com/rest/dhs/indicators?f=json&perpage=5000&page=%d" % p)["Data"]
json.dump(allind, open(os.path.join(out, "dhs_indicators.json"), "w", encoding="utf-8"))
ids = sorted(i["IndicatorId"] for i in allind if i["IndicatorId"].startswith("DV_"))
print(len(allind), "indicators;", len(ids), "DV_ ids")
for bd in ("national", "subnational"):
    rows = []
    for k in range(0, len(ids), 20):
        chunk = ",".join(ids[k:k+20]); page = 1
        while True:
            d = get("https://api.dhsprogram.com/rest/dhs/data?countryIds=ET&breakdown=%s&indicatorIds=%s&f=json&perpage=1000&page=%d" % (bd, chunk, page))
            rows += d["Data"]
            if page >= d["TotalPages"]: break
            page += 1
    json.dump(rows, open(os.path.join(out, "dhs_et_dv_%s.json" % bd), "w", encoding="utf-8"))
    print(bd, len(rows), sorted({r["SurveyId"] for r in rows}))
