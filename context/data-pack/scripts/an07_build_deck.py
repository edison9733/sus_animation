"""FloodSafe Sanitation Gambella — pitch deck (.pptx) following the 8-part template.
Usage: python an07_build_deck.py <gambella root>   (run an06_deck_data.py first)
Numbers come from proposal/deck_data.json (read from data/*.csv). Plans, designs and the priority index are the
team's proposal / own analysis; budget, partners, dates and targets stay as placeholders."""
import sys, json
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION

R = sys.argv[1].rstrip('/') + '/'; P = R + 'proposal/'
D = json.load(open(P + 'deck_data.json', encoding='utf-8'))
M = R + 'maps/'

NAVY, DEEP, COB, AZ, SKY, ICE = (RGBColor(0x0A, 0x1F, 0x4D), RGBColor(0x12, 0x3A, 0x82), RGBColor(0x1E, 0x5B, 0xB8),
                                 RGBColor(0x3D, 0x8F, 0xE0), RGBColor(0x8C, 0xC3, 0xFF), RGBColor(0xE3, 0xF0, 0xFF))
INK, MUTED, LINE, WHITE, WARN = RGBColor(0x16, 0x20, 0x2C), RGBColor(0x5A, 0x66, 0x75), RGBColor(0xD6, 0xE2, 0xF0), RGBColor(255, 255, 255), RGBColor(0xB5, 0x65, 0x1D)
SAND, BROWN = RGBColor(0xB2, 0x8A, 0x49), RGBColor(0x6D, 0x51, 0x48)
HEAD, BODY = 'Bahnschrift', 'Calibri'
f = lambda n: f'{n:,.0f}'

prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = 13.333, 7.5

def tb(s, x, y, w, h, paras, size=14, color=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, margin=0.0, space=4, name=None):
    """paras: str | list of str | list of (text|[runs], opts). runs: (text, {bold,color,size,italic})."""
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name: box.name = name
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    for side in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'): setattr(tf, side, Inches(margin))
    if isinstance(paras, str): paras = [paras]
    for i, p in enumerate(paras):
        opts = {}
        if isinstance(p, tuple): p, opts = p
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = opts.get('align', align); para.space_after = Pt(opts.get('space', space))
        if opts.get('bullet'):
            pPr = para._p.get_or_add_pPr(); pPr.set('marL', str(Emu(Inches(0.22)))); pPr.set('indent', str(-Emu(Inches(0.22))))
            from pptx.oxml.ns import qn
            for tag in ('a:buNone', 'a:buChar', 'a:buAutoNum'):
                for el in pPr.findall(qn(tag)): pPr.remove(el)
            bc = pPr.makeelement(qn('a:buClr'), {}); sc = bc.makeelement(qn('a:srgbClr'), {'val': str(opts.get('bcolor', COB))}); bc.append(sc); pPr.append(bc)
            bu = pPr.makeelement(qn('a:buChar'), {'char': '•'}); pPr.append(bu)
        runs = p if isinstance(p, list) else [(p, {})]
        for t, ro in runs:
            r = para.add_run(); r.text = t
            fo = r.font; fo.name = ro.get('font', opts.get('font', font)); fo.size = Pt(ro.get('size', opts.get('size', size)))
            fo.bold = ro.get('bold', opts.get('bold', bold)); fo.italic = ro.get('italic', False)
            fo.color.rgb = ro.get('color', opts.get('color', color))
    return box

def rect(s, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08, name=None, shadow=False):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if name: sh.name = name
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb = line; sh.line.width = Pt(1)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: sh.adjustments[0] = radius
    if not shadow:
        from pptx.oxml.ns import qn
        spPr = sh._element.spPr; ef = spPr.makeelement(qn('a:effectLst'), {}); spPr.append(ef)
    return sh

def badge(s, label):
    c = rect(s, 0.55, 0.42, 0.72, 0.72, COB, shape=MSO_SHAPE.OVAL, name='Section badge')
    c.line.color.rgb = SKY; c.line.width = Pt(2.5)
    tf = c.text_frame; tf.margin_left = tf.margin_right = 0; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = str(label); r.font.name = HEAD; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = WHITE
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

SECTION = {'n': 0, 'name': ''}
def content(title, sub=None, src=None, notes=None):
    s = prs.slides.add_slide(BLANK)
    s.shapes.add_picture(P + 'deck_img/corner.png', Inches(SW - 1.9), Inches(0), Inches(1.9), Inches(1.9)).name = 'Corner arcs'
    badge(s, SECTION['n'])
    tb(s, 1.48, 0.38, 10.0, 0.6, title, size=28, color=NAVY, font=HEAD, bold=True, name='Title')
    tb(s, 1.48, 0.98, 10.0, 0.4, (SECTION['name'].upper() + ('  ·  ' + sub if sub else '')), size=12, color=COB, font=HEAD, name='Kicker')
    if src: tb(s, 0.6, 7.0, 10.6, 0.3, 'Source: ' + src, size=10, color=MUTED, name='Source')
    tb(s, 11.6, 7.0, 1.15, 0.3, str(len(prs.slides._sldIdLst)), size=10, color=COB, font=HEAD, bold=True, align=PP_ALIGN.RIGHT, name='Slide number')
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

def divider(n, title, line):
    SECTION['n'] = n; SECTION['name'] = title
    s = prs.slides.add_slide(BLANK)
    s.shapes.add_picture(P + 'deck_img/bg_section.png', 0, 0, prs.slide_width, prs.slide_height).name = 'Background'
    c = rect(s, 0.9, 2.35, 1.3, 1.3, WHITE, shape=MSO_SHAPE.OVAL, name='Section number')
    tf = c.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    r = p.add_run(); r.text = str(n); r.font.name = HEAD; r.font.size = Pt(40); r.font.bold = True; r.font.color.rgb = NAVY
    tb(s, 2.5, 2.3, 8.5, 1.0, title.upper(), size=40, color=WHITE, font=HEAD, bold=True, anchor=MSO_ANCHOR.MIDDLE, name='Title')
    tb(s, 2.5, 3.35, 7.5, 1.0, line, size=18, color=SKY, name='Subtitle')
    return s

def stat(s, x, y, w, h, big, label, col=COB, fill=ICE, bigsize=34):
    rect(s, x, y, w, h, fill, name='Stat card')
    tb(s, x + 0.2, y + 0.12, w - 0.4, 0.75, big, size=bigsize, color=col, font=HEAD, bold=True)
    tb(s, x + 0.2, y + 0.12 + bigsize / 72 * 1.25, w - 0.4, h - 0.2 - bigsize / 72 * 1.25, label, size=13, color=INK)

def bullets(s, x, y, w, h, items, size=15, name='Body'):
    return tb(s, x, y, w, h, [(it, {'bullet': True, 'space': 7}) for it in items], size=size, name=name)

