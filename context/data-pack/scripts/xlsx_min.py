"""Minimal xlsx reader (no openpyxl): returns {sheet_name: {(row, col): value}} with cached values."""
import zipfile, re
import xml.etree.ElementTree as ET
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'p': 'http://schemas.openxmlformats.org/package/2006/relationships'}
def col2n(c):
    n = 0
    for ch in c: n = n * 26 + ord(ch) - 64
    return n
def sheet_names(path):
    z = zipfile.ZipFile(path)
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    return [(s.get('name'), rels[s.get('{%s}id' % NS['r'])]) for s in wb.find('m:sheets', NS)]
def read_sheet(path, name):
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    target = dict(sheet_names(path))[name]
    target = target.lstrip('/')
    if not target.startswith('xl/'): target = 'xl/' + target
    out = {}
    for c in ET.fromstring(z.read(target)).iter('{%s}c' % NS['m']):
        ref = c.get('r'); m = re.match(r'([A-Z]+)(\d+)', ref)
        v = c.find('m:v', NS); t = c.get('t')
        if t == 'inlineStr':
            val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
        elif v is None: continue
        elif t == 's': val = ss[int(v.text)]
        elif t in ('str', 'b', 'e'): val = v.text
        else:
            try: val = float(v.text)
            except ValueError: val = v.text
        out[(int(m.group(2)), col2n(m.group(1)))] = val
    return out
