"""fdcheck01_redownload.py - independent checker (2026-11-16).
Re-downloads every source URL of gambella_flood_drought_events.csv into raw/fd_check/ (own copy, own log),
converts to text with PyMuPDF (PDF) or tag stripping (HTML) - not the builder's pdftotext output - and tests
whether each evidence quote and each numeric field value is present in the re-downloaded text.
Writes raw/fd_check/check_results.tsv. Downloaded files are data only.
Run: python scripts/fdcheck01_redownload.py"""
import os, re, sys, html, json, subprocess, datetime, hashlib, time
import pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get('FDCHECK_OUT') or os.path.join(ROOT, 'raw', 'fd_check'); os.makedirs(OUT, exist_ok=True)
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-download'
LOG = os.path.join(OUT, 'download_log.tsv')
def norm(s):
    s = s.replace('\u00a0', ' ').replace('\u00ad', '')
    for a, b in (('\u2019', "'"), ('\u2018', "'"), ('\u201c', '"'), ('\u201d', '"'), ('\u2013', '-'), ('\u2014', '-'), ('\ufb01', 'fi'), ('\ufb02', 'fl')):
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip().lower()
def fetch(url):
    name = hashlib.md5(url.encode()).hexdigest()[:12]
    out = os.path.join(OUT, name + '.bin')
    if not (os.path.exists(out) and os.path.getsize(out) > 0):
        r = subprocess.run(['curl', '-sLg', '-m', '150', '-A', UA, '-o', out, '-w', '%{http_code}\t%{size_download}\t%{content_type}', url], capture_output=True, text=True)
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write('%s\t%s\t%s\t%s\n' % (datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), name + '.bin', url, r.stdout))
        time.sleep(0.5)
    st = ''
    for l in open(LOG, encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        if p[1] == name + '.bin': st = p[3]
    return out, st
def to_text(p):
    raw = open(p, 'rb').read()
    if raw[:5] == b'%PDF-':
        import pymupdf
        return '\n'.join(pg.get_text() for pg in pymupdf.open(p))
    s = raw.decode('utf-8', errors='replace')
    if s.lstrip()[:1] in '{[':
        return s.encode().decode('unicode_escape', errors='replace') if False else json.dumps(json.loads(s), ensure_ascii=False)
    s = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', s)
    return html.unescape(re.sub(r'<[^>]+>', ' ', s))
d = pd.read_csv(os.path.join(ROOT, 'data', 'gambella_flood_drought_events.csv'), dtype=str, keep_default_na=False, encoding='utf-8-sig')
res = []
for i, r in d.iterrows():
    if r.event_id.startswith('GAP') or not r.url: continue
    p, st = fetch(r.url)
    try: t = norm(to_text(p)) if os.path.getsize(p) else ''
    except Exception as e: t = ''; st += ' ERR ' + str(e)[:60]
    tnos = t.replace(' ', '')
    qs = [q for q in r.evidence_quote.split(' || ') if q.strip()]
    qok = [norm(q).replace(' ', '') in tnos for q in qs]
    nums = {}
    for c in ('people_affected', 'people_displaced', 'deaths'):
        for n in re.findall(r'\d+', r[c]):
            v = int(n)
            forms = {str(v), format(v, ','), format(v, ',').replace(',', ' '), format(v, ',').replace(',', '.')}
            nums[c + '=' + n] = any(f in t for f in forms)
    res.append(dict(row=i, event_id=r.event_id, http=st.split('\t')[0], bytes=(st.split('\t') + ['', ''])[1], textlen=len(t), n_quotes=len(qs), quotes_found=sum(qok),
                    missing_quotes=' || '.join(q[:80] for q, k in zip(qs, qok) if not k), nums=';'.join('%s:%s' % (k, 'ok' if v else 'MISSING') for k, v in nums.items()), url=r.url))
pd.DataFrame(res).to_csv(os.path.join(OUT, 'check_results.tsv'), sep='\t', index=False, encoding='utf-8')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 70); pd.set_option('display.max_rows', 200)
print(pd.DataFrame(res).drop(columns=['url']).to_string())
