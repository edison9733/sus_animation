"""gbv12_lit_abstracts.py - PubMed searches for the named sanitation-violence papers and efetch of abstracts.
Run: python -I scripts/gbv12_lit_abstracts.py <out_dir>   -> <out_dir>/lit_search.json, lit_abstracts.txt"""
import json, sys, time, urllib.parse, urllib.request, os
out = sys.argv[1]
base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
Q = {
 "jadhav2016": 'Jadhav A[au] AND sanitation AND sexual violence',
 "winter_barchi2016": 'Winter SC[au] AND Barchi F[au]',
 "winter_kenya": 'Winter S[au] AND (sanitation OR toilet) AND violence AND Kenya',
 "sommer2015": 'Sommer M[au] AND violence AND (sanitation OR WASH)',
 "kayser": 'Kayser GL[au] AND (sanitation OR water) AND violence',
 "srinivasan": '(sanitation OR toilet* OR latrine*) AND "non-partner sexual violence"',
 "pmids": '41605000[pmid] OR 33665330[pmid] OR 32896218[pmid] OR 31230569[pmid] OR 37507414[pmid] OR 40335140[pmid] OR 38859902[pmid] OR 37488592[pmid] OR 37303715[pmid] OR 30398223[pmid]',
}
res = {}; allids = []
for k, q in Q.items():
    u = base + "esearch.fcgi?db=pubmed&retmode=json&retmax=40&term=" + urllib.parse.quote(q)
    ids = json.load(urllib.request.urlopen(u, timeout=60))["esearchresult"]["idlist"]
    res[k] = {"query": q, "url": u, "ids": ids}
    allids += [i for i in ids if i not in allids]
    print(k, ids); time.sleep(0.6)
json.dump(res, open(os.path.join(out, "lit_search.json"), "w", encoding="utf-8"), indent=1)
txt = ""
for k in range(0, len(allids), 50):
    u = base + "efetch.fcgi?db=pubmed&rettype=abstract&retmode=text&id=" + ",".join(allids[k:k+50])
    txt += urllib.request.urlopen(u, timeout=120).read().decode("utf-8", "replace"); time.sleep(0.6)
open(os.path.join(out, "lit_abstracts.txt"), "w", encoding="utf-8").write(txt)
print(len(allids), "abstracts", len(txt))
