"""Economy+sanitation: download report PDFs/HTML listed in scripts/es03_docs.tsv (name<TAB>url) into raw/econ_san/docs/
and convert to text (pdftotext -layout / tag strip). Logs to raw/econ_san/download_log.tsv.
Usage: python scripts/es03_download_docs.py [name ...]   (no args = all not yet downloaded in this call)"""
import os, sys, re, html, subprocess, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', 'raw', 'econ_san'))
DOCS = os.path.join(ROOT, 'docs'); os.makedirs(DOCS, exist_ok=True)
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-download'
want = set(sys.argv[1:])
for line in open(os.path.join(HERE, 'es03_docs.tsv'), encoding='utf-8'):
    if not line.strip(): continue
    name, url = line.rstrip('\n').split('\t')[:2]
    if want and name not in want: continue
    out = os.path.join(DOCS, name)
    r = subprocess.run(['curl', '-sL', '-m', '180', '-A', UA, '-o', out, '-w', '%{http_code}\t%{size_download}\t%{content_type}', url], capture_output=True, text=True)
    with open(os.path.join(ROOT, 'download_log.tsv'), 'a', encoding='utf-8') as f:
        f.write('%s\tdocs/%s\t%s\t%s\n' % (datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), name, url, r.stdout))
    print(name, r.stdout)
    if not r.stdout.startswith('200'): continue
    txt = os.path.splitext(out)[0] + '.txt'
    if open(out, 'rb').read(5) == b'%PDF-':
        subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', out, txt], stderr=subprocess.DEVNULL)
    else:
        t = open(out, encoding='utf-8', errors='replace').read()
        t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', t)
        t = re.sub(r'(?i)</(p|div|tr|h\d|li)>|<br\s*/?>', '\n', t); t = re.sub(r'</t[dh]>', ' | ', t)
        open(txt, 'w', encoding='utf-8').write(re.sub(r'\n\s*\n+', '\n', html.unescape(re.sub(r'<[^>]+>', '', t))))
