"""Build a single self-contained HTML report (images embedded) from the Gambella data files.
Usage: python an03_build_report.py <gambella root>   ->  <root>/Gambella_data_report.html
Numbers in tables are read from the CSVs; prose summaries are Claude's own analysis (2026-11-16)."""
import sys, base64, html, re
import numpy as np, pandas as pd

R = sys.argv[1].rstrip('/') + '/'
rd = lambda f: pd.read_csv(R + 'data/' + f, encoding='utf-8-sig', low_memory=False)
esc = lambda s: html.escape('' if pd.isna(s) else str(s))
def img(name, alt):
    b = base64.b64encode(open(R + 'maps/' + name, 'rb').read()).decode()
    return f'<figure><img src="data:image/png;base64,{b}" alt="{esc(alt)}" loading="lazy"><figcaption>{esc(alt)}</figcaption></figure>'
def fmt(v, d=1):
    if pd.isna(v): return '–'
    if isinstance(v, (int, np.integer)): return f'{v:,}'
    if isinstance(v, (float, np.floating)):
        return f'{v:,.0f}' if abs(v) >= 1000 or float(v).is_integer() else f'{v:,.{d}f}'
    return esc(v)
def table(df, cols, heads=None, num=(), cls=''):
    heads = heads or cols
    h = ''.join(f'<th class="{"n" if c in num else ""}">{esc(x)}</th>' for c, x in zip(cols, heads))
    rows = ''.join('<tr>' + ''.join(f'<td class="{"n" if c in num else ""}">{fmt(r[c]) if c in num else esc(r[c])}</td>' for c in cols) + '</tr>' for _, r in df.iterrows())
    return f'<div class="tw {cls}"><table><thead><tr>{h}</tr></thead><tbody>{rows}</tbody></table></div>'
def badge(v):
    return {'yes': '✓ yes', 'no': '✗ no', 'not_checked': '· not checked'}.get(str(v), esc(v))

# ---------- data
ex = rd('population_exposure.csv'); wh = rd('gambella_woreda_hazard.csv'); cg = rd('correlations_grid.csv')
pn = rd('ethiopia_regions_panel.csv'); cr = rd('correlations_regions.csv'); cy = rd('correlations_yearly.csv')
ev = rd('gambella_flood_drought_events.csv'); sf = rd('gambella_safety_gbv.csv'); lit = rd('sanitation_violence_literature.csv')
es = rd('gambella_economy_sanitation.csv'); bands = rd('gambella_elevation_bands.csv'); camps = rd('gambella_refugee_camps.csv')
ey = rd('ethiopia_flood_drought_yearly.csv')

def c(x, y, df=cg, col='spearman_cells'):
    r = df[((df.var_x == x) & (df.var_y == y)) | ((df.var_x == y) & (df.var_y == x))]
    return r[col].iat[0]
def cs(sample, x, y):
    r = cr[(cr['sample'] == sample) & (((cr.var_x == x) & (cr.var_y == y)) | ((cr.var_x == y) & (cr.var_y == x)))]
    return r.spearman.iat[0], r.n.iat[0]
def cyr(x, y, s='1981-2025'):
    r = cy[(cy['sample'] == s) & (cy.var_x == x) & (cy.var_y == y)]; return r.spearman.iat[0], r.p.iat[0]

P = ex.loc[ex.group == 'all cells', 'population_worldpop_2020'].iat[0]
sh = lambda g: ex.loc[ex.group == g, 'share_population'].iat[0] * 100
band45 = bands.loc[bands.band_m == '400-500', 'share_population'].iat[0] * 100
gam = pn[pn.region == 'Gambela'].sort_values('year')

# ---------- verification counts
ver = []
for f, d in [('Flood/drought events', ev), ('Economy & sanitation', es), ('Safety / GBV', sf), ('Toilet–violence studies', lit)]:
    vc = d.verified.value_counts()
    ver.append(dict(file=f, rows=len(d), yes=int(vc.get('yes', 0)), no=int(vc.get('no', 0)), nc=int(vc.get('not_checked', 0))))
ver = pd.DataFrame(ver)

# ---------- tables
exp_t = ex[ex.group != 'all cells'].assign(share_area=lambda d: d.share_area * 100, share_population=lambda d: d.share_population * 100)
exp_html = table(exp_t, ['group', 'area_km2', 'share_area', 'population_worldpop_2020', 'share_population'],
                 ['Group of grid cells', 'Area km²', '% of area', 'People (WorldPop 2020)', '% of people'],
                 num=('area_km2', 'share_area', 'population_worldpop_2020', 'share_population'))