def table(s, x, y, w, rows, head, colw=None, size=12, rowh=0.36, num=()):
    shp = s.shapes.add_table(len(rows) + 1, len(head), Inches(x), Inches(y), Inches(w), Inches(rowh * (len(rows) + 1)))
    shp.name = 'Table'; t = shp.table
    tblPr = t._tbl.tblPr; tblPr.set('bandRow', '0'); tblPr.set('firstRow', '1')
    if colw:
        for i, cw in enumerate(colw): t.columns[i].width = Inches(cw)
    for i in range(len(rows) + 1): t.rows[i].height = Inches(rowh)
    for j, hd in enumerate(head):
        c = t.cell(0, j); c.fill.solid(); c.fill.fore_color.rgb = NAVY
        c.text = ''; p = c.text_frame.paragraphs[0]; r = p.add_run(); r.text = hd
        r.font.name = HEAD; r.font.size = Pt(size - 1); r.font.bold = True; r.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.RIGHT if j in num else PP_ALIGN.LEFT
        c.margin_left = c.margin_right = Inches(0.08); c.margin_top = c.margin_bottom = Inches(0.03); c.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, row in enumerate(rows, 1):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = ICE if i % 2 == 0 else WHITE
            c.text = ''; p = c.text_frame.paragraphs[0]; r = p.add_run(); r.text = str(val)
            r.font.name = BODY; r.font.size = Pt(size); r.font.color.rgb = INK
            if isinstance(val, str) and val.startswith('['): r.font.italic = True; r.font.color.rgb = COB
            p.alignment = PP_ALIGN.RIGHT if j in num else PP_ALIGN.LEFT
            c.margin_left = c.margin_right = Inches(0.08); c.margin_top = c.margin_bottom = Inches(0.03); c.vertical_anchor = MSO_ANCHOR.MIDDLE
    return shp

def style_chart(ch, title=None, legend=False, size=12):
    ch.font.name = BODY; ch.font.size = Pt(size); ch.font.color.rgb = MUTED
    ch.has_title = bool(title)
    if title:
        ch.chart_title.text_frame.text = title
        tp = ch.chart_title.text_frame.paragraphs[0]; tp.runs[0].font.size = Pt(13); tp.runs[0].font.bold = True; tp.runs[0].font.color.rgb = NAVY; tp.runs[0].font.name = HEAD
    ch.has_legend = legend
    if legend: ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.size = Pt(12)
    try:
        va = ch.value_axis; va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = LINE; va.format.line.fill.background()
        va.tick_labels.font.size = Pt(size); ch.category_axis.tick_labels.font.size = Pt(size); ch.category_axis.format.line.color.rgb = LINE
    except Exception: pass

def picture(s, path, x, y, w=None, h=None, name='Map'):
    p = s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None); p.name = name
    ln = p.line; ln.color.rgb = LINE; ln.width = Pt(0.75); return p

def card(s, x, y, w, h, head, text, fill=ICE, hc=DEEP, tc=INK, size=14):
    rect(s, x, y, w, h, fill, name='Card')
    tb(s, x + 0.22, y + 0.16, w - 0.44, 0.4, head, size=15, color=hc, font=HEAD, bold=True)
    tb(s, x + 0.22, y + 0.6, w - 0.44, h - 0.7, text, size=size, color=tc)

# =============================== 0. Title
s = prs.slides.add_slide(BLANK)
s.shapes.add_picture(P + 'deck_img/bg_title.png', 0, 0, prs.slide_width, prs.slide_height).name = 'Background'
pill = rect(s, 0.8, 0.85, 3.3, 0.42, NAVY, radius=0.5, name='Kicker pill')
tb(s, 0.8, 0.85, 3.3, 0.42, 'PROJECT PROPOSAL  ·  DRAFT', size=12, color=WHITE, font=HEAD, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
tb(s, 0.8, 1.55, 8, 2.6, [('FLOODSAFE', {'color': NAVY}), ('SANITATION', {'color': AZ}), ('GAMBELLA', {'color': NAVY})], size=54, font=HEAD, bold=True, space=0, name='Title')
tb(s, 0.8, 4.35, 5.6, 0.9, 'Flood- and drought-safe toilets for the people of the Gambela flood plain, western Ethiopia', size=18, color=DEEP, name='Subtitle')
tb(s, 0.8, 5.45, 6.4, 0.6, [[('Submitted by ', {}), ('[Organisation name]', {'italic': True, 'color': COB}), (' · November 2026 · draft for discussion', {})]], size=13, color=MUTED)
s.notes_slide.notes_text_frame.text = ('Draft proposal built from an open-data pack (gambella/data). Every number traces to a named source; '
                                       'items in [brackets] are deliberately left open because no data exist yet.')

# =============================== agenda
SECTION['n'] = '·'; SECTION['name'] = 'Contents'
s = content('What this proposal covers')
items = ['Executive summary', 'Problem statement', 'Proposed idea', 'Innovation & design', 'Implementation plan', 'Impact', 'Scalability plan', 'Supporting materials']
for i, it in enumerate(items):
    col, row = i % 2, i // 2
    x, y = 0.9 + col * 6.0, 1.85 + row * 1.15
    c = rect(s, x, y, 0.75, 0.75, [NAVY, DEEP, COB, AZ][row], shape=MSO_SHAPE.OVAL, name='Number')
    tf = c.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    r = p.add_run(); r.text = str(i + 1); r.font.name = HEAD; r.font.size = Pt(22); r.font.bold = True; r.font.color.rgb = WHITE
    tb(s, x + 1.0, y + 0.1, 4.7, 0.6, it, size=22, color=NAVY, font=HEAD, bold=True, anchor=MSO_ANCHOR.MIDDLE)
tb(s, 0.9, 6.45, 11.5, 0.4, [[('How to read: ', {'bold': True, 'color': DEEP}), ('numbers come from named datasets; "own analysis" = the team\'s calculations; "team proposal" = planned activities; [brackets] = still open.', {})]], size=13, color=MUTED)

# =============================== 1. Executive summary
divider(1, 'Executive summary', 'Why, where, what and how — on one page')
s = content('Toilets that survive the flood', 'The case in brief', src='DHS 2024; JRC flood maps + WorldPop 2020 (own analysis); UNHCR Oct 2026; OCHA/GDACS 2022',
            notes='Gambela lies on the flat Baro–Akobo flood plain. Sanitation progress stalled after 2016. Our proposal: toilet designs matched to the ground (zones A–D), built and repaired by local masons, with safety features for women and girls. First phase: Jikawo, Wantawo, Lare plus one camp.')
stat(s, 0.6, 1.65, 2.9, 1.65, f"{D['od24']:.0f}%", 'practise open defecation (DHS 2024) — no progress since 2016')
stat(s, 3.7, 1.65, 2.9, 1.65, f"{D['flood10']}%", 'of residents live where a 100-year river flood reaches')
stat(s, 6.8, 1.65, 2.9, 1.65, '185,200', 'people displaced by the 2022 flood')
stat(s, 9.9, 1.65, 2.85, 1.65, f"{D['refugees']/1000:,.0f}k", 'registered refugees in Gambella, many in flood-prone camps')
cards = [('The problem', f"Pit latrines flood, collapse in swelling clay and are never emptied (97.2%). People return to the bush, where women and girls face violence."),
         ('The idea', f"Four toilet designs matched to flood and soil: raised/sealed units for {D['zA']/1000:,.0f}k people in frequent-flood areas, lined pits elsewhere, safety built in."),
         ('First step', 'Validate on site and cost a pilot in Jikawo, Wantawo and Lare plus one refugee camp, before any roll-out. Estimated pilot cost about USD 540k for 500 households (to be confirmed by costing).')]
for i, (h, t) in enumerate(cards):
    card(s, 0.6 + i * 4.1, 3.55, 3.85, 2.75, h, t, fill=WHITE if i != 1 else ICE, size=15)
    if i != 1: s.shapes[-3].line.color.rgb = LINE

# =============================== 2. Problem statement
divider(2, 'Problem statement', 'Floods, swelling clay, stalled sanitation and unsafe nights')
s = content('Most people live on a plain that floods', 'Terrain, flood and drought (own analysis of 1,002 grid cells)',
            src='Copernicus DEM, WorldPop 2020, CHIRPS 1981–2025, CHC SPEI-12, JRC flood hazard maps; 0.05° grid',
            notes='Grid of 1,002 cells (about 5.5 km). Spearman correlations; grid p-values use 0.25° blocks because neighbouring cells are not independent.')
picture(s, M + 'gambella_heatmap_panel.png', 0.6, 1.5, h=5.4)
bullets(s, 5.55, 1.6, 7.2, 5.3, [
    f"{D['band45']}% of residents live between 400 and 500 m on the Baro–Akobo flood plain.",
    f"{D['flood10']}% live where a 100-year river flood covers at least a tenth of their area; {D['flood50']}% where it covers half or more.",
    f"Lower ground floods: elevation vs flood extent ρ = {D['r_elev_flood']} (cells), {D['r_elev_flood_b']} (blocks).",
    f"Drought here means a long dry season: about five months under 30 mm a year on the plain (elevation vs dry months ρ = {D['r_elev_dry']}). Years with rain under 80% of normal are rare and fall in the thinly populated south.",
    f"Rain is rising (year vs rain ρ = {D['r_year_rain']}); wetter years bring recorded floods (ρ = {D['r_rain_flood']}).",
    f"Elevation vs population is only weakly negative (ρ = {D['r_elev_pop']}): the eastern highlands of Godere and Mengesh are dense too."], size=15)

s = content('Floods displace tens of thousands almost every year', 'Documented events, Gambella 1961–2025',
            src='UN agencies, Red Cross/IFRC, GDACS, Dartmouth Flood Observatory, peer-reviewed histories, news; EM-DAT via OWID (national)',
            notes='Largest displaced figure per event among sources that passed checking; definitions differ between sources. 2024 has two entries that may be one season. 1998 rests on a map match only.')
cd = CategoryChartData(); cd.categories = [str(y) for y in D['fl_years']]; cd.add_series('People displaced', D['fl_dis'])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.55), Inches(7.6), Inches(5.3), cd); gf.name = 'Displaced chart'
ch = gf.chart; style_chart(ch, 'People displaced by floods in Gambella, by year')
pl = ch.plots[0]; pl.gap_width = 60; pl.series[0].format.fill.solid(); pl.series[0].format.fill.fore_color.rgb = COB
pl.has_data_labels = True; dl = pl.data_labels; dl.number_format = '#,##0'; dl.number_format_is_linked = False; dl.position = XL_LABEL_POSITION.OUTSIDE_END; dl.font.size = Pt(11); dl.font.color.rgb = INK
pt = pl.series[0].points[D['fl_years'].index(2022)]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = NAVY
ch.value_axis.tick_labels.number_format = '#,##0'; ch.value_axis.tick_labels.number_format_is_linked = False
stat(s, 8.6, 1.6, 4.15, 1.45, f"{D['n_events']}", f"flood and drought events documented, 1961–2025 ({D['n_flood']} floods)", bigsize=30)
stat(s, 8.6, 3.2, 4.15, 1.45, '72%', 'of cropland damaged in 2022; 250–270 water schemes out of use', bigsize=30)
tb(s, 8.6, 4.85, 4.15, 2.0, [('2014: latrines in Leitchuor refugee camp overflowed and some collapsed.', {'bullet': True, 'space': 6}),
                            ('No Gambella drought impact figure found after 2002.', {'bullet': True, 'space': 6}),
                            ('A year without a record is not a year without a flood.', {'bullet': True})], size=14)

