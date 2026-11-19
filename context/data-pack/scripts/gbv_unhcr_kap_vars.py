"""Download public variable pages (summary statistics shown openly in the UNHCR Microdata Library data dictionary)
for the 2017 WASH KAP surveys in Gambella camps and parse the frequency tables.
The microdata themselves are 'licensed' (account + request) and were NOT accessed.
Usage: python gbv_unhcr_kap_vars.py <raw/gbv/kap dir>"""
import re, sys, html, json, time, urllib.request, os
sys.stdout.reconfigure(encoding="utf-8")
out = sys.argv[1]
STUDIES = {"149": "Kule", "150": "Pugnido", "159": "Pugnido II", "152": "Tierkidi"}
WANT = ["s2a2", "s2b5b_3", "s2b7", "s2b4b", "s2e4", "s2e4a", "s2e5b", "s2e6a", "s2e6b_1", "s2e6b_2", "s2e6b_3",
        "s2e6b_4", "s2e6c", "s2e6c_1", "s2e6c_2", "s2e6c_3", "s2e6c_other", "s2e5", "s2e7", "s2e8", "s2e4b"]
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
res = []
for sid, camp in STUDIES.items():
    dd = open(os.path.join(out, f"dd_{sid}.html"), encoding="utf-8").read()
    vmap = dict((n, v) for v, n in re.findall(r'variable/F1/(V\d+)\?name=([A-Za-z0-9_]+)"', dd))
    for name in WANT:
        if name not in vmap:
            res.append({"study": sid, "camp": camp, "name": name, "error": "not in dictionary"}); continue
        url = f"https://microdata.unhcr.org/index.php/catalog/{sid}/variable/F1/{vmap[name]}?name={name}"
        fn = os.path.join(out, f"var_{sid}_{name}.html")
        if not os.path.exists(fn):
            open(fn, "w", encoding="utf-8").write(get(url)); time.sleep(0.7)
        t = open(fn, encoding="utf-8").read()
        txt = html.unescape(re.sub(r"<[^>]+>", "|", re.sub(r"<script.*?</script>", "", t, flags=re.S)))
        txt = re.sub(r"\s+", " ", txt); txt = re.sub(r"(\| ?)+", "|", txt)
        i = txt.find("Variable: ") if "Variable: " in txt else txt.find(name)
        res.append({"study": sid, "camp": camp, "name": name, "url": url, "text": txt[i:i+1800]})
json.dump(res, open(os.path.join(out, "kap_variable_pages.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in res:
    print(r["camp"], r["name"], "::", r.get("text", r.get("error"))[:700]); print()
