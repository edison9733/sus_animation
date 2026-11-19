"""PubMed E-utilities searches for the GBV/safety theme. Saves raw JSON to raw/gbv/."""
import json, sys, time, io
sys.stdout.reconfigure(encoding="utf-8")
import json, sys, time, urllib.parse, urllib.request
OUT = sys.argv[1]
QUERIES = {
 "gambella_violence": '(Gambella OR Gambela) AND (violence OR rape OR "gender-based" OR harassment)',
 "ssd_refugee_eth_violence": '("South Sudanese" AND refugee* AND Ethiopia) AND (violence OR rape)',
 "sanitation_violence": '(sanitation OR toilet* OR latrine* OR "open defecation") AND ("sexual violence" OR "non-partner" OR rape OR "gender-based violence")',
 "refugee_latrine_safety": '(refugee* OR displaced OR camp) AND (latrine* OR toilet*) AND (safety OR violence) AND (women OR girls)',
}
base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
for k, q in QUERIES.items():
    u = base + "esearch.fcgi?db=pubmed&retmode=json&retmax=60&term=" + urllib.parse.quote(q)
    ids = json.load(urllib.request.urlopen(u, timeout=60))["esearchresult"]["idlist"]
    time.sleep(0.5)
    s = {}
    if ids:
        u2 = base + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids)
        s = json.load(urllib.request.urlopen(u2, timeout=60))["result"]
    json.dump({"query": q, "ids": ids, "summary": s}, open(f"{OUT}/pubmed_{k}.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("==", k, len(ids))
    for i in ids:
        r = s[i]
        doi = [a["value"] for a in r.get("articleids", []) if a["idtype"] == "doi"]
        pmc = [a["value"] for a in r.get("articleids", []) if a["idtype"] == "pmc"]
        print(i, r["pubdate"][:4], r["source"][:25], "|", r["title"][:120], "|", doi[:1], pmc[:1])
    time.sleep(0.5)