s = content('Sanitation progress stopped in 2016', 'Toilet coverage and use', src='DHS Program API (Ethiopia DHS 2000–2024); peer-reviewed study, Gambella town 2023; WHO/regional reports (cholera 2025)',
            notes='Improved sanitation jumped in 2024 (42%) while open defecation did not fall: more households upgraded existing latrines rather than new households gaining one.')
cd = CategoryChartData(); cd.categories = [str(y) for y in D['san_years']]
cd.add_series('Open defecation, % of people', D['san_od']); cd.add_series('Improved sanitation, % of people', D['san_imp'])
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(0.6), Inches(1.55), Inches(7.4), Inches(5.3), cd); gf.name = 'Sanitation chart'
ch = gf.chart; style_chart(ch, 'Gambela, DHS survey years', legend=True)
for ser, col in zip(ch.plots[0].series, (WARN, COB)):
    ser.format.line.color.rgb = col; ser.format.line.width = Pt(3); ser.smooth = False
    ser.marker.format.fill.solid(); ser.marker.format.fill.fore_color.rgb = col; ser.marker.format.line.color.rgb = col; ser.marker.size = 8
ch.plots[0].has_data_labels = True; dl = ch.plots[0].data_labels; dl.number_format = '0'; dl.number_format_is_linked = False; dl.position = XL_LABEL_POSITION.ABOVE; dl.font.size = Pt(11)
stat(s, 8.4, 1.6, 2.1, 1.6, '97.2%', 'on-site toilets never emptied', bigsize=28)
stat(s, 10.65, 1.6, 2.1, 1.6, '47.2%', 'of latrine owners (town) still go outside', bigsize=28)
stat(s, 8.4, 3.35, 2.1, 1.6, '2,194', 'cholera cases, Jan–May 2025', bigsize=28)
stat(s, 10.65, 3.35, 2.1, 1.6, '6–64', 'people per latrine in camps', bigsize=28)
tb(s, 8.4, 5.2, 4.35, 1.7, f"In 2019 Gambela had the 4th-highest open defecation of Ethiopia's 11 regions, despite middling income.", size=14)

s = content('Women and girls are unsafe without a safe toilet', 'Violence, privacy and night-time use',
            src='DHS 2024 (women 15–49); peer-reviewed studies 2021–2023; UNHCR WASH KAP 2017; HVACS 2024',
            notes='Figures use different definitions and recall periods; DHS undercounts violence; local studies sample high-risk groups. Pugnido II: 71% safe and 13% unsafe, remaining 16% unexplained.')
table(s, 0.6, 1.6, 7.6, [
    ['Partner violence (physical/sexual), past 12 months', f"{D['ipv24_g']}%", f"{D['ipv24_e']}%"],
    ['Sexual violence, past 12 months', f"{D['sv24_g']}%", f"{D['sv24_e']}%"],
    ['Never sought help or told anyone', f"{D['ntl24_g']}%", f"{D['ntl24_e']}%"],
    ['Sexual violence (study definition), Okugo camp 2023', '34.9%', '–'],
    ['Sexual partner violence, Pugnido camp 2021', '35.5%', '–'],
    ['Partner violence, lifetime, Gambella town 2021', '58.8%', '–'],
    ['Latrines with no privacy (Kule / Pugnido) 2017', '27% / 69%', '–'],
    ['Feel unsafe using latrine (Pugnido II) 2017', '13%', '–'],
    ['Adults in the bush at night (4 camps) 2017', '7–12%', '–']], ['Measure', 'Gambela', 'Ethiopia'], colw=[5.0, 1.3, 1.3], size=12, rowh=0.47, num=(1, 2))