wh_t = wh.sort_values('pop_weighted_flood_rp100_pct', ascending=False)
wh_html = table(wh_t, ['woreda', 'pop_2020', 'elev_mean_m', 'rain_mean_mm', 'dry_months', 'years_below80pct_share', 'flood_rp100_area_pct', 'pop_weighted_flood_rp100_pct', 'clay_15_30', 'dominant_soil'],
                ['Woreda', 'People', 'Elevation m', 'Rain mm/yr', 'Dry months', '% yrs rain <80%', '100-yr flood % area', '100-yr flood % people', 'Clay %', 'Soil'],
                num=('pop_2020', 'elev_mean_m', 'rain_mean_mm', 'dry_months', 'years_below80pct_share', 'flood_rp100_area_pct', 'pop_weighted_flood_rp100_pct', 'clay_15_30'))
LAB = {'elev_mean_m': 'Elevation', 'pop_density_km2': 'Population density', 'chirps_mean_annual_mm': 'Mean annual rain', 'chirps_dry_months_lt30mm_mean': 'Dry months/yr',
       'chirps_share_years_below80pct': 'Years with rain <80% of normal', 'spei12_share_months_le_m1': 'Months SPEI-12 ≤ −1', 'jrc_rp100_flooded_pct': '100-yr flood area',
       'jrc_rp10_flooded_pct': '10-yr flood area', 'gsw_occ_ge1_pct': 'Surface water seen', 'clay_15_30': 'Clay 15–30 cm', 'slope_mean_deg': 'Slope', 'dist_to_river_km': 'Distance to river',
       'chirps_cv_annual_pct': 'Rain variability (CV)'}
key = cg[cg.var_x.isin(['elev_mean_m']) | (cg.var_x == 'pop_density_km2') | (cg.var_y == 'pop_density_km2')].copy()
key['x'] = key.var_x.map(LAB); key['y'] = key.var_y.map(LAB)
cg_html = table(key, ['x', 'y', 'spearman_cells', 'spearman_blocks_025deg', 'p_blocks'], ['Variable', 'vs', 'ρ (1,002 cells)', 'ρ (0.25° blocks)', 'p (blocks)'],
                num=('spearman_cells', 'spearman_blocks_025deg'))
gam_html = table(gam, ['year', 'open_defecation_pop_pct', 'improved_sanitation_pop_pct', 'basic_sanitation_pop_pct', 'child_diarrhoea_pct', 'households_electricity_pct', 'gdl_gni_pc_ppp2017', 'gdl_shdi'],
                 ['DHS year', 'Open defecation %', 'Improved sanitation %', 'Basic sanitation %', 'Child diarrhoea %', 'Electricity %', 'GNI/cap 2017 PPP$ (GDL)', 'Sub-national HDI'],
                 num=('open_defecation_pop_pct', 'improved_sanitation_pop_pct', 'basic_sanitation_pop_pct', 'child_diarrhoea_pct', 'households_electricity_pct', 'gdl_gni_pc_ppp2017', 'gdl_shdi'))
p19 = pn[pn.year == 2019].sort_values('open_defecation_pop_pct', ascending=False)
p19_html = table(p19, ['region', 'open_defecation_pop_pct', 'improved_sanitation_pop_pct', 'gdl_gni_pc_ppp2017', 'gdl_shdi'],
                 ['Region (2019)', 'Open defecation %', 'Improved sanitation %', 'GNI/cap', 'HDI'], num=('open_defecation_pop_pct', 'improved_sanitation_pop_pct', 'gdl_gni_pc_ppp2017', 'gdl_shdi'), cls='narrow')
rows = []
for x, y, lab in [('open_defecation_pop_pct', 'gdl_gni_pc_ppp2017', 'Open defecation vs GNI per capita'), ('improved_sanitation_pop_pct', 'gdl_gni_pc_ppp2017', 'Improved sanitation vs GNI per capita'),
                  ('open_defecation_pop_pct', 'gdl_shdi', 'Open defecation vs HDI'), ('open_defecation_pop_pct', 'child_diarrhoea_pct', 'Open defecation vs child diarrhoea'),
                  ('open_defecation_pop_pct', 'lowest_wealth_quintile_pop_pct', 'Open defecation vs share in poorest quintile')]:
    a, n1 = cs('pooled 2000-2024', x, y); b, n2 = cs('change between surveys (first differences)', x, y)
    rows.append(dict(pair=lab, pooled=a, n1=n1, fd=b, n2=n2))
cr_html = table(pd.DataFrame(rows), ['pair', 'pooled', 'n1', 'fd', 'n2'], ['Pair', 'ρ across regions × years', 'n', 'ρ of change within a region', 'n'], num=('pooled', 'n1', 'fd', 'n2'))

