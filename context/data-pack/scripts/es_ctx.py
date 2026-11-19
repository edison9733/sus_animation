"""Print context around regex hits in a text file. Usage: python es_ctx.py file regex [width] [max]"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
f, pat = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 250
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 15
t = open(f, encoding='utf-8', errors='replace').read()
print('=====', f, len(t)); last = -1; n = 0
for m in re.finditer(pat, t):
    if m.start() < last: continue
    s = max(0, m.start() - w); e = m.end() + w; last = e
    print('@%d ...' % m.start(), t[s:e].replace('\n', ' / ')); print(); n += 1
    if n >= mx: break