card(s, 8.55, 1.6, 4.2, 2.45, '43% in the evening', 'of recent sexual violence in Ethiopia\'s refugee camps happened in the evening (HVACS 2024) — when people walk to latrines or the bush.', size=14)
card(s, 8.55, 4.25, 4.2, 2.55, 'Toilet type matters elsewhere', 'Open-air or shared toilets raise the odds of non-partner sexual violence: India OR 2.1–2.5; South Africa 1.45; 31 countries 1.16–1.40. Not yet measured in Gambella.', size=14)

s = content('Money alone will not fix it', 'Economy and ability to pay', src='World Bank WDI (national); Global Data Lab (modelled); NPC 2017; DHS 2024; own analysis across 11 regions × 6 DHS rounds',
            notes='No official regional GDP exists for Gambela. Within a region, income growth does not predict sanitation gains (ρ ≈ 0), while HDI gains do go with falling open defecation.')
cd = CategoryChartData(); yrs = D['gdp_years']; cd.categories = [str(y) for y in yrs]; cd.add_series('GDP per capita, current US$', D['gdp'])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.55), Inches(6.6), Inches(5.3), cd); gf.name = 'GDP chart'
ch = gf.chart; style_chart(ch, 'Ethiopia GDP per capita, current US$ (World Bank)')
ch.plots[0].gap_width = 40; ch.plots[0].series[0].format.fill.solid(); ch.plots[0].series[0].format.fill.fore_color.rgb = AZ
ch.value_axis.tick_labels.number_format = '#,##0'; ch.value_axis.tick_labels.number_format_is_linked = False
ch.category_axis.tick_labels.font.size = Pt(10)
stat(s, 7.55, 1.6, 2.5, 1.55, f"{D['gni00']:,.0f}→{D['gni23']:,.0f}", 'Gambela GNI per capita, 2017 PPP $ (modelled), 2000→2023', bigsize=24)
stat(s, 10.25, 1.6, 2.5, 1.55, '50%→23%', 'regional poverty headcount, 1999/00→2015/16', bigsize=24)
bullets(s, 7.55, 3.4, 5.2, 3.4, [
    f"Across regions, richer means better toilets (ρ = {D['r_imp_gni']}).",
    f"But within a region, income growth does not predict sanitation gains (ρ = {D['r_imp_gni_fd']:.2f}). Gambela's income rose while open defecation stood still.",
    f"{D['lowq24']:.0f}% of Gambela's people are in Ethiopia's poorest wealth quintile — most cannot pay a raised toilet up front.",
    'No official regional GDP exists; regional income is modelled.'], size=14)

# =============================== 3. Proposed idea
divider(3, 'Proposed idea', 'A toilet matched to the ground it stands on')
s = content('FloodSafe Sanitation Gambella', 'The idea in one slide  ·  team proposal',
            notes='The idea builds on the FloodSafe Sanitation draft: do not rely on one standard latrine; check each site, pick the design, train local masons, add warning and safety features.')
steps = [('Check the site', 'Flood marks, soil, wells, ownership, nearest high ground'), ('Pick the design', 'Zone A, B, C or D from flood and soil data'),
         ('Build locally', 'Trained masons build, earn and repair'), ('Keep it safe', 'Lock, light, privacy, women\'s units, near home'),
         ('Stay ready', 'Flood gauge, colour pegs, emergency pack, swap point')]
for i, (h, t) in enumerate(steps):
    x = 0.6 + i * 2.5
    c = rect(s, x, 1.75, 2.3, 2.55, [NAVY, DEEP, COB, AZ, SKY][i], name='Step')
    tb(s, x + 0.2, 1.9, 1.9, 0.6, f'0{i+1}', size=28, color=WHITE if i < 4 else NAVY, font=HEAD, bold=True)
    tb(s, x + 0.2, 2.55, 1.95, 0.5, h, size=17, color=WHITE if i < 4 else NAVY, font=HEAD, bold=True)
    tb(s, x + 0.2, 3.1, 1.95, 1.15, t, size=13, color=WHITE if i < 4 else NAVY)
card(s, 0.6, 4.6, 6.0, 2.25, 'Who it is for', f"{D['hp']:,} residents in high-priority areas; first phase in Jikawo, Wantawo and Lare plus one refugee camp. {D['refugees']:,} refugees region-wide are a separate priority group.", size=14)
card(s, 6.85, 4.6, 5.9, 2.25, 'What is different', 'Not one standard latrine: the design follows measured flood and soil conditions, safety is built in, and repair stays local after the project ends.', size=14)

s = content('Where to start: the western flood plain', 'Priority = people × (flood 50% + swelling clay 25% + dry season 25%)  ·  own analysis',
            src='Own index from JRC flood maps, SoilGrids 2.0, CHIRPS and WorldPop 2020; camps from UNHCR', notes=f"Cells with fewer than 2 people per km² excluded. Under four different weightings, {D['rob_cells']} cells ({D['rob_pop']:,} people) stay in the top 20%. WorldPop misses camp refugees, so camps rank too low and are treated separately.")
picture(s, M + 'sanitation_priority.png', 0.6, 1.55, w=7.9)
W = sorted(D['woredas'], key=lambda r: -r['hp'])[:6][::-1]
cd = CategoryChartData(); cd.categories = [w['w'].replace('Gambella Wild Life Reserve', 'Wildlife Reserve') for w in W]; cd.add_series('People in high-priority cells', [w['hp'] for w in W])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(8.75), Inches(1.5), Inches(4.0), Inches(4.3), cd); gf.name = 'Woreda chart'
ch = gf.chart; style_chart(ch, 'High-priority residents by woreda', size=11)
ch.plots[0].gap_width = 45; ch.plots[0].series[0].format.fill.solid(); ch.plots[0].series[0].format.fill.fore_color.rgb = COB
ch.plots[0].has_data_labels = True; dl = ch.plots[0].data_labels; dl.number_format = '#,##0'; dl.number_format_is_linked = False; dl.font.size = Pt(10); dl.position = XL_LABEL_POSITION.OUTSIDE_END
ch.value_axis.visible = False; ch.value_axis.has_major_gridlines = False
tb(s, 8.75, 5.95, 4.0, 0.95, f"{D['hp']/1000:,.0f}k people in high-priority cells; {D['rob_cells']} cells stay top-20% under every weighting tested.", size=13, color=DEEP)

# =============================== 4. Innovation & design
divider(4, 'Innovation & design', 'Four designs, safety built in, repair kept local')
s = content('Four toilet designs for four kinds of ground', 'Zone rules from flood and slope data  ·  team proposal',
            src='Zones: own rules on JRC 10-/100-year flood extent and Copernicus slope; people = WorldPop 2020',
            notes='Zone A: 10-year flood ≥30% or 100-year ≥50% of the cell. B: 100-year flood 10–50%. C: little river flooding, clay soils. D: slope ≥8°. E (7k people) too sparse for a programme.')
