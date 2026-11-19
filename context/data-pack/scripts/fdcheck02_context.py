"""fdcheck02_context.py - prints the text around given keywords in the checker's own re-downloaded copy of a source row.
Usage: python scripts/fdcheck02_context.py <row> <width> <kw1> [kw2 ...]   (reading aid, checker 2026-11-16)"""
import sys, os, re, hashlib, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
sys.argv_saved = sys.argv
spec = importlib.util.spec_from_file_location('c1', os.path.join(ROOT, 'scripts', 'fdcheck01_redownload.py'))
src = open(os.path.join(ROOT, 'scripts', 'fdcheck01_redownload.py'), encoding='utf-8').read().split("d = pd.read_csv")[0]
ns = {'__file__': os.path.join(ROOT, 'scripts', 'fdcheck01_redownload.py')}; exec(src, ns)
d = pd.read_csv(os.path.join(ROOT, 'data', 'gambella_flood_drought_events.csv'), dtype=str, keep_default_na=False, encoding='utf-8-sig')
row, w = int(sys.argv[1]), int(sys.argv[2])
p = os.path.join(os.environ.get('FDCHECK_OUT') or os.path.join(ROOT, 'raw', 'fd_check'), hashlib.md5(d.url[row].encode()).hexdigest()[:12] + '.bin')
t = re.sub(r'\s+', ' ', ns['to_text'](p))
sys.stdout.reconfigure(encoding='utf-8')
for k in sys.argv[3:]:
    ms = list(re.finditer(re.escape(k), t, flags=re.I))
    print('== row %d  %r: %d hits' % (row, k, len(ms)))
    for m in ms[:3]:
        print('   ...' + t[max(0, m.start() - w):m.end() + w] + '...')
