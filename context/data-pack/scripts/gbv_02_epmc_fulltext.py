"""Download open-access full text XML (Europe PMC, fallback NCBI efetch db=pmc) and strip to text.
Usage: python gbv_02_epmc_fulltext.py <raw/gbv dir> PMCID [PMCID...]"""
import sys, re, html, time, urllib.request, os
out = sys.argv[1]
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 research-download"})
    return urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
for pmc in sys.argv[2:]:
    x = ""; src = ""
    for src, u in (("europepmc", f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"),
                   ("ncbi", f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc[3:]}&rettype=xml")):
        try:
            x = get(u)
            if "<body" in x: break
        except Exception as e:
            print(pmc, src, "ERR", e)
        time.sleep(1)
    open(os.path.join(out, f"epmc_{pmc}.xml"), "w", encoding="utf-8").write(x)
    t = re.sub(r"(?s)<ref-list.*?</ref-list>", " ", x)
    t = re.sub(r"</(p|title|td|th|tr|sec|caption|label)>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"[ \t]+", " ", t); t = re.sub(r"\n\s*\n+", "\n", t)
    open(os.path.join(out, f"epmc_{pmc}.txt"), "w", encoding="utf-8").write(t)
    print(pmc, src, len(x), "body" if "<body" in x else "NO BODY", u)
    time.sleep(1)