Z = [('A', 'Raised / sealed unit', 'Sealed above-ground chamber or two-chamber box on a plinth above the worst remembered flood. No open pit.', D['zA'], NAVY),
     ('B', 'Raised slab + lined pit', 'Fully lined pit; slab and squat hole above flood level; sealed lid for the flood season.', D['zB'], COB),
     ('C', 'Lined pit on clay', 'Lining that tolerates swelling clay; dry or low-water design for the five-month dry season.', D['zC'], SAND),
     ('D', 'Steep ground', 'Eastern highland slopes ≥8°: drainage, erosion and access decided on site.', D['zD'], BROWN)]
for i, (z, h, t, n, col) in enumerate(Z):
    x = 0.6 + i * 3.1
    rect(s, x, 1.6, 2.9, 5.2, col, name='Zone card')
    tb(s, x + 0.25, 1.75, 2.4, 1.0, z, size=54, color=WHITE, font=HEAD, bold=True)
    tb(s, x + 0.25, 2.85, 2.45, 0.8, h, size=18, color=WHITE, font=HEAD, bold=True)
    tb(s, x + 0.25, 3.7, 2.45, 2.0, t, size=14, color=WHITE)
    tb(s, x + 0.25, 5.85, 2.45, 0.8, [[(f'{n/1000:,.0f}k', {'size': 26, 'bold': True, 'font': HEAD}), (' people', {'size': 14})]], color=WHITE)

s = content('What every unit includes', 'Safety, health and resilience  ·  team proposal',
            notes='Features come from the FloodSafe Sanitation draft and the risks named in camp surveys (no lock, no separate men\'s/women\'s latrines, night-time use).')
F3 = [('Safety', ['Inside lock and solid door', 'Solar light', 'Separate women\'s units where shared', 'Close to the home, away from night paths']),
      ('Health', ['Handwashing point with water store', 'Screened vent and fly-proof lid', 'Cover-material store', 'Safe emptying route']),
      ('Resilience', ['Plinth above the design flood', 'Anchored shelter', 'Flood-season seal', 'Pre-rain emptying check'])]
