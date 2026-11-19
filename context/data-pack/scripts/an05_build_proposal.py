"""NGO-style project proposal (draft) for a flood/drought-safe toilet in Gambela, rendered to PDF with Edge headless.
Usage: python an05_build_proposal.py <gambella root>
Figures in tables are read from data/*.csv. Proposal text, the priority index, design ideas and plans are the
team's / Claude's own proposals (labelled); budget figures, dates and partners are left as placeholders on purpose."""
import sys, html, re, subprocess, os
import numpy as np, pandas as pd

R = sys.argv[1].rstrip('/') + '/'
OUT = R + 'proposal/'
os.makedirs(OUT, exist_ok=True)
rd = lambda f: pd.read_csv(R + 'data/' + f, encoding='utf-8-sig', low_memory=False)
E = lambda s: html.escape('' if pd.isna(s) else str(s))
def F(v, d=1):
    if v is None or (isinstance(v, float) and np.isnan(v)): return '–'
    try: v = float(v)
    except Exception: return E(v)
    return f'{v:,.0f}' if abs(v) >= 100 or v.is_integer() else f'{v:,.{d}f}'
def T(rows, heads, num=(), cls=''):
    h = ''.join(f'<th class="{"n" if i in num else ""}">{x}</th>' for i, x in enumerate(heads))
    b = ''.join('<tr>' + ''.join(f'<td class="{"n" if i in num else ""}">{c}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'
IMG = lambda f, cap, cls='': f'<figure class="{cls}"><img src="../maps/{f}"><figcaption>{cap}</figcaption></figure>'
MINE = '<span class="mine">team proposal</span>'
ANAL = '<span class="mine">own analysis</span>'

# ---------------- data
ex = rd('population_exposure.csv'); pn = rd('ethiopia_regions_panel.csv'); cr = rd('correlations_regions.csv'); cg = rd('correlations_grid.csv')
cy = rd('correlations_yearly.csv'); ev = rd('gambella_flood_drought_events.csv'); sf = rd('gambella_safety_gbv.csv'); lit = rd('sanitation_violence_literature.csv')
es = rd('gambella_economy_sanitation.csv'); bands = rd('gambella_elevation_bands.csv'); camps = rd('gambella_refugee_camps.csv')
spw = rd('sanitation_priority_woredas.csv'); spg = rd('sanitation_priority_grid.csv'); spc = rd('sanitation_priority_camps.csv'); ey = rd('ethiopia_flood_drought_yearly.csv')
sh = lambda grp: ex.loc[ex.group == grp, 'share_population'].iat[0] * 100
P = spg.pop_2020.sum()
zp = spg.groupby('toilet_zone').pop_2020.sum()
gam = pn[pn.region == 'Gambela'].sort_values('year'); g24 = gam[gam.year == 2024].iloc[0]; g16 = gam[gam.year == 2016].iloc[0]
def cgv(x, y, col='spearman_cells'):
    r = cg[((cg.var_x == x) & (cg.var_y == y)) | ((cg.var_x == y) & (cg.var_y == x))]; return r[col].iat[0]
def crv(s, x, y):
    r = cr[(cr['sample'] == s) & (((cr.var_x == x) & (cr.var_y == y)) | ((cr.var_x == y) & (cr.var_y == x)))]; return r.spearman.iat[0]
def cyv(x, y): r = cy[(cy['sample'] == '1981-2025') & (cy.var_x == x) & (cy.var_y == y)]; return r.spearman.iat[0]
def esv(ind, geo='Gambella', yr=None):
    s = es[es.indicator.str.fullmatch(ind, na=False) & es.geography.str.contains(geo, na=False)]
    if yr is not None: s = s[s.year.astype(str).str.startswith(str(yr))]
    return s.value.iat[0]
def dv(code, yr, geo): return sf[sf.indicator.str.contains(code, regex=False) & sf.year.astype(str).str.startswith(str(yr)) & (sf.geography == geo)].value.iat[0]
refugees = int(camps.loc[camps.camp.str.startswith('ALL registered'), 'population'].iat[0])
hp = spg[spg.priority >= .6].pop_2020.sum(); rob = spg[spg.top20_agreement == 4]
band45 = bands.loc[bands.band_m == '400-500', 'share_population'].iat[0] * 100

# events, one row per event (largest figure among non-rejected sources)
e = ev[~ev.event_id.str.startswith('GAP') & (ev.verified != 'no')].copy()
num = lambda s: pd.to_numeric(s.astype(str).str.replace(',', '').str.extract(r'(\d+)')[0], errors='coerce')
e['aff'] = num(e.people_affected); e['dis'] = num(e.people_displaced)
eg = e.groupby('event_id').agg(type=('event_type', 'first'), year=('year', 'first'), aff=('aff', 'max'), dis=('dis', 'max'), n=('source', 'count'), places=('woredas_or_places', 'first')).reset_index().sort_values('year')
eth = ey[['flood_events', 'drought_events']].sum()

# ---------------- tables
t_glance = T([
    ['Project', 'FloodSafe Sanitation Gambella — flood- and drought-safe household toilets'],
    ['Location', 'Gambela Region, western Ethiopia (Baro–Akobo basin); first phase in Jikawo, Wantawo and Lare woredas'],
    ['Sector', 'WASH · climate adaptation (flood and drought) · protection from gender-based violence'],
    ['Problem', f'{g24.open_defecation_pop_pct:.0f}% of people practise open defecation (DHS 2024), unchanged since 2016; most people live on a flood plain with swelling clay soils'],
    ['People in high-priority area', f'{hp:,.0f} host residents (WorldPop 2020) + {refugees:,} registered refugees region-wide (UNHCR, Oct 2026)'],
    ['Approach', 'Toilet type matched to flood and soil conditions (zones A–D), built and repaired by trained local masons, with safety features for women and girls'],
    ['Implementing organisation', '<span class="ph">[Organisation name]</span> with <span class="ph">[local partners]</span>'],
    ['Duration · budget', '<span class="ph">[to be agreed]</span> · <span class="ph">[to be costed — no cost data yet]</span>'],
], ['Item', 'Summary'], cls='glance')

t_san = T([[int(r.year), F(r.open_defecation_pop_pct), F(r.improved_sanitation_pop_pct), F(r.basic_sanitation_pop_pct), F(r.child_diarrhoea_pct), F(r.gdl_gni_pc_ppp2017), F(r.gdl_shdi, 3)] for _, r in gam.iterrows()],
          ['DHS year', 'Open defecation %', 'Improved sanitation %', 'Basic sanitation %', 'Child diarrhoea %', 'GNI/cap PPP$ (modelled)', 'HDI (modelled)'], num=(1, 2, 3, 4, 5, 6))
p19 = pn[pn.year == 2019].sort_values('open_defecation_pop_pct', ascending=False)
t_p19 = T([[('<b>%s</b>' % r.region) if r.region == 'Gambela' else r.region, F(r.open_defecation_pop_pct), F(r.improved_sanitation_pop_pct), F(r.gdl_gni_pc_ppp2017)] for _, r in p19.iterrows()],
          ['Region, 2019', 'Open defecation %', 'Improved %', 'GNI/cap'], num=(1, 2, 3), cls='small')
t_safety = T([
    ['Physical or sexual partner violence, past 12 months', f'{dv("DV_SPV1_W_POS", 2024, "Gambela Region")}%', f'{dv("DV_SPV1_W_POS", 2024, "Ethiopia")}%', 'DHS 2024, women 15–49'],
    ['Sexual violence, past 12 months', f'{dv("DV_EXSV_W_12M", 2024, "Gambela Region")}%', f'{dv("DV_EXSV_W_12M", 2024, "Ethiopia")}%', 'DHS 2024'],
    ['Never sought help or told anyone (of women who experienced violence)', f'{dv("DV_STPV_W_NTL", 2024, "Gambela Region")}%', f'{dv("DV_STPV_W_NTL", 2024, "Ethiopia")}%', 'DHS 2024'],
    ['Sexual violence (study definition), Okugo camp', '34.9%', '–', 'Peer-reviewed, 2023'],
    ['Sexual partner violence, past 12 months, Pugnido camp', '35.5%', '–', 'Peer-reviewed, 2021'],
    ['Partner violence, lifetime, Gambella town', '58.8%', '–', 'Peer-reviewed, 2021'],
    ['Latrines that give no privacy (Kule / Pugnido camps)', '27% / 69%', '–', 'UNHCR WASH KAP 2017'],
    ['Feel unsafe using the latrine (Pugnido II camp)', '13%', '–', 'UNHCR WASH KAP 2017'],
    ['Adults who defecate in the bush at night (4 camps)', '7–12%', '–', 'UNHCR WASH KAP 2017'],
    ['Recent sexual violence that happened in the evening (20 camps nationally)', '43.2%', '–', 'HVACS 2024'],
], ['Measure', 'Gambela', 'Ethiopia', 'Source'], num=(1, 2))
t_lit = T([[E(r.authors.split(',')[0] + ' et al.'), int(r.year), E(r.country), E(str(r.effect_size)[:150])] for _, r in lit.iterrows() if not str(r.effect_size).startswith(('NOT', 'none', 'not app', 'Not in'))],
          ['Study', 'Year', 'Setting', 'Effect, as printed'], cls='small')
t_wor = T([[r.woreda, F(r.people), F(r.mean_priority, 2), F(r.people_high_priority), F(r.share_high_priority), F(r.people_zone_A), F(r.people_zone_B), F(r.people_zone_C), r.main_zone.split(':')[0]] for _, r in spw.iterrows()],
          ['Woreda', 'People', 'Priority', 'High-priority people', '% high', 'Zone A', 'Zone B', 'Zone C', 'Main'], num=(1, 2, 3, 4, 5, 6, 7), cls='small')
t_camps = T([[r.camp, F(r.population), E(r.woreda_geoboundaries), E(r.toilet_zone.split(':')[0]), F(r.jrc_rp100_flooded_pct), F(r.clay_15_30)] for _, r in spc.iterrows()],
            ['Camp', 'Refugees (2022)', 'Woreda', 'Zone', '100-yr flood %', 'Clay %'], num=(1, 4, 5), cls='small')
t_events = T([[int(r.year), r.type, E(str(r.places) if len(str(r.places)) <= 70 else str(r.places)[:68].rsplit(" ", 1)[0] + " …"), F(r.aff), F(r.dis), int(r.n)] for _, r in eg.iterrows()],
             ['Year', 'Type', 'Places', 'Affected', 'Displaced', 'Sources'], num=(3, 4, 5), cls='small')
t_corr = T([
    ['Elevation vs 100-year flood extent (grid cells)', F(cgv('elev_mean_m', 'jrc_rp100_flooded_pct'), 2), F(cgv('elev_mean_m', 'jrc_rp100_flooded_pct', 'spearman_blocks_025deg'), 2)],
    ['Elevation vs population density', F(cgv('elev_mean_m', 'pop_density_km2'), 2), F(cgv('elev_mean_m', 'pop_density_km2', 'spearman_blocks_025deg'), 2)],
    ['Elevation vs dry months per year', F(cgv('elev_mean_m', 'chirps_dry_months_lt30mm_mean'), 2), F(cgv('elev_mean_m', 'chirps_dry_months_lt30mm_mean', 'spearman_blocks_025deg'), 2)],
    ['Population density vs rain-deficit years', F(cgv('pop_density_km2', 'chirps_share_years_below80pct'), 2), F(cgv('pop_density_km2', 'chirps_share_years_below80pct', 'spearman_blocks_025deg'), 2)],
    ['Population density vs 100-year flood extent', F(cgv('pop_density_km2', 'jrc_rp100_flooded_pct'), 2), F(cgv('pop_density_km2', 'jrc_rp100_flooded_pct', 'spearman_blocks_025deg'), 2)],
], ['Pair (Gambela grid, n = 1,002 cells / 50 blocks)', 'ρ cells', 'ρ blocks'], num=(1, 2), cls='small')
t_corr2 = T([
    ['Open defecation vs GNI per capita', F(crv('pooled 2000-2024', 'open_defecation_pop_pct', 'gdl_gni_pc_ppp2017'), 2), F(crv('change between surveys (first differences)', 'open_defecation_pop_pct', 'gdl_gni_pc_ppp2017'), 2)],
    ['Improved sanitation vs GNI per capita', F(crv('pooled 2000-2024', 'improved_sanitation_pop_pct', 'gdl_gni_pc_ppp2017'), 2), F(abs(crv('change between surveys (first differences)', 'improved_sanitation_pop_pct', 'gdl_gni_pc_ppp2017')), 2)],
    ['Open defecation vs HDI', F(crv('pooled 2000-2024', 'open_defecation_pop_pct', 'gdl_shdi'), 2), F(crv('change between surveys (first differences)', 'open_defecation_pop_pct', 'gdl_shdi'), 2)],
    ['Open defecation vs child diarrhoea', F(crv('pooled 2000-2024', 'open_defecation_pop_pct', 'child_diarrhoea_pct'), 2), F(crv('change between surveys (first differences)', 'open_defecation_pop_pct', 'child_diarrhoea_pct'), 2)],
], ['Pair (11 regions × 6 DHS rounds)', 'ρ across regions', 'ρ of change within regions'], num=(1, 2), cls='small')
t_corr3 = T([
    ['Annual rainfall vs a flood record that year', F(cyv('annual_mm', 'gam_flood_record'), 2)],
    ['Annual rainfall vs a drought record that year', F(cyv('annual_mm', 'gam_drought_record'), 2)],
    ['SPEI-12 (December) vs a drought record', F(cyv('spei12_dec_mean', 'gam_drought_record'), 2)],
    ['Year vs annual rainfall (trend)', F(cyv('year', 'annual_mm'), 2)],
], ['Gambela, 1981–2025 (n = 45 years)', 'ρ'], num=(1,), cls='small')

def ver(d, name):
    v = d.verified.value_counts(); return [name, F(len(d)), F(v.get('yes', 0)), F(v.get('no', 0)), F(v.get('not_checked', 0))]
t_ver = T([ver(ev, 'Flood/drought events'), ver(es, 'Economy & sanitation'), ver(sf, 'Safety / GBV'), ver(lit, 'Toilet–violence studies')],
          ['File', 'Rows', 'Confirmed', 'Wrong (kept, marked)', 'Not checked'], num=(1, 2, 3, 4), cls='small')
t_src = T([
    ['Sanitation, water, hygiene, diarrhoea, violence', 'DHS Program API — Ethiopia DHS 2000, 2005, 2011, 2016, 2019, 2024-25', 'region'],
    ['National GDP and GDP per capita', 'World Bank API (NY.GDP.*)', 'national'],
    ['Regional GNI per capita and HDI (modelled)', 'Global Data Lab, Subnational HDI database', 'region'],
    ['Gridded GDP (modelled)', 'Kummu et al., downscaled GDP per capita (Zenodo)', '5 arc-min'],
    ['Poverty headcount', 'National Planning Commission (2017) poverty report', 'region'],
    ['Flood and drought events', 'UN, Red Cross, IFRC GO, GDACS, Dartmouth Flood Observatory, peer-reviewed histories, news', 'event'],
    ['Ethiopia disaster counts', 'EM-DAT (CRED/UCLouvain) via Our World in Data', 'national'],
    ['Elevation and slope', 'Copernicus DEM GLO-90', '90 m'],
    ['Population', 'WorldPop 2020, 1 km, UN-adjusted', '1 km'],
    ['Soil texture and class', 'ISRIC SoilGrids 2.0 (clay, sand, silt; WRB class)', '250 m'],
    ['Rainfall, drought indices', 'CHIRPS v2.0 monthly (1981–2025); CHC SPEI-12', '5 km'],
    ['Flood extent', 'JRC Global Surface Water; JRC global river flood hazard maps (10- and 100-year)', '30 m – 90 m'],
    ['Boundaries, rivers', 'geoBoundaries 2016; OCHA COD-AB 2025; OpenStreetMap waterways', 'woreda'],
    ['Refugee camps', 'UNHCR camp figures (2022, 2026); OCHA/UNHCR camp points', 'camp'],
    ['Safety, GBV, latrine perception', 'UNHCR WASH KAP 2017; HVACS 2024; peer-reviewed studies via Europe PMC', 'camp / town'],
], ['Data', 'Source', 'Level'], cls='small')

# ---------------- CSS (white page, retro blue gradients)
CSS = r"""
@page{size:A4;margin:20mm 17mm 18mm 17mm;@top-left{content:'FLOODSAFE SANITATION GAMBELLA';font:600 7.5pt Bahnschrift,sans-serif;letter-spacing:.14em;color:#123a82}@top-right{content:'PROJECT PROPOSAL \B7  DRAFT';font:600 7.5pt Bahnschrift,sans-serif;letter-spacing:.14em;color:#3d8fe0}@bottom-left{content:'[Organisation name] \B7  Gambella data pack, November 2026';font:7pt 'Segoe UI',sans-serif;color:#5a6675}@bottom-right{content:counter(page);font:700 9pt Bahnschrift,sans-serif;color:#1e5bb8}}
@page cover{margin:0;@top-left{content:none}@top-right{content:none}@bottom-left{content:none}@bottom-right{content:none}}
:root{--navy:#0a1f4d;--deep:#123a82;--cobalt:#1e5bb8;--azure:#3d8fe0;--sky:#8cc3ff;--ice:#e3f0ff;--ink:#16202c;--muted:#5a6675;--line:#d6e2f0;--warn:#b5651d}
*{box-sizing:border-box}
html,body{margin:0;background:#fff;color:var(--ink);font:10.2pt/1.5 "Segoe UI",Arial,sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
h1,h2,h3,.disp{font-family:Bahnschrift,"Segoe UI",sans-serif;letter-spacing:.01em}
.run{position:fixed;top:-15mm;left:0;right:0;height:9mm;display:flex;align-items:center;justify-content:space-between;font:8pt Bahnschrift,sans-serif;color:var(--deep);text-transform:uppercase;letter-spacing:.12em}
.run:after{content:"";position:absolute;left:0;right:0;bottom:-2.2mm;height:2mm;background:linear-gradient(90deg,var(--navy),var(--cobalt) 35%,var(--azure) 60%,var(--sky) 85%,#fff);border-radius:2mm}
.foot{position:fixed;bottom:-12mm;left:0;right:0;font-size:7.5pt;color:var(--muted);display:flex;justify-content:space-between}
/* cover */
.cover{page:cover;height:297mm;width:210mm;position:relative;overflow:hidden;break-after:page;background:#fff}
.sun{position:absolute;left:50%;top:120mm;width:340mm;height:340mm;transform:translateX(-50%);border-radius:50%;
  background:repeating-conic-gradient(from -90deg,rgba(30,91,184,.10) 0 6deg,rgba(255,255,255,0) 6deg 12deg)}
.arcs{position:absolute;left:50%;transform:translateX(-50%);bottom:-205mm;width:330mm;height:330mm;border-radius:50%;
  background:radial-gradient(circle,#fff 0 34%,var(--sky) 34% 44%,#fff 44% 46%,var(--azure) 46% 56%,#fff 56% 58%,var(--cobalt) 58% 68%,#fff 68% 70%,var(--deep) 70% 80%,#fff 80% 82%,var(--navy) 82% 100%)}
.stripes{position:absolute;top:0;left:0;right:0;height:16mm;background:linear-gradient(180deg,var(--navy) 0 25%,#fff 25% 33%,var(--cobalt) 33% 58%,#fff 58% 66%,var(--sky) 66% 100%)}
.cover .inner{position:absolute;top:34mm;left:20mm;right:20mm}
.kicker{display:inline-block;font:600 9pt Bahnschrift,sans-serif;letter-spacing:.25em;text-transform:uppercase;color:#fff;background:linear-gradient(90deg,var(--navy),var(--cobalt));padding:2.2mm 5mm;border-radius:20mm}
.cover h1{font-size:44pt;line-height:.98;margin:9mm 0 4mm;color:var(--navy);text-transform:uppercase;font-weight:700}
.cover h1 span{background:linear-gradient(90deg,var(--cobalt),var(--azure));-webkit-background-clip:text;background-clip:text;color:transparent}
.cover .sub{font-size:14pt;color:var(--deep);max-width:150mm;line-height:1.35}
.cover .meta{margin-top:8mm;font-size:9.5pt;color:var(--muted)}
.cstats{position:absolute;top:138mm;left:20mm;right:20mm;display:grid;grid-template-columns:repeat(3,1fr);gap:5mm}
.cstat{background:#fff;border:1.2mm solid var(--ice);border-radius:6mm;padding:4mm 5mm;box-shadow:0 1mm 0 var(--sky)}
.cstat b{display:block;font:700 24pt/1 Bahnschrift,sans-serif;color:var(--cobalt)}
.cstat span{font-size:8.6pt;color:var(--muted)}
/* body */
.sec{break-before:page}
.sechead{display:flex;align-items:center;gap:5mm;margin:0 0 5mm;padding-bottom:3.5mm;background:linear-gradient(90deg,var(--navy),var(--cobalt) 35%,var(--azure) 60%,var(--sky) 85%,#fff) bottom/100% 1.6mm no-repeat}
.badge{flex:0 0 15mm;height:15mm;border-radius:50%;display:flex;align-items:center;justify-content:center;font:700 16pt Bahnschrift,sans-serif;color:#fff;
  background:radial-gradient(circle at 35% 30%,var(--azure),var(--cobalt) 55%,var(--navy));box-shadow:0 0 0 1.2mm #fff,0 0 0 2mm var(--sky)}
h2{font-size:21pt;margin:0;color:var(--navy);text-transform:uppercase;line-height:1}
h2 small{display:block;font:500 9pt "Segoe UI",sans-serif;color:var(--muted);text-transform:none;letter-spacing:0;margin-top:1.5mm}
h3{font-size:12.5pt;color:var(--deep);margin:6mm 0 2mm;text-transform:uppercase;letter-spacing:.04em}
h3:before{content:"";display:inline-block;width:7mm;height:2.2mm;margin-right:2.5mm;vertical-align:middle;border-radius:2mm;background:linear-gradient(90deg,var(--cobalt),var(--sky))}
p{margin:1.6mm 0 2.4mm;text-align:left}
ul{margin:1mm 0 3mm;padding-left:5mm}li{margin:1mm 0}
.mine{display:inline-block;font:600 6.8pt Bahnschrift,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--cobalt);border:.3mm solid var(--sky);border-radius:3mm;padding:.2mm 2mm;vertical-align:middle;margin-left:1.5mm}
.ph{background:var(--ice);color:var(--deep);padding:0 1.5mm;border-radius:1.2mm;font-style:italic}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:3.5mm;margin:3mm 0 4mm}
.kpis.k3{grid-template-columns:repeat(3,1fr)}
.kpi{border-radius:4mm;padding:3mm 3.5mm;background:linear-gradient(160deg,#fff 0 55%,var(--ice));border:.35mm solid var(--line);border-top:1.6mm solid var(--cobalt)}
.kpi:nth-child(2){border-top-color:var(--azure)}.kpi:nth-child(3){border-top-color:var(--sky)}.kpi:nth-child(4){border-top-color:var(--deep)}
.kpi b{display:block;font:700 17pt/1.05 Bahnschrift,sans-serif;color:var(--navy)}
.kpi span{font-size:8pt;color:var(--muted);line-height:1.3;display:block;margin-top:1mm}
.box{border-radius:4mm;padding:3.5mm 4.5mm;margin:3mm 0;background:var(--ice);border-left:1.6mm solid var(--cobalt)}
.box.warn{background:#fff6ec;border-left-color:var(--warn)}
.box h4{margin:0 0 1mm;font:700 9.5pt Bahnschrift,sans-serif;text-transform:uppercase;letter-spacing:.06em;color:var(--deep)}
.box.warn h4{color:var(--warn)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:6mm}
.cols3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4mm}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:8.6pt;margin:2mm 0 4mm;break-inside:auto}
th{background:linear-gradient(90deg,var(--navy),var(--cobalt));color:#fff;font:600 7.8pt Bahnschrift,sans-serif;letter-spacing:.04em;text-transform:uppercase;text-align:left;padding:1.8mm 2.2mm}
th:first-child{border-top-left-radius:2.5mm}th:last-child{border-top-right-radius:2.5mm}
td{padding:1.5mm 2.2mm;border-bottom:.25mm solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:#f5f9ff}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
table.small{font-size:7.8pt}table.small td{padding:1.1mm 1.8mm}
table.glance td:first-child{font-weight:600;color:var(--deep);width:42mm}
tr{break-inside:avoid}thead{display:table-header-group}
figure{margin:2mm 0 4mm;break-inside:avoid}
figure img{width:100%;display:block;border-radius:3mm;border:.3mm solid var(--line)}
figcaption{font-size:7.8pt;color:var(--muted);margin-top:1.2mm}
figure.half img{max-height:118mm;object-fit:contain}
.zone{border-radius:4mm;padding:3mm 4mm;color:#fff;break-inside:avoid}
.zone b{font:700 13pt Bahnschrift,sans-serif;display:block}
.zone p{margin:1mm 0;font-size:8.6pt}
.zA{background:linear-gradient(150deg,var(--navy),var(--cobalt))}.zB{background:linear-gradient(150deg,var(--cobalt),var(--azure))}
.zC{background:linear-gradient(150deg,#b28a49,#d9b26f);}.zD{background:linear-gradient(150deg,#6d5148,#8d6e63)}
.flow{display:flex;gap:2.5mm;margin:3mm 0 5mm;align-items:stretch}
.step{flex:1;border-radius:4mm;padding:3mm;background:#fff;border:.4mm solid var(--sky);position:relative;font-size:8pt}
.step b{display:block;font:700 9pt Bahnschrift,sans-serif;color:var(--cobalt);text-transform:uppercase;margin-bottom:1mm}
.step i{position:absolute;top:-3mm;left:3mm;background:linear-gradient(90deg,var(--navy),var(--azure));color:#fff;font:700 8pt Bahnschrift,sans-serif;font-style:normal;border-radius:3mm;padding:.3mm 2.5mm}
.phase{display:grid;grid-template-columns:32mm 1fr;gap:4mm;margin:2.5mm 0;break-inside:avoid}
.phase .ph-t{border-radius:4mm;padding:3mm;color:#fff;font:700 10pt Bahnschrift,sans-serif;text-transform:uppercase;background:linear-gradient(160deg,var(--navy),var(--azure))}
.phase .ph-t small{display:block;font:500 7.5pt "Segoe UI";text-transform:none;opacity:.9;margin-top:1mm}
.phase .ph-b{border:.35mm solid var(--line);border-radius:4mm;padding:2.5mm 4mm;font-size:8.8pt}
.toc{columns:2;column-gap:10mm;font-size:10pt}
.toc div{display:flex;gap:3mm;margin:1.6mm 0;break-inside:avoid}.toc b{color:var(--cobalt);font-family:Bahnschrift;width:8mm}
.endband{height:7mm;margin-top:8mm;border-radius:4mm;background:linear-gradient(90deg,var(--navy),var(--cobalt) 30%,var(--azure) 55%,var(--sky) 80%,var(--ice))}
.small{font-size:8.4pt}.muted{color:var(--muted)}
"""

def sec(n, title, sub, body):
    return f'<section class="sec"><div class="sechead"><div class="badge">{n}</div><h2>{title}<small>{sub}</small></h2></div>{body}</section>'

cover = f"""
<div class="cover"><div class="stripes"></div><div class="sun"></div><div class="arcs"></div>
<div class="inner">
<div class="kicker">Project proposal · draft</div>
<h1>FloodSafe<br><span>Sanitation</span><br>Gambella</h1>
<div class="sub">Flood- and drought-safe toilets for the people of the Gambela flood plain, western Ethiopia</div>
<div class="meta">Submitted by <span class="ph">[Organisation name]</span> · prepared from open data, November 2026 · version 1.0 (draft for discussion)</div>
</div>
<div class="cstats">
<div class="cstat"><b>{g24.open_defecation_pop_pct:.0f}%</b><span>of people in Gambela practise open defecation (DHS 2024) — no progress since 2016</span></div>
<div class="cstat"><b>{sh('100-year river flood covers >= 10% of cell'):.0f}%</b><span>of residents live where a 100-year river flood reaches</span></div>
<div class="cstat"><b>{refugees/1000:,.0f}k</b><span>registered refugees in Gambella (UNHCR, Oct 2026), many in flood-prone camps</span></div>
</div></div>"""

toc = '<div class="toc">' + ''.join(f'<div><b>{i}</b>{t}</div>' for i, t in enumerate([
    'Project at a glance', 'Executive summary', 'Problem: floods, drought and land', 'Problem: sanitation and health', 'Problem: safety of women and girls',
    'Economy and ability to pay', 'Target area and beneficiaries', 'Proposed solution', 'How the evidence was built', 'Implementation plan',
    'Monitoring and evaluation', 'Risks, safeguarding and sustainability', 'Budget framework', 'Limits of the evidence', 'Annexes'], 1)) + '</div>'

s1 = sec(1, 'Project at a glance', 'Summary sheet for reviewers', t_glance + '<h3>Contents</h3>' + toc +
         '<div class="box"><h4>How to read this proposal</h4>Every number comes from a named dataset in the project data pack (<code>gambella/data/</code>), with source, URL and year on each row. '
         'Labels mark what is not from a source: <span class="mine">own analysis</span> = calculations and interpretation by the project team; <span class="mine">team proposal</span> = planned activities and designs. '
         'Items in <span class="ph">[brackets]</span> are deliberately left open because no data exist yet.</div>')

s2 = sec(2, 'Executive summary', 'Why, where, what and how', f"""
<p>Gambela Region lies on the flat Baro–Akobo flood plain in western Ethiopia. {band45:.0f}% of residents live between 400 and 500 m, where the Baro, Gilo and Akobo rivers overflow most years. Floods were recorded in 20 of the years since 1961; in 2022 alone about <b>185,200 people were displaced</b>. The soils of the plain are mostly swelling Vertisol clays, which crack in the dry season and slump when wet.</p>
<p>Sanitation has stalled. Open defecation fell from 74% (2005) to 45% (2016) but has not moved since ({g24.open_defecation_pop_pct:.0f}% in 2024). Of households with on-site toilets, 97.2% have never emptied them, and in Gambella town nearly half of latrine owners still defecate in the open. Ordinary pit latrines flood, collapse or fill, and people return to the bush, where women and girls face violence: local studies find sexual or partner violence among 35–59% of women surveyed, and camp surveys report latrines without privacy, locks or separation for men and women.</p>
<p>We propose <b>FloodSafe Sanitation Gambella</b>: toilets matched to the ground they stand on. Using flood, soil, rainfall and population data we mapped four zones — <b>A</b> raised or sealed above-ground units where floods are frequent ({zp.get('A: raised / sealed above-ground unit',0)/1000:,.0f}k people), <b>B</b> raised slabs over lined pits on the flood edge ({zp.get('B: raised slab + lined pit',0)/1000:,.0f}k), <b>C</b> lined pits on clay with little river flooding ({zp.get('C: lined pit (clay), low flood',0)/1000:,.0f}k) and <b>D</b> site-specific designs on steep ground. Every unit has a lock, light, privacy screen and handwashing point, and is built and repaired by trained local masons. {MINE}</p>
<p>The first phase targets <b>Jikawo, Wantawo and Lare</b>, where nearly every resident lives in the top priority band and in zone A, plus one refugee camp. A site check and community consultation come before any construction, and the design is tested before it is scaled.</p>
<div class="kpis">
<div class="kpi"><b>{hp/1000:,.0f}k</b><span>residents in high-priority cells (score ≥ 0.6)</span></div>
<div class="kpi"><b>{len(rob)}</b><span>grid cells in the top 20% under every weighting tested ({rob.pop_2020.sum()/1000:,.0f}k people)</span></div>
<div class="kpi"><b>29</b><span>flood and drought events documented, 1961–2025</span></div>
<div class="kpi"><b>{int(eth.flood_events)}</b><span>flood disasters in Ethiopia recorded by EM-DAT since 1965</span></div>
</div>
<div class="box warn"><h4>What is not yet known</h4>Costs, the exact design of each unit, groundwater depth, and whether safety features reduce violence in Gambella have not been measured. The plan therefore starts with validation and a costed pilot rather than a full roll-out.</div>
""")

s3 = sec(3, 'The problem: floods, drought and land', 'Hazard maps built from satellite and model data', f"""
<p>We built a grid of 1,002 cells (0.05°, about 5.5 km) covering the region and attached elevation, slope, population, soil, rainfall, drought and flood data to each cell. {ANAL}</p>
{IMG('gambella_heatmap_panel.png', 'Elevation, population density, two drought measures, dry-season length and 100-year river flood extent. Star = Gambela town; triangles = refugee camps; lines = woredas.')}
""") + f"""<section><h3>What the maps show {ANAL}</h3><ul>
<li><b>Flood, not drought, is the hazard where people live.</b> {sh('100-year river flood covers >= 10% of cell'):.0f}% of residents live in cells where a 100-year river flood covers at least a tenth of the cell; {sh('100-year river flood covers >= 50% of cell'):.0f}% where it covers half or more.</li>
<li><b>Lower ground floods.</b> Elevation and flood extent are strongly negatively correlated (ρ = {cgv('elev_mean_m','jrc_rp100_flooded_pct'):.2f} across cells).</li>
<li><b>Drought means a long dry season more than failed years.</b> The plain has about five months under 30 mm of rain a year (dry months vs elevation ρ = {cgv('elev_mean_m','chirps_dry_months_lt30mm_mean'):.2f}), but years with rain under 80% of normal are rare (0–18% of years) and fall mainly in the thinly populated south.</li>
<li><b>Swelling clay underfoot.</b> {sh('Vertisols (swelling clay) dominant'):.0f}% of residents live on Vertisols; {sh('100-year flood >= 50% AND Vertisols'):.0f}% on Vertisols that are also at least half covered by the 100-year flood.</li>
<li><b>Rain is rising.</b> Annual rainfall has increased since 1981 (year vs rain ρ = {cyv('year','annual_mm'):.2f}), and wetter years are much more likely to bring a recorded flood (ρ = {cyv('annual_mm','gam_flood_record'):.2f}).</li></ul>
<div class="cols">{IMG('map_soil_class.png','Dominant soil group (SoilGrids 2.0).','half')}{IMG('scatter_elevation.png','Each dot is a grid cell: elevation against density, drought and flood.','half')}</div>
<h3>Documented disasters</h3>
<p>We found 29 flood and drought events for Gambella from 1961 to 2025, from UN, Red Cross, GDACS, Dartmouth Flood Observatory, peer-reviewed and news sources (full list in Annex B). The largest, in August–October 2022, displaced about 185,200 people and damaged 72% of cropland; 250–270 water schemes stopped working. In 2014 latrines in Leitchuor refugee camp overflowed and some collapsed. No Gambella-specific drought impact figure was found after 2002.</p></section>"""

s4 = sec(4, 'The problem: sanitation and health', 'Toilet coverage, use and disease', f"""
<div class="kpis">
<div class="kpi"><b>{g24.open_defecation_pop_pct:.0f}%</b><span>open defecation, 2024 (DHS) — {g16.open_defecation_pop_pct:.0f}% in 2016</span></div>
<div class="kpi"><b>97.2%</b><span>of on-site toilets never emptied (DHS 2024)</span></div>
<div class="kpi"><b>47.2%</b><span>of latrine-owning households in Gambella town still defecate in the open (peer-reviewed, 2023)</span></div>
<div class="kpi"><b>2,194</b><span>cholera cases and 32 deaths, January–May 2025</span></div>
</div>
<h3>Gambela over time</h3>{t_san}
<div class="cols"><div><h3>Compared with other regions</h3>{t_p19}<p class="small">In 2019 Gambela had the 4th-highest open defecation of 11 regions despite middling modelled income and HDI.</p></div>
<div><h3>Refugee camps</h3><ul class="small">
<li>6 to 64 people per latrine across Gambella camps and sites (UNHCR, 2015–2026).</li>
<li>37% of refugee families had a household toilet in 2019; 28% had access in 2020.</li>
<li>Household latrine coverage of 24% in one camp (2019).</li>
<li>No latrine attendants at the 2026 emergency sites.</li></ul>
<h3>Income is not the answer {ANAL}</h3><p class="small">Across regions, richer means better toilets (ρ = {crv('pooled 2000-2024','improved_sanitation_pop_pct','gdl_gni_pc_ppp2017'):.2f}). But within a region, income growth does not predict sanitation gains (ρ = {abs(crv('change between surveys (first differences)','improved_sanitation_pop_pct','gdl_gni_pc_ppp2017')):.2f}). Gambela's income rose while open defecation stood still: design, maintenance and use matter, not only money.</p></div></div>
{IMG('panel_sanitation_income_rain.png','Left: open defecation per region (red = Gambela). Middle: open defecation vs modelled GNI per capita. Right: Gambela rainfall anomaly with flood and drought records.')}
""")

s5 = sec(5, 'The problem: safety of women and girls', 'Violence, privacy and night-time toilet use', f"""
<p>Where toilets are missing, unsafe or far away, women and girls go to the bush, often after dark. In Gambela's camps and town, violence against women is common and rarely reported.</p>
{t_safety}
<h3>Evidence from other countries</h3>
<p>Studies elsewhere link open-air or shared toilets to higher odds of non-partner sexual violence. No study has measured this in Gambella, so the safety features below are justified by this wider evidence and by camp surveys, and will be tested in the pilot.</p>
{t_lit}
<div class="box warn"><h4>Read with care</h4>Figures use different definitions and recall periods and cannot be compared directly. DHS violence data are known to undercount; local studies sample high-risk groups. The Pugnido II survey reports 71% safe and 13% unsafe without explaining the remaining 16%.</div>
""")

wb = es[(es.admin_level == 'national') & (es.indicator == 'GDP per capita (current US$)')].copy(); wb['y'] = pd.to_numeric(wb.year, errors='coerce')
wbr = [[int(r.y), F(float(r.value))] for _, r in wb[wb.y.isin([2000, 2010, 2015, 2020, 2024])].sort_values('y').iterrows()]
s6 = sec(6, 'Economy and ability to pay', 'What households and the region can afford', f"""
<div class="cols"><div>
<p>No official regional GDP exists for Gambela. The best available figures are national accounts and modelled regional estimates.</p>
{T(wbr, ['Year', 'Ethiopia GDP per capita, current US$ (World Bank)'], num=(1,), cls='small')}
<ul class="small"><li>Regional poverty headcount (national line): 50.5% (1999/00), 32% (2010/11), 23.0% (2015/16) — National Planning Commission.</li>
<li>Modelled GNI per capita (Global Data Lab, 2017 PPP $): {gam.gdl_gni_pc_ppp2017.iat[0]:,.0f} in 2000, {g24.gdl_gni_pc_ppp2017:,.0f} in 2023.</li>
<li>{F(g24.lowest_wealth_quintile_pop_pct)}% of Gambela's population is in Ethiopia's poorest wealth quintile (DHS 2024).</li></ul>
</div><div>
<div class="box"><h4>Implications for financing {MINE}</h4>
<ul class="small"><li>Most households cannot pay the full cost of a raised or sealed toilet up front; plan for savings groups, instalments and subsidies for the poorest.</li>
<li>Landlords and camp operators (UNHCR and its WASH partners) should pay for shared and camp units.</li>
<li>Local masons earn from building and repairs, which keeps maintenance going after the project.</li>
<li>Exact prices are unknown: the pilot must record the real cost of each zone's unit.</li></ul></div>
</div></div>
""")

s7 = sec(7, 'Target area and beneficiaries', 'Where a flood- and drought-safe toilet helps most', f"""
<p>No village-level toilet data exist, so we ranked places by how many people live where ordinary pit latrines are most likely to fail. {ANAL}</p>
<div class="box"><h4>Priority score</h4>priority = population rank × (0.50 × flood rank + 0.25 × clay-soil rank + 0.25 × dry-season rank), scaled 0–1. Cells with fewer than 2 people per km² are excluded. The result was recomputed under three other weightings (flood only, equal, water-scarcity heavy); {len(rob)} cells holding {rob.pop_2020.sum():,.0f} people stay in the top 20% under all four.</div>
{IMG('sanitation_priority.png','Left: priority score. Right: toilet type suited to the ground (zones A–E). Circles = refugee camps sized by registered refugees.')}
""") + f"""<section><h3>Priority by woreda</h3>{t_wor}
<div class="cols"><div><h3>Refugee camps</h3>{t_camps}<p class="small">WorldPop counts only a few hundred to a few thousand people in camp cells, so camps rank too low in the score; they are treated as a separate priority group. The river-flood model also leaves out flooding from heavy rain, which affected camps in 2014.</p></div>
<div>{IMG('sanitation_priority_robustness.png','Cells in the top 20% under 4 weightings.')}</div></div>
<h3>Proposed first-phase beneficiaries {MINE}</h3>
<ul><li><b>Jikawo, Wantawo and Lare woredas</b>: {spw.set_index('woreda').loc[['Jikawo','Wantawo','Lare'],'people'].sum():,.0f} residents, {spw.set_index('woreda').loc[['Jikawo','Wantawo','Lare'],'people_high_priority'].sum():,.0f} in high-priority cells, almost all zone A.</li>
<li><b>One refugee camp</b> chosen with UNHCR and the Refugees and Returnees Service, for comparison with a camp setting.</li>
<li>Number of households per pilot village: <span class="ph">[set after site check and costing]</span>.</li></ul></section>"""

s8 = sec(8, 'Proposed solution', 'A toilet matched to the ground it stands on', f"""
<p>Instead of one standard latrine, the project offers four designs. A site check decides which one a household gets. {MINE}</p>
<div class="cols">
<div class="zone zA"><b>Zone A · Raised / sealed unit</b><p>Where a 10-year flood covers ≥30% or a 100-year flood ≥50% of the area. Above-ground sealed chamber or two-chamber box on a raised plinth above the worst remembered flood; no open pit.</p><p>{zp.get('A: raised / sealed above-ground unit',0):,.0f} people</p></div>
<div class="zone zB"><b>Zone B · Raised slab + lined pit</b><p>Flood edge (100-year flood 10–50%). Fully lined pit, slab and squat hole raised above flood level, sealed lid for the flood season.</p><p>{zp.get('B: raised slab + lined pit',0):,.0f} people</p></div>
<div class="zone zC"><b>Zone C · Lined pit on clay</b><p>Little river flooding but swelling clay. Lining that tolerates ground movement; dry or low-water design for the five-month dry season.</p><p>{zp.get('C: lined pit (clay), low flood',0):,.0f} people</p></div>
<div class="zone zD"><b>Zone D · Steep ground</b><p>Slopes of 8° or more in the eastern highlands. Design chosen on site (drainage, erosion, access).</p><p>{zp.get('D: steep ground, site-specific',0):,.0f} people</p></div>
</div>
<h3>Features in every unit {MINE}</h3>
<div class="cols3 small">
<div class="box"><h4>Safety</h4>Inside lock, solar light, solid walls and door, separate women's units where shared, placed close to the home and away from paths used at night.</div>
<div class="box"><h4>Health</h4>Handwashing point with water store, screened vent, fly-proof lid, cover material store, safe emptying route.</div>
<div class="box"><h4>Resilience</h4>Plinth above the design flood (worst remembered flood marked on a fixed point), anchored shelter, flood-season seal, pre-rain emptying check.</div>
</div>
<h3>Around the toilet {MINE}</h3>
<ul><li><b>Site check before building</b>: flood marks, soil, distance to wells, ownership, nearest high ground. No pit where groundwater or soil makes it unsafe.</li>
<li><b>Local masons</b> trained to build and repair every design, paid per unit and per repair.</li>
<li><b>Early warning without power</b>: groundwater gauge and colour pegs (green/yellow/red) beside the toilet; a forecast alert moves households to "yellow"; a local helper passes on warnings.</li>
<li><b>Emergency pack and high-ground swap point</b> for long floods, when toilets cannot be used.</li>
<li><b>Behaviour and use</b>: household visits and school sessions; people chose why they use or avoid toilets in the baseline survey.</li></ul>
<div class="box warn"><h4>Honest limits</h4>No toilet can be used under water; the plan covers what households do during long floods. Raised and lined latrines already exist elsewhere in East Africa; the gauge, sealed unit, lining and forecast rule are untested in Gambela.</div>
""")

s9 = sec(9, 'How the evidence was built', 'Data, methods and checks', f"""
<div class="flow">
<div class="step"><i>1</i><b>Collect</b>Download open data from 15+ sources; save every file and download log.</div>
<div class="step"><i>2</i><b>Extract</b>Turn reports into rows with a quote, source, URL and year; no gap filled with guesses.</div>
<div class="step"><i>3</i><b>Grid</b>Combine rasters on 1,002 cells of 0.05°; zonal statistics per woreda.</div>
<div class="step"><i>4</i><b>Analyse</b>Rank correlations, exposure counts, priority score, zones.</div>
<div class="step"><i>5</i><b>Verify</b>An independent checker re-opened sources and recomputed cells.</div>
</div>
<h3>Data sources</h3>{t_src}
<div class="cols"><div><h3>Methods</h3><ul class="small">
<li>Correlations are Spearman rank correlations. Grid p-values use 0.25° blocks because neighbouring cells are not independent.</li>
<li>Cross-region analysis uses 11 regions × 6 DHS rounds; "within-region change" removes the common trend.</li>
<li>Drought: share of years with rain below 80% of each cell's mean, SPI-3 (June–August), SPEI-12 and dry months under 30 mm.</li>
<li>Flood: JRC 10- and 100-year river flood extent and depth; surface water seen 1984–2021.</li>
<li>Exposure = WorldPop 2020 population summed over cells meeting each condition.</li></ul></div>
<div><h3>Verification</h3>{t_ver}<p class="small">Errors found and fixed: 2007 flood figures (an Ethiopia-wide record and a five-region total had been attributed to Gambella), a population grid offset of 0.1°, and one literature effect size.</p></div></div>
""")

s10 = sec(10, 'Implementation plan', 'Validate, pilot, learn, then scale', f"""
<p>Durations and dates are to be agreed with partners and funders. {MINE}</p>
<div class="phase"><div class="ph-t">Phase 0<small>Validate</small></div><div class="ph-b">Community consultation in pilot villages; site checks (flood marks, soil pits, wells); baseline household survey including toilet use and safety; confirm zones on the ground; agree roles with woreda offices, health extension workers, UNHCR and the Refugees and Returnees Service.</div></div>
<div class="phase"><div class="ph-t">Phase 1<small>Design &amp; cost</small></div><div class="ph-b">Prototype each zone's unit with local masons and materials; record real costs; flood-test the sealed unit and lining; set the design flood margin with a civil engineer.</div></div>
<div class="phase"><div class="ph-t">Phase 2<small>Pilot</small></div><div class="ph-b">Build in Jikawo, Wantawo and Lare and one camp; train masons and local helpers; set up savings groups and payment options; install gauges and pegs; run the first flood season.</div></div>
<div class="phase"><div class="ph-t">Phase 3<small>Evaluate</small></div><div class="ph-b">Repeat the household survey; compare pilot and comparison villages; review damage after the flood season, cost per household and use by women and girls; publish results, including failures.</div></div>
<div class="phase"><div class="ph-t">Phase 4<small>Scale</small></div><div class="ph-b">Extend to Akobo, Itang and remaining zone A/B areas only if the pilot meets its targets; hand over training and repair to local masons and woreda health offices.</div></div>
<h3>Partners to involve <span class="ph">[to be confirmed]</span></h3>
<ul class="small"><li>Gambela regional health and water bureaus; woreda administrations; health extension workers.</li><li>UNHCR, the Refugees and Returnees Service and camp WASH partners.</li><li>Local masons, women's groups and savings groups.</li><li>A university partner for monitoring and the flood and soil tests.</li></ul>
""")

s11 = sec(11, 'Monitoring and evaluation', 'Indicators with baselines from the data pack', T([
    ['Open defecation, % of population', f'{g24.open_defecation_pop_pct:.1f}% (region, DHS 2024)', 'Household survey, pilot vs comparison', '[to be set]'],
    ['Improved sanitation, % of population', f'{g24.improved_sanitation_pop_pct:.1f}% (region, DHS 2024)', 'Household survey', '[to be set]'],
    ['Latrine owners who still defecate in the open', '47.2% (Gambella town, 2023)', 'Household survey, observation', '[to be set]'],
    ['Toilets usable after the flood season', 'No baseline', 'Post-flood inspection of every unit', '[to be set]'],
    ['On-site toilets never emptied', '97.2% (region, DHS 2024)', 'Inspection, mason records', '[to be set]'],
    ['People per latrine in the pilot camp', '6–64 (UNHCR, 2015–2026)', 'Camp WASH monitoring', 'SPHERE standard ≤ 20'],
    ['Women and girls who feel unsafe using the toilet', '13% (Pugnido II, 2017)', 'Survey with female enumerators', '[to be set]'],
    ['Adults defecating in the bush at night', '7–12% (4 camps, 2017)', 'Survey', '[to be set]'],
    ['Child diarrhoea, past 2 weeks', f'{g24.child_diarrhoea_pct:.1f}% (region, DHS 2024)', 'Survey; health post records', '[to be set]'],
    ['Cost per household by zone', 'Unknown', 'Project accounts', 'Recorded in Phase 1'],
    ['Trained masons still working after 12 months', 'None yet', 'Follow-up', '[to be set]'],
], ['Indicator', 'Baseline (source)', 'How measured', 'Target']) + f"""
<p class="small">Targets are left open until the baseline survey; regional DHS values are context, not a village baseline. Surveys on violence follow WHO safety and ethics guidance (trained female enumerators, private interviews, referral to services). {MINE}</p>""")

s12 = sec(12, 'Risks, safeguarding and sustainability', 'What could go wrong and how we respond', T([
    ['A flood larger than the design flood', 'Plinth margin set with an engineer; emergency pack and high-ground swap point; post-flood repair fund'],
    ['Swelling clay cracks linings', 'Test linings in Phase 1; choose flexible joints; masons trained to repair'],
    ['Households build but do not use toilets', 'Design with users; women choose placement; follow-up visits; measure use, not only numbers built'],
    ['Costs too high for poor households', 'Savings groups, instalments, targeted subsidy; record real costs before scaling'],
    ['Conflict and insecurity in parts of the region', 'Work through local partners; flexible schedule; do-no-harm review'],
    ['Data gaps (groundwater, latrine-level data)', 'Site checks and baseline survey fill gaps before building'],
    ['Survey on violence causes harm', 'Ethics approval, trained female enumerators, referral pathways, no names stored with answers'],
], ['Risk', 'Response']) + f"""
<div class="cols"><div class="box"><h4>Gender and inclusion</h4><ul class="small"><li>Women and girls take part in choosing designs and locations.</li><li>Accessible units for older and disabled people where needed.</li><li>Safety features (lock, light, separation) are part of every design, not an add-on.</li><li>Female masons and helpers are recruited where possible.</li></ul></div>
<div class="box"><h4>Sustainability</h4><ul class="small"><li>Local masons keep building and repairing after the project.</li><li>Payment through savings groups builds ownership.</li><li>Woreda health offices take over monitoring.</li><li>Designs and costs are published so others can copy them.</li></ul></div></div>
<p class="small">{MINE}</p>""")

s13 = sec(13, 'Budget framework', 'Cost lines — amounts to be filled after costing', T([
    ['1', 'Site checks, community consultation, baseline survey', '[to be costed]'],
    ['2', 'Prototype design, materials testing, engineering advice', '[to be costed]'],
    ['3', 'Toilet units — zone A (raised / sealed)', '[to be costed per unit × number of households]'],
    ['4', 'Toilet units — zone B (raised slab + lined pit)', '[to be costed]'],
    ['5', 'Safety features: locks, solar lights, women\'s units', '[to be costed]'],
    ['6', 'Mason and local helper training, tools', '[to be costed]'],
    ['7', 'Early-warning gauges, pegs, emergency packs, swap point', '[to be costed]'],
    ['8', 'Behaviour and hygiene activities', '[to be costed]'],
    ['9', 'Monitoring, evaluation and endline survey', '[to be costed]'],
    ['10', 'Staff, transport, management and overheads', '[to be costed]'],
    ['11', 'Contingency for flood damage and price changes', '[to be costed]'],
], ['#', 'Line', 'Amount']) + """
<div class="box warn"><h4>Why no figures</h4>No cost data for these designs in Gambella were found. Inventing amounts would mislead funders; Phase 1 exists to produce them.</div>""")

s14 = sec(14, 'Limits of the evidence', 'What this proposal cannot yet show', """
<ul>
<li><b>No village-level toilet data.</b> DHS gives one value for the whole region; the priority map shows where pits are likely to fail, not where toilets are missing.</li>
<li><b>Refugees are missing from the population map.</b> WorldPop counts only a few thousand people in camp cells holding 10,000–110,000 refugees.</li>
<li><b>Flood maps are global models.</b> The JRC map covers river floods only, not flooding from heavy rain on flat clay; it has not been checked against local flood marks.</li>
<li><b>Groundwater depth was not found</b> in any dataset; it decides whether a pit is safe and must be measured on site.</li>
<li><b>Regional income is modelled.</b> There is no official regional GDP; the two modelled population series also disagree (480,000 vs 610,000 in 2022).</li>
<li><b>Disaster records are incomplete.</b> ReliefWeb/OCHA and government disaster sites could not be accessed; years without a record may still have had floods; some figures (2019, 2021, 2024) are disputed between sources.</li>
<li><b>Violence data are not comparable</b> across studies and are likely undercounts; no study measures violence linked to latrines in Gambella.</li>
<li><b>Correlations show association, not cause.</b></li>
</ul>""")

annex = sec('A', 'Annexes', 'Correlations, disaster list and files', f"""
<h3>Annex A · Correlation results {ANAL}</h3>{t_corr}{t_corr2}{t_corr3}
<h3>Annex B · Flood and drought events, Gambella 1961–2025</h3>
<p class="small">One row per event; "affected" and "displaced" show the largest figure among the sources that passed checking. Definitions differ between sources and years.</p>{t_events}
<h3>Annex C · Data pack</h3>
<p class="small">Folder <code>OneDrive/Research/gambella/</code>: <code>data/</code> (CSV files with source, URL, year and a <code>verified</code> flag on each row), <code>maps/</code>, <code>scripts/</code> (rebuild every number), <code>raw/</code> (downloaded files), <code>README.md</code>, and an interactive version of this analysis in <code>Gambella_data_report.html</code>. EM-DAT data are for non-commercial use; only aggregated counts are published.</p>
<div class="endband"></div>""")

doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>FloodSafe Sanitation Gambella — project proposal</title><style>{CSS}</style></head><body>
{cover}{s1}{s2}{s3}{s4}{s5}{s6}{s7}{s8}{s9}{s10}{s11}{s12}{s13}{s14}{annex}
</body></html>"""
doc = doc.replace('[to be set]', '<span class="ph">[to be set]</span>').replace('[to be costed', '<span class="ph">[to be costed').replace('costed]', 'costed]</span>').replace('households]', 'households]</span>')
edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
def render(html_doc, name):
    h = OUT + name + '.html'; f = OUT + name + '.pdf'
    open(h, 'w', encoding='utf-8').write(html_doc)
    subprocess.run([edge, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--run-all-compositor-stages-before-draw', '--virtual-time-budget=8000',
                    f'--print-to-pdf={f}', 'file:///' + h.replace(chr(92), '/')], check=True, timeout=180)
    return h, f
cover_doc = doc.replace(cover, '').split('<body>')[0] + '<body>' + cover + '</body></html>'
cover_doc = cover_doc.replace('</style>', '@page{size:A4;margin:0}html,body{width:210mm;height:297mm;overflow:hidden}</style>')
body_doc = doc.replace(cover, '')
_, fc = render(cover_doc, '_cover'); hb, fb = render(body_doc, '_body')
from pypdf import PdfReader, PdfWriter
w = PdfWriter(); w.add_page(PdfReader(fc).pages[0])
for pg in PdfReader(fb).pages: w.add_page(pg)
w.add_metadata({'/Title': 'FloodSafe Sanitation Gambella - project proposal (draft)', '/Subject': 'Flood- and drought-safe toilets, Gambela Region, Ethiopia'})
pdf = OUT + 'FloodSafe_Sanitation_Gambella_proposal.pdf'
with open(pdf, 'wb') as fh: w.write(fh)
open(OUT + 'FloodSafe_Sanitation_Gambella_proposal.html', 'w', encoding='utf-8').write(doc)
for x in (fc, fb, OUT + '_cover.html', OUT + '_body.html'): os.remove(x)
print('pages', len(PdfReader(pdf).pages), 'size KB', os.path.getsize(pdf) // 1024)