evs = ev[~ev.event_id.str.startswith('GAP')].copy()
evs['year'] = evs.year.astype('Int64'); evs['verified'] = evs.verified.map(badge)
evs['source'] = evs.source.str.slice(0, 90)
ev_html = table(evs.sort_values(['year', 'event_id']), ['year', 'event_type', 'woredas_or_places', 'people_affected', 'people_displaced', 'deaths', 'source', 'source_type', 'verified'],
                ['Year', 'Type', 'Places', 'Affected', 'Displaced', 'Deaths', 'Source', 'Source type', 'Checked'], cls='scroll')
eth = ey[['flood_events', 'drought_events', 'flood_total_affected', 'drought_total_affected']].sum()

sfv = sf[~sf.value.astype(str).isin(['NOT FOUND', 'NOT ACCESSED', 'qualitative'])].copy()
sfv['indicator'] = sfv.indicator.str.replace(r'\s*\[[A-Z0-9_]+\]', '', regex=True)
sfv['year'] = sfv.year.apply(lambda v: '' if pd.isna(v) else str(int(float(v))) if re.match(r'^\d+(\.0)?$', str(v)) else str(v))
sfv['verified'] = sfv.verified.map(badge)
sf_html = table(sfv, ['indicator', 'value', 'unit', 'year', 'geography', 'disaggregation', 'measure_type', 'source_type', 'verified'],
                ['Indicator', 'Value', 'Unit', 'Year', 'Where', 'Who', 'Measure', 'Source type', 'Checked'], cls='scroll')
qual = sf[sf.value.astype(str) == 'qualitative']
qual_html = ''.join(f'<li>{esc(r.indicator)} <span class="muted">({esc(r.geography)}, {esc(r.year)}; {esc(r.source_type)}; checked: {badge(r.verified)})</span></li>' for _, r in qual.iterrows())
gaps = sf[sf.value.astype(str).isin(['NOT FOUND', 'NOT ACCESSED'])]
gap_html = ''.join(f'<li><b>{esc(r.value)}</b> — {esc(r.indicator)}</li>' for _, r in gaps.iterrows())
lit_html = table(lit, ['authors', 'year', 'country', 'design', 'n', 'effect_size'], ['Authors', 'Year', 'Country', 'Design', 'n', 'Effect (as printed)'], cls='scroll')

campv = camps[pd.to_numeric(camps.population, errors='coerce').notna() & camps.lat.notna()]
camp_html = table(campv, ['camp', 'population', 'date', 'woreda_geoboundaries', 'worldpop_2020_cell', 'worldpop_2020_cell_3x3'],
                  ['Camp', 'Registered (UNHCR)', 'Date', 'Woreda', 'WorldPop in its cell', 'WorldPop 3×3 cells'], cls='narrow')
lat = es[es.indicator.str.contains('latrine', case=False, na=False) & pd.to_numeric(es.value, errors='coerce').notna()]
lat_html = table(lat, ['indicator', 'value', 'unit', 'year', 'geography', 'source_type', 'verified'], ['Indicator', 'Value', 'Unit', 'Year', 'Where', 'Source type', 'Checked'], cls='scroll')
chol = es[es.indicator.str.contains('cholera', case=False, na=False) & pd.to_numeric(es.value, errors='coerce').notna()]
chol_html = table(chol, ['indicator', 'value', 'year', 'source_type'], ['Indicator', 'Value', 'Year', 'Source type'], cls='narrow')
spw = rd('sanitation_priority_woredas.csv'); spc = rd('sanitation_priority_camps.csv'); spg = rd('sanitation_priority_grid.csv')
spw_html = table(spw, ['woreda', 'people', 'mean_priority', 'people_high_priority', 'share_high_priority', 'people_zone_A', 'people_zone_B', 'people_zone_C', 'main_zone'],
                 ['Woreda', 'People', 'Priority (0-1)', 'People in high-priority cells', '% high', 'Zone A people', 'Zone B people', 'Zone C people', 'Main zone'],
                 num=('people', 'mean_priority', 'people_high_priority', 'share_high_priority', 'people_zone_A', 'people_zone_B', 'people_zone_C'))
spc_html = table(spc, ['camp', 'population', 'woreda_geoboundaries', 'toilet_zone', 'jrc_rp100_flooded_pct', 'clay_15_30'],
                 ['Camp', 'Refugees', 'Woreda', 'Zone from grid', '100-yr flood % of cell', 'Clay %'], num=('population', 'jrc_rp100_flooded_pct', 'clay_15_30'), cls='narrow')
hp = spg[spg.priority >= .6].pop_2020.sum(); rob = spg[spg.top20_agreement == 4]
zpop = spg.groupby('toilet_zone').pop_2020.sum()
ver_html = table(ver, ['file', 'rows', 'yes', 'no', 'nc'], ['File', 'Rows', 'Confirmed', 'Wrong (kept, marked)', 'Not checked'], num=('rows', 'yes', 'no', 'nc'), cls='narrow')