for i, (h, its) in enumerate(F3):
    x = 0.6 + i * 4.1
    rect(s, x, 1.6, 3.85, 3.05, ICE, name='Feature card')
    c = rect(s, x + 0.25, 1.8, 0.6, 0.6, [NAVY, COB, AZ][i], shape=MSO_SHAPE.OVAL, name='Icon dot')
    tb(s, x + 1.0, 1.82, 2.6, 0.55, h, size=20, color=NAVY, font=HEAD, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    bullets(s, x + 0.25, 2.6, 3.4, 2.0, its, size=14)
card(s, 0.6, 4.9, 6.0, 1.95, 'Around the toilet', 'Site check before building · local masons trained and paid per unit and repair · early warning without power: groundwater gauge and green/yellow/red pegs, forecast alert, local helper · emergency pack and high-ground swap point for long floods.', fill=WHITE, size=13)
s.shapes[-3].line.color.rgb = LINE
card(s, 6.85, 4.9, 5.9, 1.95, 'Honest limits', 'No toilet can be used under water. Raised and lined latrines already exist elsewhere in East Africa; the gauge, sealed unit, lining and forecast rule are untested in Gambella.', fill=RGBColor(0xFF, 0xF6, 0xEC), hc=WARN, size=13)

s = content('Why this is innovative — and what is not new', 'Positioning against existing practice  ·  own analysis',
            notes='Be honest with reviewers: the hardware ideas exist; the innovation is matching design to measured site conditions, safety-by-default and local repair.')
table(s, 0.6, 1.65, 12.15, [
    ['Design choice', 'One standard pit latrine', 'Toilet type chosen per site from flood, soil and slope data'],
    ['Flood', 'Pits flood and spread waste', 'Raised or sealed units where floods are frequent; flood-season seal'],
    ['Soil', 'Unlined pits slump in swelling clay', 'Linings tested for clay; masons trained to repair'],
    ['Safety', 'Locks, light, separation often missing', 'Lock, light, privacy and women\'s units in every design'],
    ['Warning', 'Depends on phone/internet', 'Gauge and colour pegs, local helper, forecast rule'],
    ['After the project', 'Breaks, not repaired', 'Local masons earn from repairs; savings groups for payment'],
    ['Evidence', 'Coverage counted', 'Use, flood survival, cost per zone and women\'s safety measured']],
      ['Topic', 'Common practice', 'FloodSafe approach'], colw=[2.3, 4.1, 5.75], size=14, rowh=0.56)
tb(s, 0.6, 6.55, 12.1, 0.4, 'Not new: raised and lined latrines exist (e.g. Kenya, Mozambique). New here: the combination, the site rules and the measurement plan.', size=13, color=MUTED)

# =============================== 5. Implementation plan
divider(5, 'Implementation plan', 'Validate, design, pilot, evaluate — then scale')
s = content('Five phases, learning before scaling', 'Durations and dates to be agreed  ·  team proposal',
            notes='Phase 0 validates zones on the ground and runs the baseline survey (with ethics approval for the safety questions). Phase 1 produces real costs. Scale only if pilot targets are met.')
PH = [('0', 'Validate', 'Consultation, site checks (flood marks, soil pits, wells), baseline survey incl. safety, confirm zones'),
      ('1', 'Design & cost', 'Prototype each zone with local masons; record real costs; flood-test sealed unit and lining; engineer sets design flood margin'),
      ('2', 'Pilot', 'Build in Jikawo, Wantawo, Lare + one camp; train masons and helpers; savings groups; gauges and pegs; first flood season'),
      ('3', 'Evaluate', 'Repeat survey; pilot vs comparison villages; flood damage, cost per household, use by women and girls; publish failures too'),
      ('4', 'Scale', 'Akobo, Itang and remaining zone A/B areas if targets are met; hand over to masons and woreda health offices')]
for i, (n, h, t) in enumerate(PH):
    x = 0.6 + i * 2.5
    c = rect(s, x + 0.75, 1.65, 0.85, 0.85, [NAVY, DEEP, COB, AZ, SKY][i], shape=MSO_SHAPE.OVAL, name='Phase dot')
    tf = c.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    r = p.add_run(); r.text = n; r.font.name = HEAD; r.font.size = Pt(24); r.font.bold = True; r.font.color.rgb = WHITE if i < 4 else NAVY
    if i < 4:
        ln = s.shapes.add_connector(1, Inches(x + 1.65), Inches(2.075), Inches(x + 3.2), Inches(2.075)); ln.line.color.rgb = SKY; ln.line.width = Pt(3); ln.name = 'Connector'
    rect(s, x, 2.75, 2.35, 4.05, ICE, name='Phase card')
    tb(s, x + 0.2, 2.9, 1.95, 0.5, h, size=18, color=NAVY, font=HEAD, bold=True)
    tb(s, x + 0.2, 3.45, 1.95, 3.3, t, size=13)

import pandas as _pd
BS = _pd.read_csv(R + 'data/budget_summary.csv', encoding='utf-8-sig'); BA = _pd.read_csv(R + 'data/budget_assumptions.csv', encoding='utf-8-sig')
_hh = int(BA.loc[BA.assumption == 'Pilot households', 'value'].iat[0]); _ppl = int(float(BA.loc[BA.assumption.str.startswith('People reached'), 'value'].iat[0]))
_t = BS[['total_low', 'total_mid', 'total_high']].sum()
k = lambda v: f"{v/1000:,.0f}k"
s = content('Partners and estimated pilot budget', f'Estimate for a {_hh}-household pilot, USD 2026  ·  own estimate',
            src='Unit costs from UNHCR, SDI, AICD, IRC WASHCost, Crocker et al. 2021 and Ethiopian market data; details in data/budget_estimate.csv',
            notes='All amounts are estimates built from published unit costs elsewhere in Ethiopia and East Africa; no Gambella cost data exist. Assumptions: 400 zone A + 100 zone B households in Jikawo, Wantawo and Lare, 20 shared stances in one camp, 30 masons, 1,000 interviews per survey round. Management share 24% follows the Ethiopia CLTS programme (Crocker et al. 2021). Phase 1 replaces these with real quotes.')
card(s, 0.6, 1.6, 4.6, 2.75, 'Partners to involve', '', size=14)
bullets(s, 0.8, 2.2, 4.2, 2.1, ['Regional health and water bureaus, woredas, health extension workers', 'UNHCR, RRS, camp WASH partners',
                                 "Masons, women's and savings groups; a university partner [to be confirmed]"], size=13)
rect(s, 0.6, 4.55, 4.6, 2.3, NAVY, name='Total card')
tb(s, 0.85, 4.7, 4.1, 0.4, 'ESTIMATED PILOT TOTAL', size=13, color=SKY, font=HEAD, bold=True)
tb(s, 0.85, 5.1, 4.1, 0.8, f"USD {k(_t.total_mid)}", size=36, color=WHITE, font=HEAD, bold=True)
tb(s, 0.85, 5.9, 4.1, 0.9, f"range {k(_t.total_low)} – {k(_t.total_high)} · about USD {_t.total_mid/_hh:,.0f} per household, {_t.total_mid/_ppl:,.0f} per person ({_hh} households, ~{_ppl:,} people)", size=12, color=WHITE)
table(s, 5.5, 1.6, 7.25, [[str(int(r.line_no)), r.budget_line, k(r.total_mid), f"{k(r.total_low)}–{k(r.total_high)}"] for _, r in BS.iterrows()]
      + [['', 'Total', k(_t.total_mid), f"{k(_t.total_low)}–{k(_t.total_high)}"]],
      ['#', 'Budget line', 'Mid (USD)', 'Range'], colw=[0.45, 4.0, 1.25, 1.55], size=12, rowh=0.415, num=(2, 3))

BE = _pd.read_csv(R + 'data/budget_estimate.csv', encoding='utf-8-sig')
s = content('Where the cost estimates come from', 'Unit costs behind the pilot budget  ·  own estimate',
            src='UNHCR (UDDT SOP, Innovation); SDI; Kenya GTZ 2009; rural Ethiopia latrine study 2023; AICD; IRC WASHCost; Crocker et al. 2021; TechXLab; FX 161.3 ETB/USD (16 Nov 2026)',
            notes='Only toilet units, hygiene activities and the management share rest on published figures; the rest are own estimates. The UNHCR UDDT guide and the rural Ethiopia latrine study were read from search excerpts only (full text blocked). Replace with Phase 1 quotes.')
_rows = []
for item, short in [('Raised / sealed units', 'Zone A unit'), ('Raised slab + lined pit', 'Zone B unit'), ('Shared stances, one refugee camp', 'Camp stance'),
                    ('Lock, light, door upgrade', 'Safety kit'), ('Hygiene promotion and follow-up', 'Hygiene work'), ('Baseline survey interviews', 'Interview'),
                    ('Gauge, pegs, emergency pack', 'Gauge + pack'), ('Management, staff, transport', 'Management')]:
    r = BE[BE.item == item].iloc[0]
    unit = (f"{r.unit_low*100:.0f}–{r.unit_high*100:.0f}% (mid {r.unit_mid*100:.0f}%)" if r.unit_mid < 1 else f"${r.unit_low:,.0f}–{r.unit_high:,.0f} (mid ${r.unit_mid:,.0f})")
    basis = {'Zone A unit': 'UNHCR UDDT ~$500 (Gambella); UNHCR $400–700; SDI raised toilet $350–500; plinth extra',
             'Zone B unit': 'Rural Ethiopia model latrine ~4,000 ETB (≈$110, unlined); VIP $441 (Senegal); slab $12–18',
             'Camp stance': 'Own estimate from zone A/B costs + handwashing, light',
             'Safety kit': 'Solar lanterns $1–20 (catalogue); lock and door own estimate',
             'Hygiene work': 'Ethiopia CLTS $16.5–22.6 per household (2012–14), inflated',
             'Interview': 'Own estimate; no Ethiopia per-interview cost found',
             'Gauge + pack': 'Own estimate', 'Management': 'Ethiopia CLTS: management 23.7% of total'}[short]
    _rows.append([short, unit, basis, r.confidence])
table(s, 0.6, 1.6, 12.15, _rows, ['Item', 'Unit cost (USD)', 'Basis', 'Confidence'], colw=[1.7, 2.6, 6.45, 1.4], size=12, rowh=0.52)
tb(s, 0.6, 6.5, 12.1, 0.45, [[('Biggest lever: ', {'bold': True, 'color': DEEP}), ('toilet units are ~54% of the total — price the zone A unit (plinth + sealed chamber) first. ', {}),
                             ('Full model: data/budget_estimate.csv', {'italic': True, 'color': MUTED})]], size=13)

# =============================== 6. Impact
divider(6, 'Impact', 'Who benefits and how we will know')
s = content('Who benefits', 'People by toilet zone and first-phase reach', src='WorldPop 2020 (host population), UNHCR (refugees), own zone rules',
            notes='Host population figures exclude most camp refugees. First phase numbers per village are set after site checks and costing.')
jwl = [w for w in D['woredas'] if w['w'] in ('Jikawo', 'Wantawo', 'Lare')]
stat(s, 0.6, 1.6, 3.9, 1.7, f"{sum(w['people'] for w in jwl):,}", 'residents in the first-phase woredas (Jikawo, Wantawo, Lare)', bigsize=32)
stat(s, 4.7, 1.6, 3.9, 1.7, f"{sum(w['hp'] for w in jwl):,}", 'of them in high-priority cells — almost all zone A', bigsize=32)
stat(s, 8.8, 1.6, 3.95, 1.7, f"{D['refugees']:,}", 'registered refugees region-wide; one camp in the pilot', bigsize=32)
cd = CategoryChartData(); cd.categories = ['A: raised / sealed', 'B: raised slab + lined pit', 'C: lined pit on clay', 'D: steep ground']
cd.add_series('People (WorldPop 2020)', [D['zA'], D['zB'], D['zC'], D['zD']])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.6), Inches(3.55), Inches(6.6), Inches(3.3), cd); gf.name = 'Zone chart'
ch = gf.chart; style_chart(ch, 'Residents by toilet zone', size=12)
ser = ch.plots[0].series[0]; ch.plots[0].gap_width = 45
for k, col in enumerate([NAVY, COB, SAND, BROWN]):
    p_ = ser.points[k]; p_.format.fill.solid(); p_.format.fill.fore_color.rgb = col
