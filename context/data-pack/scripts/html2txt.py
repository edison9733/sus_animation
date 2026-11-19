"""Strip HTML to plain text. usage: python -P scripts/html2txt.py raw/web/x.html [more...] -> writes .txt next to each"""
import sys, re, html
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8', errors='replace').read()
    s = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?i)<(br|/p|/div|/h\d|/li|/tr)[^>]*>', '\n', s)
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    s = re.sub(r'[ \t\r\f\v]+', ' ', s); s = re.sub(r'\n\s*\n+', '\n', s)
    open(re.sub(r'\.html?$', '', p) + '.txt', 'w', encoding='utf-8').write(s)
