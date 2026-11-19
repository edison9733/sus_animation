"""Export the numbers the slide deck needs (read from data/*.csv) to proposal/deck_data.json, and draw the retro
background images (PIL). Usage: python an06_deck_data.py <gambella root>"""
import sys, json, os
import numpy as np, pandas as pd
from PIL import Image, ImageDraw, ImageFilter

R = sys.argv[1].rstrip('/') + '/'; OUT = R + 'proposal/'; os.makedirs(OUT + 'deck_img', exist_ok=True)
rd = lambda f: pd.read_csv(R + 'data/' + f, encoding='utf-8-sig', low_memory=False)
ex = rd('population_exposure.csv'); pn = rd('ethiopia_regions_panel.csv'); cr = rd('correlations_regions.csv'); cg = rd('correlations_grid.csv')
cy = rd('correlations_yearly.csv'); ev = rd('gambella_flood_drought_events.csv'); sf = rd('gambella_safety_gbv.csv'); es = rd('gambella_economy_sanitation.csv')
bands = rd('gambella_elevation_bands.csv'); camps = rd('gambella_refugee_camps.csv'); spw = rd('sanitation_priority_woredas.csv'); spg = rd('sanitation_priority_grid.csv')
spc = rd('sanitation_priority_camps.csv'); ey = rd('ethiopia_flood_drought_yearly.csv'); lit = rd('sanitation_violence_literature.csv')
sh = lambda g: round(float(ex.loc[ex.group == g, 'share_population'].iat[0] * 100))
def cgv(x, y, col='spearman_cells'):
    r = cg[((cg.var_x == x) & (cg.var_y == y)) | ((cg.var_x == y) & (cg.var_y == x))]; return round(float(r[col].iat[0]), 2)
def crv(s, x, y):
    r = cr[(cr['sample'] == s) & (((cr.var_x == x) & (cr.var_y == y)) | ((cr.var_x == y) & (cr.var_y == x)))]; return round(float(r.spearman.iat[0]), 2)