# ---------- national GDP series (World Bank)
wb = es[(es.admin_level == 'national') & (es.indicator == 'GDP per capita (current US$)')].copy()
wb['y'] = pd.to_numeric(wb.year, errors='coerce'); wb = wb.dropna(subset=['y']).sort_values('y')
wb = wb[wb.y.isin([2000, 2005, 2010, 2015, 2020, 2022, 2023, 2024])]
wb_html = table(wb.assign(value=pd.to_numeric(wb.value)), ['year', 'value'], ['Year', 'Ethiopia GDP per capita, current US$ (World Bank)'], num=('value',), cls='narrow')

r_ed, _ = cyr('annual_mm', 'gam_flood_record'); r_dd, _ = cyr('annual_mm', 'gam_drought_record'); r_sp, _ = cyr('spei12_dec_mean', 'gam_drought_record'); r_tr, _ = cyr('year', 'annual_mm')
gni_od, n66 = cs('pooled 2000-2024', 'open_defecation_pop_pct', 'gdl_gni_pc_ppp2017'); gni_is, _ = cs('pooled 2000-2024', 'improved_sanitation_pop_pct', 'gdl_gni_pc_ppp2017')
fd_gni, _ = cs('change between surveys (first differences)', 'improved_sanitation_pop_pct', 'gdl_gni_pc_ppp2017'); fd_hdi, _ = cs('change between surveys (first differences)', 'open_defecation_pop_pct', 'gdl_shdi')
od19_rank = int((p19.open_defecation_pop_pct > p19.loc[p19.region == 'Gambela', 'open_defecation_pop_pct'].iat[0]).sum() + 1)
g24 = gam[gam.year == 2024].iloc[0]; g16 = gam[gam.year == 2016].iloc[0]
dhs_sv = lambda yr, geo, code: sf[(sf.indicator.str.contains(code, regex=False)) & (sf.year.astype(str).str.startswith(str(yr))) & (sf.geography == geo)].value.iat[0]

CSS = """
:root{--bg:#f7f6f2;--card:#ffffff;--ink:#1d2329;--muted:#5d6670;--line:#e2dfd7;--accent:#1f5f8b;--warm:#a8611a;--flood:#2a6f97;--ok:#2e7d4f;--bad:#b23b2e;--chip:#eef3f7}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#14181c;--card:#1c2228;--ink:#e6e9ec;--muted:#9aa5b0;--line:#2c343c;--accent:#6fb0dd;--warm:#e0a060;--flood:#7bb7da;--ok:#6cc08f;--bad:#e5806f;--chip:#22303b}}
:root[data-theme="dark"]{--bg:#14181c;--card:#1c2228;--ink:#e6e9ec;--muted:#9aa5b0;--line:#2c343c;--accent:#6fb0dd;--warm:#e0a060;--flood:#7bb7da;--ok:#6cc08f;--bad:#e5806f;--chip:#22303b}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:15.5px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px 80px}
header{padding:44px 0 18px;border-bottom:1px solid var(--line);margin-bottom:8px}
h1{font-size:clamp(26px,4vw,38px);line-height:1.15;margin:0 0 8px;letter-spacing:-.01em}
h2{font-size:24px;margin:52px 0 6px;padding-top:8px;letter-spacing:-.01em}
h3{font-size:17px;margin:26px 0 8px}
p{margin:8px 0;max-width:78ch}.muted{color:var(--muted)}.small{font-size:13px}
nav.toc{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:8px 0;overflow-x:auto;white-space:nowrap}
nav.toc a{display:inline-block;color:var(--muted);text-decoration:none;font-size:13.5px;padding:4px 10px;border-radius:999px}
nav.toc a:hover{background:var(--chip);color:var(--ink)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:18px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.kpi b{display:block;font-size:28px;line-height:1.1;font-variant-numeric:tabular-nums}
.kpi span{font-size:13px;color:var(--muted)}
.kpi.flood b{color:var(--flood)}.kpi.warm b{color:var(--warm)}.kpi.bad b{color:var(--bad)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}
.note{border-left:3px solid var(--warm);background:var(--card);padding:10px 14px;border-radius:0 10px 10px 0;margin:14px 0;font-size:14.5px}
ul.find{padding-left:20px}ul.find li{margin:6px 0;max-width:80ch}
figure{margin:16px 0;background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px}
figure img{width:100%;height:auto;display:block}
figcaption{color:#5d6670;font-size:13px;padding:6px 4px 0}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card);margin:12px 0}
.tw.scroll{max-height:520px;overflow:auto}.tw.narrow{max-width:760px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{position:sticky;top:0;background:var(--chip);font-weight:600;font-size:12.5px;z-index:1}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tbody tr:hover{background:var(--chip)}
code{font-size:13px;background:var(--chip);padding:1px 5px;border-radius:5px}
.tag{display:inline-block;font-size:11.5px;padding:1px 8px;border-radius:999px;background:var(--chip);color:var(--muted);margin-left:6px;vertical-align:middle}
footer{margin-top:60px;border-top:1px solid var(--line);padding-top:16px;font-size:13px;color:var(--muted)}
@media (max-width:600px){h2{font-size:21px}.kpi b{font-size:24px}}
"""

H = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gambella Data Report</title><style>{CSS}</style></head><body>
<div class="wrap">
<header>
<div class="muted small">Gambela Region, Ethiopia · data pack for a flood- and drought-safe toilet · built 15–16 Nov 2026</div>
<h1>Gambella: floods, drought, money, toilets and safety</h1>
<p class="muted">Every number in the tables comes from a named source file in <code>gambella/data/</code>. Text marked <span class="tag">my analysis</span> is Claude's own calculation or interpretation, not a statement from a source.</p>
</header>
<nav class="toc"><a href="#summary">Summary</a><a href="#maps">Heat maps</a><a href="#terrain">Terrain &amp; people</a><a href="#woredas">Woredas</a><a href="#disasters">Flood &amp; drought records</a><a href="#economy">Economy</a><a href="#sanitation">Sanitation</a><a href="#safety">Safety</a><a href="#priority">Priority areas</a><a href="#design">Design implications</a><a href="#quality">Data quality</a><a href="#files">Files &amp; sources</a></nav>

<h2 id="summary">Summary <span class="tag">my analysis</span></h2>
<div class="kpis">
<div class="kpi flood"><b>{sh('100-year river flood covers >= 10% of cell'):.0f}%</b><span>of people live in cells where a 100-year flood covers ≥10% of the cell</span></div>
<div class="kpi"><b>{band45:.0f}%</b><span>of people live between 400 and 500 m elevation</span></div>
<div class="kpi warm"><b>{g24.open_defecation_pop_pct:.0f}%</b><span>open defecation in 2024 (DHS) — no progress since 2016 ({g16.open_defecation_pop_pct:.0f}%)</span></div>
<div class="kpi bad"><b>{sh('Vertisols (swelling clay) dominant'):.0f}%</b><span>of people live on swelling-clay Vertisols</span></div>
<div class="kpi"><b>{int(ev[~ev.event_id.str.startswith('GAP')].event_id.nunique())}</b><span>flood/drought events found 1961–2025 (24 floods)</span></div>
<div class="kpi"><b>438,572</b><span>registered refugees in Gambella (UNHCR data portal, 31 Oct 2026) — mostly missing from population maps</span></div>
</div>
<ul class="find">
<li><b>Flood, not drought, is the hazard where people live.</b> About half the host population lives where the 100-year river flood reaches; {sh('100-year river flood covers >= 50% of cell'):.0f}% where it covers at least half the cell. Elevation and flood extent are strongly negatively related (ρ = {c('elev_mean_m','jrc_rp100_flooded_pct'):.2f} across cells, {c('elev_mean_m','jrc_rp100_flooded_pct',col='spearman_blocks_025deg'):.2f} across 0.25° blocks).</li>
<li><b>Drought likelihood depends on how you measure it.</b> The lowland plain is drier on average (dry months vs elevation ρ = {c('elev_mean_m','chirps_dry_months_lt30mm_mean'):.2f}), but years with rain below 80% of normal are rare everywhere (0–18% of years) and cluster in the thinly populated south. Population density is <i>negatively</i> related to that drought measure (ρ = {c('pop_density_km2','chirps_share_years_below80pct'):.2f}).</li>
<li><b>Elevation vs population:</b> weakly negative (ρ = {c('elev_mean_m','pop_density_km2'):.2f} cells, {c('elev_mean_m','pop_density_km2',col='spearman_blocks_025deg'):.2f} blocks, not significant). Most people are on the plain, but the eastern highland woredas Godere and Mengesh are also dense.</li>
<li><b>Income does not explain toilet progress.</b> Across regions richer means better sanitation (ρ = {gni_is:.2f}), but within a region, income growth and sanitation gains are unrelated (ρ = {abs(fd_gni):.2f}). In 2019 Gambela had the {od19_rank}th-highest open defecation of 11 regions despite middling income.</li>
<li><b>Safety:</b> sexual and partner violence is common in camps and Gambella town (35–59% in local studies); DHS figures are much lower and known to undercount. Studies elsewhere link open-air or shared toilets to higher odds of non-partner sexual violence (odds ratios about 1.2–2.5). No study measures latrine-related violence in Gambella itself.</li>
</ul>

