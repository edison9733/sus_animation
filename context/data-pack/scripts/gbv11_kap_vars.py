"""gbv11_kap_vars.py - download the public variable pages (frequency tables shown openly in the UNHCR Microdata Library
data dictionary) of the 2017 WASH KAP surveys in 4 Gambella camps and parse them to raw/gbv3/kap/kap_freq.json.
The microdata are 'licensed' (account + request) and are NOT accessed. Needs raw/gbv3/web/kap_ddF1_<sid>.html (gbv10).
Run: python -P scripts/gbv11_kap_vars.py"""
import re, sys, html, json, time, urllib.request, os
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(ROOT, 'raw', 'gbv3', 'web'); out = os.path.join(ROOT, 'raw', 'gbv3', 'kap')
STUDIES = {"149": "Kule", "150": "Pugnido", "159": "Pugnido II", "152": "Tierkidi"}
WANT = ["s2a2", "s2b5b_3", "s2b7", "s2e4", "s2e4a", "s2e5", "s2e5b", "s2e6a", "s2e6b_1", "s2e6b_2", "s2e6b_3",
        "s2e6b_4", "s2e6c", "s2e6c_1", "s2e6c_2", "s2e6c_3", "s2e6c_other"]
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 research-download"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
res = []
for sid, camp in STUDIES.items():
    dd = open(os.path.join(W, f"kap_ddF1_{sid}.html"), encoding="utf-8").read()
    vmap = dict((n, v) for v, n in re.findall(r'variable/F1/(V\d+)\?name=([A-Za-z0-9_]+)"', dd))
    for name in WANT:
        url = f"https://microdata.unhcr.org/index.php/catalog/{sid}/variable/F1/{vmap[name]}?name={name}"
        fn = os.path.join(out, f"var_{sid}_{name}.html")
        if not os.path.exists(fn) or os.path.getsize(fn) == 0:
            for a in range(3):
                try:
                    open(fn, "w", encoding="utf-8").write(get(url)); break
                except Exception as e:
                    print("retry", url, e); time.sleep(5)
            time.sleep(0.7)
        t = open(fn, encoding="utf-8").read()
        txt = html.unescape(re.sub(r"<[^>]+>", "|", re.sub(r"(?s)<script.*?</script>", "", t)))
        txt = re.sub(r"\s+", " ", txt); txt = re.sub(r"(\| ?)+", "|", txt)
        i = txt.find("|Valid|")
        i = i if i >= 0 else txt.find("Categories")
        res.append({"study": sid, "camp": camp, "name": name, "url": url, "text": txt[max(0, i-900):i+1500]})
json.dump(res, open(os.path.join(out, "kap_freq.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in res:
    if r["camp"] == "Kule" or r["name"].startswith("s2e6c"):
        print(r["camp"], r["name"], "::", r["text"][:1500]); print()