def cyv(x, y): r = cy[(cy['sample'] == '1981-2025') & (cy.var_x == x) & (cy.var_y == y)]; return round(float(r.spearman.iat[0]), 2)
def dv(code, yr, geo): return float(sf[sf.indicator.str.contains(code, regex=False) & sf.year.astype(str).str.startswith(str(yr)) & (sf.geography == geo)].value.iat[0])
gam = pn[pn.region == 'Gambela'].sort_values('year')
zp = spg.groupby('toilet_zone').pop_2020.sum()
rob = spg[spg.top20_agreement == 4]
e = ev[~ev.event_id.str.startswith('GAP') & (ev.verified != 'no')].copy()
num = lambda s: pd.to_numeric(s.astype(str).str.replace(',', '').str.extract(r'(\d+)')[0], errors='coerce')
e['dis'] = num(e.people_displaced); e['aff'] = num(e.people_affected)
eg = e.groupby('event_id').agg(type=('event_type', 'first'), year=('year', 'first'), dis=('dis', 'max'), aff=('aff', 'max')).reset_index()
fl = eg[(eg.type == 'flood') & eg.dis.notna()].groupby('year').dis.sum().reset_index()
wb = es[(es.admin_level == 'national') & (es.indicator == 'GDP per capita (current US$)')].copy(); wb['y'] = pd.to_numeric(wb.year, errors='coerce'); wb = wb.dropna(subset=['y']).sort_values('y')
wb = wb[wb.y >= 2000]
p19 = pn[pn.year == 2019].sort_values('open_defecation_pop_pct', ascending=False)
D = dict(
    od24=float(gam.open_defecation_pop_pct.iat[-1]), od16=float(gam[gam.year == 2016].open_defecation_pop_pct.iat[0]),
    imp24=float(gam.improved_sanitation_pop_pct.iat[-1]), diar24=float(gam.child_diarrhoea_pct.iat[-1]), lowq24=float(gam.lowest_wealth_quintile_pop_pct.iat[-1]),
    gni00=float(gam.gdl_gni_pc_ppp2017.iat[0]), gni23=float(gam.gdl_gni_pc_ppp2017.iat[-1]),
    san_years=[int(y) for y in gam.year], san_od=[float(v) for v in gam.open_defecation_pop_pct], san_imp=[float(v) for v in gam.improved_sanitation_pop_pct],
    flood10=sh('100-year river flood covers >= 10% of cell'), flood50=sh('100-year river flood covers >= 50% of cell'), vert=sh('Vertisols (swelling clay) dominant'),
    vertflood=sh('100-year flood >= 50% AND Vertisols'), band45=round(float(bands.loc[bands.band_m == '400-500', 'share_population'].iat[0] * 100)),
    hostpop=round(float(spg.pop_2020.sum())), hp=round(float(spg[spg.priority >= .6].pop_2020.sum())), rob_cells=int(len(rob)), rob_pop=round(float(rob.pop_2020.sum())),
    zA=round(float(zp.get('A: raised / sealed above-ground unit', 0))), zB=round(float(zp.get('B: raised slab + lined pit', 0))),
    zC=round(float(zp.get('C: lined pit (clay), low flood', 0))), zD=round(float(zp.get('D: steep ground, site-specific', 0))),
    refugees=int(camps.loc[camps.camp.str.startswith('ALL registered'), 'population'].iat[0]),
    r_elev_flood=cgv('elev_mean_m', 'jrc_rp100_flooded_pct'), r_elev_flood_b=cgv('elev_mean_m', 'jrc_rp100_flooded_pct', 'spearman_blocks_025deg'),
    r_elev_pop=cgv('elev_mean_m', 'pop_density_km2'), r_elev_pop_b=cgv('elev_mean_m', 'pop_density_km2', 'spearman_blocks_025deg'),
    r_elev_dry=cgv('elev_mean_m', 'chirps_dry_months_lt30mm_mean'), r_pop_drought=cgv('pop_density_km2', 'chirps_share_years_below80pct'),
    r_pop_flood=cgv('pop_density_km2', 'jrc_rp100_flooded_pct'),
    r_imp_gni=crv('pooled 2000-2024', 'improved_sanitation_pop_pct', 'gdl_gni_pc_ppp2017'), r_od_gni=crv('pooled 2000-2024', 'open_defecation_pop_pct', 'gdl_gni_pc_ppp2017'),
    r_imp_gni_fd=abs(crv('change between surveys (first differences)', 'improved_sanitation_pop_pct', 'gdl_gni_pc_ppp2017')),
    r_od_hdi=crv('pooled 2000-2024', 'open_defecation_pop_pct', 'gdl_shdi'), r_od_hdi_fd=crv('change between surveys (first differences)', 'open_defecation_pop_pct', 'gdl_shdi'),
    r_od_diar=crv('pooled 2000-2024', 'open_defecation_pop_pct', 'child_diarrhoea_pct'),
    r_rain_flood=cyv('annual_mm', 'gam_flood_record'), r_rain_drought=cyv('annual_mm', 'gam_drought_record'), r_spei_drought=cyv('spei12_dec_mean', 'gam_drought_record'),
    r_year_rain=cyv('year', 'annual_mm'),
    ipv24_g=dv('DV_SPV1_W_POS', 2024, 'Gambela Region'), ipv24_e=dv('DV_SPV1_W_POS', 2024, 'Ethiopia'), sv24_g=dv('DV_EXSV_W_12M', 2024, 'Gambela Region'),
    sv24_e=dv('DV_EXSV_W_12M', 2024, 'Ethiopia'), ntl24_g=dv('DV_STPV_W_NTL', 2024, 'Gambela Region'), ntl24_e=dv('DV_STPV_W_NTL', 2024, 'Ethiopia'),
    fl_years=[int(y) for y in fl.year], fl_dis=[float(v) for v in fl.dis],
    n_events=int(eg.event_id.nunique()), n_flood=int((eg.type == 'flood').sum()), eth_floods=int(ey.flood_events.sum()), eth_droughts=int(ey.drought_events.sum()),
    gdp_years=[int(y) for y in wb.y], gdp=[round(float(v)) for v in pd.to_numeric(wb.value)],
    p19=[[r.region, float(r.open_defecation_pop_pct)] for _, r in p19.iterrows()],
    woredas=[dict(w=r.woreda, people=int(r.people), pri=float(r.mean_priority), hp=int(r.people_high_priority), share=float(r.share_high_priority),
                  A=int(r.people_zone_A), B=int(r.people_zone_B), C=int(r.people_zone_C), main=r.main_zone.split(':')[0]) for _, r in spw.iterrows()],
    camps=[dict(c=r.camp, pop=int(r.population), w=str(r.woreda_geoboundaries), z=str(r.toilet_zone).split(':')[0], fl=round(float(r.jrc_rp100_flooded_pct), 1)) for _, r in spc.iterrows()],
    ver=[[n, int(len(d)), int((d.verified == 'yes').sum()), int((d.verified == 'no').sum()), int((d.verified == 'not_checked').sum())]
         for n, d in [('Flood/drought events', ev), ('Economy & sanitation', es), ('Safety / GBV', sf), ('Toilet–violence studies', lit)]],
    lit=[[r.authors.split(',')[0] + ' et al.', int(r.year), r.country, str(r.effect_size)[:110]] for _, r in lit.iterrows()
         if not str(r.effect_size).startswith(('NOT', 'none', 'not app', 'Not in'))],
)
json.dump(D, open(OUT + 'deck_data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- retro backgrounds (13.333 x 7.5 in at 150 dpi)
W, H = 2000, 1125
NAVY, DEEP, COB, AZ, SKY, ICE = (10, 31, 77), (18, 58, 130), (30, 91, 184), (61, 143, 224), (140, 195, 255), (227, 240, 255)
def arcs(img, cx, cy, radii, colors, gap):
    d = ImageDraw.Draw(img)
    for r, c in zip(radii, colors):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c); d.ellipse([cx - r + gap, cy - r + gap, cx + r - gap, cy + r - gap], fill=(255, 255, 255))
def sun(img, cx, cy, R, col, n=30):
    d = ImageDraw.Draw(img)
    for i in range(n):
        a0 = np.radians(180 + i * 360 / n); a1 = np.radians(180 + i * 360 / n + 360 / n / 2)
        d.polygon([(cx, cy), (cx + R * np.cos(a0), cy + R * np.sin(a0)), (cx + R * np.cos(a1), cy + R * np.sin(a1))], fill=col)
# title: white, sunburst + concentric arcs rising bottom-right
t = Image.new('RGB', (W, H), 'white'); sun(t, 1800, 1250, 1500, (236, 244, 255))
d = ImageDraw.Draw(t)
for r, c in zip([820, 700, 580, 460], [NAVY, DEEP, COB, AZ]):
    d.ellipse([1800 - r, 1250 - r, 1800 + r, 1250 + r], fill=c); d.ellipse([1800 - r + 95, 1250 - r + 95, 1800 + r - 95, 1250 + r - 95], fill='white')
d.ellipse([1800 - 340, 1250 - 340, 1800 + 340, 1250 + 340], fill=SKY); d.ellipse([1800 - 250, 1250 - 250, 1800 + 250, 1250 + 250], fill='white')
t.save(OUT + 'deck_img/bg_title.png')
# section divider: navy gradient left-to-right with light arcs on the right
s = Image.new('RGB', (W, H)); px = s.load()
for x in range(W):
    f = x / W; c = tuple(int(NAVY[k] + (COB[k] - NAVY[k]) * f) for k in range(3))
    for y in range(H): px[x, y] = c
ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
for r, a in zip([900, 760, 620, 480, 340], [40, 55, 70, 90, 110]):
    d.ellipse([1700 - r, 1200 - r, 1700 + r, 1200 + r], outline=(140, 195, 255, a), width=70)
s = Image.alpha_composite(s.convert('RGBA'), ov).convert('RGB'); s.save(OUT + 'deck_img/bg_section.png')
# small corner arcs for content slides (top-right)
c = Image.new('RGBA', (600, 600), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
for r, col in zip([560, 470, 380, 290], [ICE, SKY, AZ, COB]):
    d.ellipse([600 - r, -r, 600 + r, r], outline=col + (255,), width=34)
c.save(OUT + 'deck_img/corner.png')
print('ok', len(D))
