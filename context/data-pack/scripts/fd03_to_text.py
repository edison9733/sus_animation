"""fd03_to_text.py - convert everything in raw/fd_rerun/web to plain text (pdftotext -layout for PDFs, tag stripping for HTML).
Run: python -P scripts/fd03_to_text.py"""
import os, re, html, subprocess, glob
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'raw', 'fd_rerun', 'web')
for p in sorted(glob.glob(os.path.join(D, '*'))):
    b, e = os.path.splitext(p)
    if e == '.pdf':
        if open(p, 'rb').read(5) != b'%PDF-': print('not a pdf:', os.path.basename(p)); continue
        subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', p, b + '.txt'], capture_output=True)
    elif e in ('.html', '.htm'):
        raw = open(p, 'rb').read()
        if not raw: continue
        s = raw.decode('utf-8', errors='replace')
        s = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', s)
        s = re.sub(r'(?i)<(br|/p|/div|/h\d|/li|/tr)[^>]*>', '\n', s)
        s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
        s = re.sub(r'[ \t\r\f\v]+', ' ', s); s = re.sub(r'\n\s*\n+', '\n', s)
        open(b + '.txt', 'w', encoding='utf-8').write(s)
print('done')
