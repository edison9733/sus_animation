"""Fetch PubMed abstracts (text) for given PMIDs or title queries. Saves to raw/gbv/pubmed_abstracts_<tag>.txt"""
import json, sys, time, io
sys.stdout.reconfigure(encoding="utf-8")
import json, sys, time, urllib.parse, urllib.request
out, tag = sys.argv[1], sys.argv[2]
items = sys.argv[3:]
base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
pmids = []
for it in items:
    if it.isdigit():
        pmids.append(it)
    else:
        u = base + "esearch.fcgi?db=pubmed&retmode=json&retmax=3&term=" + urllib.parse.quote(it)
        ids = json.load(urllib.request.urlopen(u, timeout=60))["esearchresult"]["idlist"]
        print("Q:", it, "->", ids)
        pmids += ids
        time.sleep(0.5)
u = base + "efetch.fcgi?db=pubmed&rettype=abstract&retmode=text&id=" + ",".join(pmids)
txt = urllib.request.urlopen(u, timeout=90).read().decode("utf-8")
open(f"{out}/pubmed_abstracts_{tag}.txt", "w", encoding="utf-8").write(txt)
print(txt)