ch.plots[0].has_data_labels = True; dl = ch.plots[0].data_labels; dl.number_format = '#,##0'; dl.number_format_is_linked = False; dl.font.size = Pt(11); dl.position = XL_LABEL_POSITION.OUTSIDE_END
ch.value_axis.visible = False; ch.value_axis.has_major_gridlines = False; ch.category_axis.reverse_order = True
card(s, 7.5, 3.55, 5.25, 3.3, 'Expected benefits', '', size=14)
bullets(s, 7.7, 4.15, 4.9, 2.7, ['Health: less open defecation and diarrhoea, fewer cholera outbreaks', 'Safety: fewer night trips to the bush for women and girls',
                                 'Resilience: toilets usable again soon after floods', 'Economy: local mason jobs; lower cost of outbreak response'], size=14)

s = content('How we will measure impact', 'Indicators with baselines from the data pack  ·  targets set after the baseline survey',
            notes='Regional DHS values are context, not a village baseline. Surveys on violence follow WHO safety and ethics guidance: trained female enumerators, private interviews, referral to services.')
table(s, 0.6, 1.6, 12.15, [
    ['Open defecation, % of population', f"{D['od24']:.1f}% (region, DHS 2024)", 'Household survey, pilot vs comparison', '[to be set]'],
    ['Improved sanitation, % of population', f"{D['imp24']:.1f}% (region, DHS 2024)", 'Household survey', '[to be set]'],
    ['Latrine owners who still go outside', '47.2% (Gambella town, 2023)', 'Survey and observation', '[to be set]'],
    ['Toilets usable after the flood season', 'No baseline', 'Post-flood inspection of every unit', '[to be set]'],
    ['On-site toilets never emptied', '97.2% (region, DHS 2024)', 'Inspection, mason records', '[to be set]'],
    ['People per latrine, pilot camp', '6–64 (UNHCR 2015–2026)', 'Camp WASH monitoring', 'SPHERE ≤ 20'],
    ['Women and girls who feel unsafe using the toilet', '13% (Pugnido II, 2017)', 'Survey with female enumerators', '[to be set]'],
    ['Child diarrhoea, past 2 weeks', f"{D['diar24']:.1f}% (region, DHS 2024)", 'Survey; health post records', '[to be set]'],
    ['Cost per household by zone', 'Unknown', 'Project accounts', 'Recorded in Phase 1'],
    ['Trained masons still working after 12 months', 'None yet', 'Follow-up', '[to be set]']],
      ['Indicator', 'Baseline (source)', 'How measured', 'Target'], colw=[4.1, 3.3, 3.25, 1.5], size=13, rowh=0.47)

# =============================== 7. Scalability
divider(7, 'Scalability plan', 'From three woredas to the whole flood plain')
s = content('How the idea scales', 'Scale only what the pilot proves  ·  team proposal', src='Woreda figures: own priority index (WorldPop 2020, JRC, SoilGrids, CHIRPS)',
            notes='Expansion order follows the priority index: Akobo and Itang next, then remaining zone A/B areas; camps through UNHCR partners. The same site rules can be applied in other flood plains with the open data used here.')
STG = [('Pilot', f"Jikawo · Wantawo · Lare\n+ one camp ({sum(w['people'] for w in jwl)/1000:,.0f}k live there)", f"{_hh} households first"),
       ('Next', 'Akobo · Itang\n+ more camps via UNHCR', f"{sum(w['people'] for w in D['woredas'] if w['w'] in ('Akobo','Itang'))/1000:,.0f}k residents"),
       ('Region', 'All zone A and B areas\nof Gambela', f"{(D['zA']+D['zB'])/1000:,.0f}k residents"),
       ('Beyond', 'Other flood plains in Ethiopia\nand the region', 'same open data and rules')]
for i, (h, t, n) in enumerate(STG):
    x = 0.6 + i * 3.1; hgt = 2.0 + i * 0.55; y = 4.55 - i * 0.55
    rect(s, x, y, 2.9, hgt, [SKY, AZ, COB, NAVY][i], name='Stage block')
    tc = NAVY if i == 0 else WHITE
    tb(s, x + 0.2, y + 0.15, 2.5, 0.5, h.upper(), size=18, color=tc, font=HEAD, bold=True)
    tb(s, x + 0.2, y + 0.65, 2.5, 0.8, t, size=13, color=tc)
    tb(s, x + 0.2, y + hgt - 0.6, 2.5, 0.45, n, size=15, color=tc, bold=True)
bullets(s, 0.6, 1.55, 12.1, 1.9, [f'Cost efficiency: estimated pilot cost about USD {_t.total_mid/_hh:,.0f} per household (USD {_t.total_mid/_ppl:,.0f} per person); standard designs, local materials and masons should lower unit costs at scale (to be shown in Phase 3).',
                                  'Funding: household savings groups and instalments, targeted subsidies, landlords, UNHCR/WASH partners for camps, government and donor funds.',
                                  'Policy: work through woreda health offices and the regional WASH bureau so designs enter local standards.'], size=14)

s = content('Risks and how we respond', 'Risk register and sustainability  ·  team proposal')
table(s, 0.6, 1.6, 7.7, [
    ['Flood larger than the design flood', 'Engineer-set margin; emergency pack and swap point; repair fund'],
    ['Swelling clay cracks linings', 'Test linings in Phase 1; flexible joints; trained repair'],
    ['Toilets built but not used', 'Design with users; women choose placement; measure use'],
    ['Costs too high for poor households', 'Savings groups, instalments, targeted subsidy'],
    ['Conflict and insecurity', 'Local partners; flexible schedule; do-no-harm review'],
    ['Data gaps (groundwater, village data)', 'Site checks and baseline fill gaps first'],
    ['Violence survey causes harm', 'Ethics approval, female enumerators, referral, no names stored']],
      ['Risk', 'Response'], colw=[3.2, 4.5], size=13, rowh=0.66)
card(s, 8.6, 1.6, 4.15, 2.5, 'Sustainability', 'Masons keep building and repairing; savings groups build ownership; woreda health offices take over monitoring; designs and costs are published.', size=14)
card(s, 8.6, 4.3, 4.15, 2.5, 'Gender and inclusion', 'Women choose designs and locations; accessible units for older and disabled people; female masons and helpers where possible.', size=14)

# =============================== 8. Supporting materials
divider(8, 'Supporting materials', 'Evidence, methods, checks and sources')
s = content('How the evidence was built', 'Process and data sources',
            notes='Everything is rebuildable from scripts in gambella/scripts. Raw downloads are kept in gambella/raw with download logs.')
FL = [('Collect', '15+ open sources; every file and download logged'), ('Extract', 'Rows with quote, source, URL, year; no gaps filled'),
      ('Grid', '1,002 cells of 0.05°; zonal stats per woreda'), ('Analyse', 'Rank correlations, exposure, priority, zones'), ('Verify', 'Independent re-check of sources and cells')]
