"""gbv14_epmc_abstracts.py - print title, journal, year, DOI and abstract of downloaded Europe PMC XMLs.
Run: python -I scripts/gbv14_epmc_abstracts.py raw/gbv3/web/epmc_PMC*.xml"""
import sys, re, html
sys.stdout.reconfigure(encoding="utf-8")
def clean(s): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
for p in sys.argv[1:]:
    x = open(p, encoding="utf-8").read()
    t = re.search(r"<article-title[^>]*>(.*?)</article-title>", x, re.S)
    j = re.search(r"<journal-title>(.*?)</journal-title>", x, re.S)
    y = re.search(r"<pub-date[^>]*>.*?<year>(\d{4})</year>", x, re.S)
    doi = re.search(r'<article-id pub-id-type="doi">(.*?)</article-id>', x)
    au = re.findall(r"<surname>(.*?)</surname>\s*<given-names[^>]*>(.*?)</given-names>", x)[:8]
    a = re.search(r"<abstract[^>]*>(.*?)</abstract>", x, re.S)
    print("=====", p); print(clean(t.group(1)) if t else "", "|", clean(j.group(1)) if j else "", "|", y.group(1) if y else "", "|", doi.group(1) if doi else "")
    print("AU:", "; ".join(f"{s} {g}" for s, g in au)); print(clean(a.group(1)) if a else "NO ABSTRACT"); print()
