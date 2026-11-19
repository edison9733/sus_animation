"""Economy+sanitation: Europe PMC searches and open-access full texts -> raw/econ_san/epmc/.
Usage: python scripts/es02_epmc.py search | fulltext PMCID [PMCID...] | abstract PMID [PMID...]"""
import sys, os, re, json, html, urllib.request, urllib.parse, datetime
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw', 'econ_san', 'epmc'))
os.makedirs(ROOT, exist_ok=True)
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest/'
QS = {'latrine_t': '(TITLE:Gambella OR TITLE:Gambela OR ABSTRACT:Gambella OR ABSTRACT:Gambela) AND (latrine OR sanitation OR toilet OR "open defecation" OR diarrhea OR diarrhoea OR cholera OR hygiene)',
      'cholera': '(Gambella OR Gambela) AND (TITLE:cholera OR TITLE:"acute watery")',
      'camps': '(Kule OR Tierkidi OR Nguenyyiel OR Jewi OR Pugnido OR Pinyudo) AND Ethiopia AND refugee AND (latrine OR sanitation OR diarrhea OR diarrhoea OR cholera OR WASH)'}


def get(rel, url):
    try:
        d = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'research-download'}), timeout=120).read(); st = '200'
        open(os.path.join(ROOT, rel), 'wb').write(d)
    except Exception as e:
        d = b''; st = 'ERR:' + str(e)[:60]
    with open(os.path.join(ROOT, '..', 'download_log.tsv'), 'a', encoding='utf-8') as f:
        f.write('%s\tepmc/%s\t%s\t%s\t%d\n' % (datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), rel, url, st, len(d)))
    print(st, len(d), rel)
    return d


def xml2txt(x):
    x = re.sub(r'<(/?)(sec|p|title|tr|table-wrap|caption|abstract|fig)\b[^>]*>', '\n', x)
    x = re.sub(r'</t[dh]>', ' | ', x)
    x = re.sub(r'<[^>]+>', '', x)
    return re.sub(r'\n\s*\n+', '\n', html.unescape(x))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'search':
        for k, q in QS.items():
            get('search_%s.json' % k, BASE + 'search?' + urllib.parse.urlencode({'query': q, 'format': 'json', 'pageSize': 200, 'resultType': 'lite'}))
    elif mode == 'fulltext':
        for pmc in sys.argv[2:]:
            d = get(pmc + '.xml', BASE + pmc + '/fullTextXML')
            if d: open(os.path.join(ROOT, pmc + '.txt'), 'w', encoding='utf-8').write(xml2txt(d.decode('utf-8')))
    elif mode == 'abstract':
        for pmid in sys.argv[2:]:
            get('abs_%s.json' % pmid, BASE + 'search?' + urllib.parse.urlencode({'query': 'EXT_ID:%s AND SRC:MED' % pmid, 'format': 'json', 'resultType': 'core'}))
