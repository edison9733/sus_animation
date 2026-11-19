"""gbv10_fetch.py - download every (name, url) in a manifest TSV to raw/gbv3/web, log status, convert to text.
Usage: python -P scripts/gbv10_fetch.py scripts/gbv10_manifest.tsv   (lines: name<TAB>url ; '#' = comment)
Existing non-empty files are skipped unless --force. Log: raw/gbv3/download_log.tsv"""
import sys, os, re, html, subprocess, time, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'raw', 'gbv3', 'web'); LOG = os.path.join(ROOT, 'raw', 'gbv3', 'download_log.tsv')
force = '--force' in sys.argv
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-download"
def totext(p):
    b, e = os.path.splitext(p)
    head = open(p, 'rb').read(5)
    if head == b'%PDF-':
        subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', p, b + '.txt'], capture_output=True)
    elif e in ('.html', '.htm', '.xml'):
        s = open(p, 'rb').read().decode('utf-8', errors='replace')
        s = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', s)
        s = re.sub(r'(?is)<ref-list.*?</ref-list>', ' ', s)
        s = re.sub(r'(?i)<(br|/p|/div|/h\d|/li|/tr|/title|/td|/th|/sec|/caption)[^>]*>', '\n', s)
        s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
        s = re.sub(r'[ \t\r\f\v]+', ' ', s); s = re.sub(r'\n\s*\n+', '\n', s)
        open(b + '.txt', 'w', encoding='utf-8').write(s)
for line in open(sys.argv[1], encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#'): continue
    name, url = line.split('\t')[:2]
    out = os.path.join(D, name)
    if os.path.exists(out) and os.path.getsize(out) > 0 and not force:
        continue
    r = subprocess.run(['curl', '-sL', '-m', '120', '-A', UA, '-o', out, '-w', '%{http_code}\t%{size_download}\t%{content_type}', url], capture_output=True, text=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write('%s\t%s\t%s\t%s\n' % (datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), name, url, r.stdout))
    print(name, r.stdout)
    if os.path.exists(out) and os.path.getsize(out) > 0: totext(out)
    time.sleep(1)