<h2 id="maps">Heat maps</h2>
<p>Grid of 1,002 cells (0.05°, about 5.5 km). Star = Gambela town, triangles = refugee camps, lines = woredas.</p>
{img('gambella_heatmap_panel.png', 'Elevation, population density (WorldPop 2020), two drought measures (CHIRPS rain deficit years, SPEI-12), dry-season length and 100-year river flood extent (JRC).')}
<div class="grid2">
{img('map_soil_class.png', 'Dominant soil group (SoilGrids 2.0, modelled). Vertisols = swelling clays that crack when dry and drain poorly when wet.')}
{img('map_clay_15_30.png', 'Clay content at 15–30 cm depth (SoilGrids 2.0).')}
{img('map_jrc_rp10_flooded_pct.png', 'Area flooded by a 10-year river flood (JRC global model).')}
{img('map_chirps_mean_annual_mm.png', 'Mean annual rainfall 1981–2025 (CHIRPS v2.0).')}
</div>

<h2 id="terrain">Terrain, people and hazard <span class="tag">my analysis</span></h2>
{img('scatter_elevation.png', 'Each dot is a grid cell: elevation against population density, rain-deficit years, dry months and 100-year flood extent.')}
<h3>Rank correlations between cells</h3>
<p class="muted small">Neighbouring cells are not independent, so p-values are given only for the coarser 0.25° blocks (n = 50) as a rough guide.</p>
{cg_html}
<h3>Who lives where</h3>
{exp_html}
{img('correlation_matrix_grid.png', 'Spearman correlation matrix of all grid variables (n = 1,002 cells).')}

<h2 id="woredas">Woredas, sorted by flood exposure</h2>
<p class="muted small">Cell averages per woreda (geoBoundaries 2016 boundaries). "100-yr flood % people" weights each cell by its WorldPop population. <span class="tag">my analysis</span></p>
{wh_html}
<h3>Refugee camps vs the population map</h3>
<p>WorldPop counts only a few hundred to a few thousand people in the cells holding camps of 10,000–110,000 refugees, so the grid describes the host population. Camp figures must be added separately.</p>
{camp_html}

<h2 id="disasters">Flood and drought records</h2>
<p>One row per event per source (59 source rows, {int(ev[~ev.event_id.str.startswith('GAP')].event_id.nunique())} events). Different sources for the same event are kept apart rather than merged. A year without a record does not mean there was no flood: sources say the rivers overflow almost every year, and reporting has grown since 2019.</p>
<div class="kpis">
<div class="kpi flood"><b>185,200</b><span>displaced in the 2022 flood (OCHA via news/GDACS), plus 79,631 otherwise affected</span></div>
<div class="kpi"><b>72%</b><span>of cropland damaged in 2022; 250–270 water schemes out of use</span></div>
<div class="kpi warm"><b>2002</b><span>last Gambella-specific drought impact figure found (58,400 needing food aid in 2003)</span></div>
</div>
{ev_html}
<p class="small muted">Ethiopia as a whole (EM-DAT): {int(eth.flood_events)} flood and {int(eth.drought_events)} drought records 1965–2026; {eth.flood_total_affected:,.0f} people affected by floods and {eth.drought_total_affected:,.0f} by droughts (summed over records). EM-DAT carries no place names, so it cannot be filtered to Gambella.</p>
<h3>Rainfall against the records <span class="tag">my analysis</span></h3>
<ul class="find">
<li>Wetter years are much more likely to have a recorded flood (ρ = {r_ed:.2f}, 1981–2025).</li>
<li>Recorded droughts barely relate to rainfall (ρ = {r_dd:.2f}) or SPEI (ρ = {r_sp:.2f}); "drought" here is more about late rains and failed flood-recession farming than low annual totals.</li>
<li>Caution: rainfall has risen (year vs rain ρ = {r_tr:.2f}) while reporting improved, which inflates the flood link.</li>
</ul>

<h2 id="economy">Economy and GDP</h2>
<div class="note">No official regional GDP exists for Gambella. What exists: national GDP (World Bank), modelled regional GNI and HDI (Global Data Lab), gridded GDP (Kummu et al.), and old JICA projections. All regional values below are modelled.</div>
<div class="grid2">
<div>{wb_html}</div>
<div><p>Regional poverty headcount (national poverty line, NPC 2017): <b>50.5%</b> (1999/00) → <b>32%</b> (2010/11) → <b>23.0%</b> (2015/16).</p>
<p>Gambela's modelled GNI per capita (GDL, 2017 PPP $) rose from <b>{gam.gdl_gni_pc_ppp2017.iat[0]:,.0f}</b> (2000) to <b>{g24.gdl_gni_pc_ppp2017:,.0f}</b> (2023), and its HDI from {gam.gdl_shdi.iat[0]:.3f} to {g24.gdl_shdi:.3f}.</p></div>
</div>

