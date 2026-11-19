"""gbv13_dhs_inspect.py - list Ethiopia DHS DV_ indicators with Gambela + national values (2016, 2024).
Run: python -I scripts/gbv13_dhs_inspect.py <raw/gbv3/dhs>"""
import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")
d = sys.argv[1]
nat = json.load(open(os.path.join(d, "dhs_et_dv_national.json"), encoding="utf-8"))
sub = json.load(open(os.path.join(d, "dhs_et_dv_subnational.json"), encoding="utf-8"))
print(sorted({r["CharacteristicLabel"] for r in sub if "amb" in r["CharacteristicLabel"].lower()}))
g = {}
for r in sub:
    if "gamb" in r["CharacteristicLabel"].lower():
        g[(r["SurveyId"], r["IndicatorId"])] = r
n = {(r["SurveyId"], r["IndicatorId"]): r for r in nat if r["CharacteristicCategory"] == "Total"}
for (s, i), r in sorted(g.items()):
    nv = n.get((s, i), {}).get("Value")
    print(s, i, "|", r["Indicator"][:110], "| Gam", r["Value"], "| CI", r.get("CILow"), r.get("CIHigh"),
          "| DenomW", r.get("DenominatorWeighted"), "DenomU", r.get("DenominatorUnweighted"), "| Nat", nv, "| lvl", r.get("RegionId"), r.get("CharacteristicLabel"))