for i, (h, t) in enumerate(FL):
    x = 0.6 + i * 2.5
    rect(s, x, 1.6, 2.3, 1.55, ICE, name='Process step')
    tb(s, x + 0.18, 1.7, 2.0, 0.45, f'{i+1}  {h}', size=16, color=COB, font=HEAD, bold=True)
    tb(s, x + 0.18, 2.2, 2.0, 0.9, t, size=12)
table(s, 0.6, 3.4, 12.15, [
    ['Sanitation, water, hygiene, diarrhoea, violence', 'DHS Program API — Ethiopia DHS 2000–2024-25', 'region'],
    ['GDP; regional GNI and HDI; gridded GDP; poverty', 'World Bank API; Global Data Lab; Kummu et al.; NPC 2017', 'national / region'],
    ['Flood and drought events', 'UN, IFRC GO, GDACS, Dartmouth Flood Observatory, peer-reviewed, news; EM-DAT via OWID', 'event'],
    ['Elevation, population, soil', 'Copernicus DEM GLO-90; WorldPop 2020 1 km; ISRIC SoilGrids 2.0', '90 m – 1 km'],
    ['Rainfall, drought, flood extent', 'CHIRPS v2.0; CHC SPEI-12; JRC Global Surface Water and flood hazard maps', '30 m – 5 km'],
    ['Boundaries, camps, safety surveys', 'geoBoundaries; OCHA COD-AB; UNHCR; WASH KAP 2017; HVACS 2024; Europe PMC', 'woreda / camp']],
      ['Data', 'Source', 'Level'], colw=[3.9, 6.45, 1.8], size=12, rowh=0.5)

s = content('Key correlations', 'Spearman rank correlations  ·  own analysis', src='Grid: 1,002 cells / 50 blocks of 0.25°; regions: 11 × 6 DHS rounds; years: 1981–2025',
            notes='Correlations show association, not cause. Grid p-values are only meaningful at block level because neighbouring cells are not independent.')
table(s, 0.6, 1.6, 6.0, [
    ['Elevation vs 100-year flood extent', D['r_elev_flood'], D['r_elev_flood_b']],
    ['Elevation vs population density', D['r_elev_pop'], D['r_elev_pop_b']],
    ['Elevation vs dry months per year', D['r_elev_dry'], '–'],
    ['Population vs rain-deficit years', D['r_pop_drought'], '–'],
    ['Population vs 100-year flood extent', D['r_pop_flood'], '–']], ['Gambela grid', 'ρ cells', 'ρ blocks'], colw=[3.8, 1.1, 1.1], size=13, rowh=0.46, num=(1, 2))
table(s, 6.85, 1.6, 5.9, [
    ['Open defecation vs GNI per capita', D['r_od_gni'], '–'],
    ['Improved sanitation vs GNI per capita', D['r_imp_gni'], f"{D['r_imp_gni_fd']:.2f}"],
    ['Open defecation vs HDI', D['r_od_hdi'], D['r_od_hdi_fd']],
    ['Open defecation vs child diarrhoea', D['r_od_diar'], '–']], ['11 regions × 6 rounds', 'ρ across', 'ρ change'], colw=[3.7, 1.1, 1.1], size=13, rowh=0.5, num=(1, 2))
table(s, 6.85, 4.4, 5.9, [
    ['Annual rain vs flood record', D['r_rain_flood']], ['Annual rain vs drought record', D['r_rain_drought']],
    ['SPEI-12 vs drought record', D['r_spei_drought']], ['Year vs annual rain', D['r_year_rain']]], ['Gambela 1981–2025', 'ρ'], colw=[4.8, 1.1], size=13, rowh=0.48, num=(1,))
picture(s, M + 'scatter_elevation.png', 0.6, 4.85, h=2.0)

s = content('Data quality and limits', 'Independent re-check, 16 Nov 2026',
            notes='Errors fixed: 2007 flood figures (an Ethiopia-wide record and a five-region total had been attributed to Gambella), a 0.1° population grid offset, one literature effect size.')
table(s, 0.6, 1.6, 6.2, [[r[0], f(r[1]), f(r[2]), f(r[3]), f(r[4])] for r in D['ver']], ['File', 'Rows', 'Confirmed', 'Wrong', 'Not checked'], colw=[2.3, 0.9, 1.1, 0.9, 1.0], size=12, rowh=0.5, num=(1, 2, 3, 4))
bullets(s, 0.6, 4.25, 6.2, 2.6, ['Fixed: 2007 flood figures, a 0.1° population offset, one study effect size.',
                                 'Still uncertain: 2021 vs 2020 for 11,749 displaced; 2024 may be double-counted; 2019 sources differ eightfold.'], size=14)
card(s, 7.1, 1.6, 5.65, 5.25, 'What the evidence cannot yet show', '', fill=RGBColor(0xFF, 0xF6, 0xEC), hc=WARN)
bullets(s, 7.3, 2.2, 5.3, 4.6, ['No village-level toilet data: the map shows where pits fail, not where toilets are missing.',
                                'Refugees are largely missing from the population map.', 'Flood maps are global river models; rain flooding not included.',
                                'Groundwater depth not found — must be measured on site.', 'Regional income is modelled; no official regional GDP.',
                                'Violence data are not comparable and likely undercounts.', 'Correlation is not cause.'], size=14)

s = content('Supporting maps', 'Robustness, soil and camps', src='Own analysis; SoilGrids 2.0; UNHCR camp populations (2022)')
picture(s, M + 'sanitation_priority_robustness.png', 0.6, 1.55, h=5.3)
picture(s, M + 'map_soil_class.png', 6.75, 1.55, h=3.0)
table(s, 6.75, 4.75, 6.0, [[c['c'], f(c['pop']), c['z'], c['fl']] for c in D['camps']], ['Camp', 'Refugees', 'Zone', '100-yr flood %'],
      colw=[2.0, 1.4, 1.0, 1.6], size=10, rowh=0.235, num=(1, 3))

# closing
s = prs.slides.add_slide(BLANK)
s.shapes.add_picture(P + 'deck_img/bg_section.png', 0, 0, prs.slide_width, prs.slide_height).name = 'Background'
tb(s, 0.9, 1.9, 9, 1.2, 'THANK YOU', size=48, color=WHITE, font=HEAD, bold=True, name='Title')
tb(s, 0.9, 3.05, 8.5, 1.4, 'FloodSafe Sanitation Gambella — toilets that survive the flood, keep women safe and stay repaired.', size=20, color=SKY)
tb(s, 0.9, 4.7, 8.5, 1.2, [[('Contact: ', {'bold': True}), ('[Organisation name] · [contact]', {'italic': True})],
                          'Full proposal (PDF), data pack and scripts: OneDrive/Research/gambella/'], size=14, color=WHITE)

prs.core_properties.title = 'FloodSafe Sanitation Gambella — pitch deck (draft)'
out = P + 'FloodSafe_Sanitation_Gambella_deck.pptx'
prs.save(out); print('saved', out, len(prs.slides._sldIdLst), 'slides')