<h2 id="sanitation">Sanitation and toilets</h2>
<h3>Gambela over time (DHS)</h3>
{gam_html}
{img('panel_sanitation_income_rain.png', 'Left: open defecation per region (red = Gambela). Middle: open defecation against modelled GNI per capita, all regions and survey years. Right: Gambela rainfall anomaly with flood (blue bands) and drought (triangles) records.')}
<h3>Correlations across Ethiopia's 11 regions <span class="tag">my analysis</span></h3>
<p class="muted small">"Within a region" uses the change between consecutive surveys, which removes the common upward trend and the urban regions' head start.</p>
{cr_html}
{p19_html}
<h3>Latrines in camps and towns</h3>
{lat_html}
<h3>Cholera</h3>
{chol_html}

<h2 id="safety">Safety and sexual harassment</h2>
<div class="note">Figures differ in definition and recall period (past 12 months, lifetime, "any GBV" with a study-specific definition) and should not be compared directly. DHS violence figures are known to undercount; local studies sample high-risk groups.</div>
<div class="kpis">
<div class="kpi bad"><b>{dhs_sv(2024,'Gambela Region','DV_SPV1_W_POS')}%</b><span>physical or sexual partner violence, past 12 months, Gambela 2024 (Ethiopia {dhs_sv(2024,'Ethiopia','DV_SPV1_W_POS')}%)</span></div>
<div class="kpi"><b>{dhs_sv(2024,'Gambela Region','DV_STPV_W_NTL')}%</b><span>of women who experienced violence never sought help or told anyone (2024)</span></div>
<div class="kpi bad"><b>34.9%</b><span>sexual violence, Okugo camp (study definition, 2023)</span></div>
<div class="kpi warm"><b>43%</b><span>of recent sexual violence in Ethiopian camps happened in the evening (HVACS 2024)</span></div>
</div>
{sf_html}
<h3>Reported risks (qualitative)</h3><ul class="find">{qual_html}</ul>
<h3>Looked for but not found</h3><ul class="find small">{gap_html}</ul>
<h3>Toilet type and sexual violence — published studies</h3>
{lit_html}

<h2 id="priority">Where to improve sanitation first <span class="tag">my analysis</span></h2>
<div class="note">There is no village-level toilet data: DHS gives one number for the whole region. So this map ranks places by how many people live where ordinary pit latrines are most likely to fail (river flood, swelling clay, long dry season). Weights and thresholds are my choice; the robustness map shows the result holds under other weights.</div>
<div class="kpis">
<div class="kpi bad"><b>{hp/1000:,.0f}k</b><span>people in high-priority cells (score ≥ 0.6) of {spg.pop_2020.sum()/1000:,.0f}k host population</span></div>
<div class="kpi flood"><b>{zpop.get('A: raised / sealed above-ground unit',0)/1000:,.0f}k</b><span>people where only a raised or sealed above-ground toilet makes sense (zone A)</span></div>
<div class="kpi"><b>{len(rob)}</b><span>cells ({rob.pop_2020.sum()/1000:,.0f}k people) in the top 20% under all four weightings</span></div>
</div>
{img('sanitation_priority.png', 'Left: priority = people x (flood 50% + swelling clay 25% + dry season 25%). Right: toilet type suited to the ground. Circles = refugee camps sized by registered refugees.')}
<div class="grid2">
{img('sanitation_priority_robustness.png', 'Cells in the top 20% under 4 weightings: main, flood only, equal, water-scarcity heavy.')}
<div class="card"><h3 style="margin-top:0">How to read it</h3><ul class="find small">
<li><b>Start in Jikawo, Wantawo and Lare</b>: almost everyone there lives in the top priority band, and nearly all of it is zone A (raised/sealed units). Akobo and Itang follow.</li>
<li><b>Zone A</b>: a 10-year flood covers ≥30% or a 100-year flood ≥50% of the cell. Pits will be flooded.</li>
<li><b>Zone B</b>: flood edge (100-year flood 10–50%). Raised slab over a lined pit.</li>
<li><b>Zone C</b>: little river flooding, but clay soils. Lined pit; plan for dry-season water.</li>
<li><b>Gambella town and the big camps</b> (Nguenyiel, Tierkidi, Kule) fall in zones B/C on this river-flood model, but the model does not include flooding from heavy rain on flat clay ground; the camps' own flood history (2014) says to check on site.</li>
<li>Camps hold about 370,000 refugees missing from the population layer, so they rank too low here. Treat them as a separate priority.</li>
</ul></div>
</div>
{spw_html}
{spc_html}
<p class="small muted">Data: <code>data/sanitation_priority_grid.csv</code> (per cell, with every component), <code>sanitation_priority_woredas.csv</code>, <code>sanitation_priority_camps.csv</code>. Script: <code>scripts/an04_sanitation_priority.py</code>.</p>

<h2 id="design">What this means for the toilet design <span class="tag">my analysis</span></h2>
<div class="card"><ul class="find">
<li><b>Design for floods first.</b> Most people live on the flat 400–450 m plain that the Baro, Gilo and Akobo flood. A pit that floods spreads faeces; the 2014 camp floods made latrines overflow and collapse. Raised or sealed units suit the western woredas (Jikawo, Wantawo, Lare, Akobo, Jor).</li>
<li><b>Expect swelling clay.</b> Vertisols crack in the dry season and turn to mud when wet; unlined pits slump. Linings and bases need to cope with ground that moves.</li>
<li><b>Drought matters for water, less for structure.</b> The plain has about five dry months a year; designs needing flush water will fail then. Dry or low-water designs fit better.</li>
<li><b>Owning is not using.</b> In one study 47% of households with a latrine still practised open defecation, and open defecation stayed at about 45–47% while income rose. Comfort, privacy and maintenance matter as much as cost.</li>
<li><b>Safety features are evidence-based elsewhere, unproven here.</b> Locks, lighting, separate women's units and placement close to the home address the risks named in camp surveys (missing locks, no separate men's/women's latrines, night-time use). No study measures their effect in Gambella; that would need your own survey.</li>
<li><b>Count refugees separately.</b> About 439,000 refugees live largely outside the population map, in camps with 6–64 people per latrine.</li>
</ul></div>

<h2 id="quality">Data quality</h2>
<p>Every data file was re-checked on 16 Nov 2026 by an independent checker that re-opened the cited sources. Rows marked "wrong" are kept so the problem stays visible.</p>
{ver_html}
<h3>Errors found and fixed</h3>
<ul class="find small">
<li>2007 flood: IFRC's 36,090 affected was a five-region total; Gambella's share is 20,000.</li>
<li>2007 flood: Dartmouth figures (42,000 displaced, 17 dead) cover most of Ethiopia; the yearly value now uses Gambella sources (11,886 displaced, 1 death).</li>
<li>Population grid: a 0.1° westward shift was fixed (regional total 816,595 → 645,689).</li>
<li>Bandyopadhyay 2023: effect size −0.006 (not −0.005); sample size 76,580 added.</li>
</ul>
<h3>Still uncertain</h3>
<ul class="find small">
<li>11,749 displaced may belong to 2020, not 2021 (the OCHA original sits behind a bot check).</li>
<li>The two 2024 flood entries may be the same season counted twice.</li>
<li>1998: 66,000 displaced rests on a map match only. 2019: sources differ about eightfold (1,405 vs 11,128 displaced).</li>
<li>Two modelled population series disagree (480,000 vs 610,000 in 2022). WorldPop misses camp refugees.</li>
<li>Flood extent is a global model (JRC); groundwater depth was not found in any dataset.</li>
<li>Sources not accessed: ReliefWeb/OCHA (bot check), EDRMC/NDRMC sites (no response), several news sites (403).</li>
</ul>

<h2 id="files">Files and sources</h2>
<div class="card small">
<p><b>Folder:</b> <code>OneDrive/Research/gambella/</code> — <code>data/</code> CSVs (UTF-8, each row with source, URL and year), <code>maps/</code> PNGs, <code>scripts/</code> to rebuild, <code>raw/</code> downloads, <code>README.md</code> index.</p>
<p><b>Main sources:</b> DHS Program API (2000–2024 surveys); World Bank API; Global Data Lab sub-national HDI; Kummu et al. gridded GDP; EM-DAT via Our World in Data; IFRC GO; GDACS; Dartmouth Flood Observatory; UNHCR, UNICEF and Protection Cluster reports; peer-reviewed studies via Europe PMC; Copernicus DEM GLO-90; WorldPop 2020 (1 km, UN-adjusted); ISRIC SoilGrids 2.0; CHIRPS v2.0 rainfall; CHC SPEI-12; JRC Global Surface Water; JRC global river flood hazard maps; geoBoundaries and OCHA COD-AB boundaries; OSM waterways.</p>
<p>EM-DAT data are for non-commercial use; publish aggregated counts only.</p>
</div>
<footer>Built with Claude from the files in <code>gambella/</code> · 16 Nov 2026 · Correlations show association, not cause.</footer>
</div></body></html>"""
open(R + 'Gambella_data_report.html', 'w', encoding='utf-8').write(H)
print('written', len(H) // 1024, 'KB')
