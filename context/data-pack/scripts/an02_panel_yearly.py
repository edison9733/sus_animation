"""Cross-region panel (Ethiopia's 11 regions x DHS years) and Gambella yearly series: correlations.
Usage: python an02_panel_yearly.py <gambella root>
All outputs are derived (Claude's own analysis, 2026-11-16)."""
import sys, json
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R = sys.argv[1].rstrip('/') + '/'
DHS_URL = 'https://api.dhsprogram.com/rest/dhs/data?countryIds=ET&breakdown=subnational (raw/dhs/dhs_et_subnational.json)'
GDL_URL = 'https://globaldatalab.org/shdi/ (raw/es_gdl/*.html, Subnational HDI database)'

# ---------- DHS regional indicators
D = json.load(open(R + 'raw/dhs/dhs_et_subnational.json', encoding='utf-8'))
IND = {'WS_TLET_P_NFC': 'open_defecation_pop_pct', 'WS_TLET_P_IMP': 'improved_sanitation_pop_pct', 'WS_TLET_P_BAS': 'basic_sanitation_pop_pct',
       'WS_TLET_P_NIM': 'unimproved_sanitation_pop_pct', 'CH_DIAR_C_DIA': 'child_diarrhoea_pct', 'HC_WIXQ_P_LOW': 'lowest_wealth_quintile_pop_pct',
       'HC_ELEC_H_ELC': 'households_electricity_pct'}
MAP = {'Tigray': 'Tigray', 'Afar': 'Afar', 'Amhara': 'Amhara', 'Oromia': 'Oromia', 'Somali': 'Somali', 'Benishangul-Gumuz': 'Benishangul-Gumuz',
       'SNNPR': 'SNNPR', 'Gambela': 'Gambela', 'Harari': 'Harari', 'Addis Ababa': 'Addis Ababa', 'Dire Dawa': 'Dire Dawa'}
rows = [dict(region=MAP[x['CharacteristicLabel']], year=x['SurveyYear'], var=IND[x['IndicatorId']], value=x['Value'])
        for x in D if x['IndicatorId'] in IND and x['CharacteristicLabel'] in MAP and x['IsPreferred']]
dhs = pd.DataFrame(rows).drop_duplicates(['region', 'year', 'var']).pivot_table(index=['region', 'year'], columns='var', values='value').reset_index()

# ---------- GDL subnational HDI and log GNI per capita
GMAP = {'Addis': 'Addis Ababa', 'Affar': 'Afar', 'Amhara': 'Amhara', 'Ben-Gumz': 'Benishangul-Gumuz', 'Dire Dawa': 'Dire Dawa', 'Gambela': 'Gambela',
        'Harari': 'Harari', 'Oromiya': 'Oromia', 'SNNP': 'SNNPR', 'Somali': 'Somali', 'Tigray': 'Tigray'}
def gdl(f, name):
    t = pd.read_html(R + 'raw/es_gdl/' + f, flavor='lxml')[0]
    t = t.rename(columns={t.columns[0]: 'g'})
    t = t[t.g.isin(GMAP)].melt(id_vars='g', var_name='year', value_name=name)
    t['region'] = t.g.map(GMAP); t['year'] = t.year.astype(int)
    return t[['region', 'year', name]]
shdi = gdl('shdi_table_shdi_ETH__levels_1_4_interpolation_0_extrapolation_0.html', 'gdl_shdi')
lg = gdl('shdi_table_lgnic_ETH_.html', 'gdl_log_gni_pc')
gd = shdi.merge(lg, on=['region', 'year'], how='outer')
gd['gdl_gni_pc_ppp2017'] = np.exp(gd.gdl_log_gni_pc).round(0)
dhs['gdl_year'] = dhs.year.where(dhs.year <= 2023, 2023)  # GDL ends 2023; DHS 2024-25 matched to 2023
panel = dhs.merge(gd.rename(columns={'year': 'gdl_year'}), on=['region', 'gdl_year'], how='left')

# ---------- regional hazard exposure (EM-DAT has no region text; use JRC flood share only for Gambela -> not available nationally)
panel['source'] = f'DHS: {DHS_URL}; GDL: {GDL_URL}'
panel['derived'] = 'yes (merged; GNI pc = exp(log GNI pc))'
panel.to_csv(R + 'data/ethiopia_regions_panel.csv', index=False, encoding='utf-8-sig')

# ---------- correlations across regions
V = ['open_defecation_pop_pct', 'improved_sanitation_pop_pct', 'child_diarrhoea_pct', 'lowest_wealth_quintile_pop_pct',
     'households_electricity_pct', 'gdl_gni_pc_ppp2017', 'gdl_shdi']
out = []
for yr, d in [('pooled 2000-2024', panel)] + [(str(y), panel[panel.year == y]) for y in sorted(panel.year.unique())]:
    for i, x in enumerate(V):
        for y in V[i + 1:]:
            dd = d[[x, y]].dropna()
            if len(dd) < 5: continue
            r, p = stats.spearmanr(dd[x], dd[y])
            out.append(dict(sample=yr, var_x=x, var_y=y, n=len(dd), spearman=round(r, 3), p=float(f'{p:.3g}'), derived='yes',
                            note='regions are not independent draws; pooled sample repeats regions across years' if yr.startswith('pooled') else ''))
# within-region change (first differences between consecutive surveys) removes the common time trend
fd = panel.sort_values(['region', 'year']).groupby('region')[V].diff().dropna(how='all')
for i, x in enumerate(V):
    for y in V[i + 1:]:
        dd = fd[[x, y]].dropna()
        if len(dd) < 5: continue
        r, p = stats.spearmanr(dd[x], dd[y])
        out.append(dict(sample='change between surveys (first differences)', var_x=x, var_y=y, n=len(dd), spearman=round(r, 3), p=float(f'{p:.3g}'), derived='yes', note=''))
cr = pd.DataFrame(out)
cr.to_csv(R + 'data/correlations_regions.csv', index=False, encoding='utf-8-sig')

# ---------- Gambella yearly: rainfall vs flood/drought records
ry = pd.read_csv(R + 'data/gambella_rainfall_yearly.csv', encoding='utf-8-sig')
fy = pd.read_csv(R + 'data/gambella_flood_drought_yearly.csv', encoding='utf-8-sig')
ey = pd.read_csv(R + 'data/ethiopia_flood_drought_yearly.csv', encoding='utf-8-sig')
y = ry[['year', 'annual_mm', 'jjas_mm', 'anomaly_pct', 'spi_jja', 'spei12_dec_mean']].merge(
    fy[['year', 'flood_events', 'drought_events', 'flood_affected', 'flood_displaced']], on='year', how='left').merge(
    ey[['year', 'flood_events', 'drought_events', 'flood_total_affected', 'drought_total_affected']].rename(
        columns={'flood_events': 'eth_flood_events', 'drought_events': 'eth_drought_events', 'flood_total_affected': 'eth_flood_affected',
                 'drought_total_affected': 'eth_drought_affected'}), on='year', how='left')
y['gam_flood_record'] = (y.flood_events > 0).astype(int)
y['gam_drought_record'] = (y.drought_events > 0).astype(int)
y['derived'] = 'yes'
y.to_csv(R + 'data/gambella_yearly_merged.csv', index=False, encoding='utf-8-sig')
yo = []
def yc(name, a, b, d):
    dd = d[[a, b]].dropna()
    r, p = stats.spearmanr(dd[a], dd[b]); yo.append(dict(sample=name, var_x=a, var_y=b, n=len(dd), spearman=round(r, 3), p=float(f'{p:.3g}'), derived='yes'))
for per, d in [('1981-2025', y), ('2006-2025 (denser records)', y[y.year >= 2006])]:
    for a in ['annual_mm', 'jjas_mm', 'spi_jja', 'spei12_dec_mean']:
        for b in ['gam_flood_record', 'gam_drought_record', 'eth_flood_events', 'eth_drought_events']:
            yc(per, a, b, d)
yc('1981-2025', 'year', 'gam_flood_record', y); yc('1981-2025', 'year', 'annual_mm', y)
pd.DataFrame(yo).to_csv(R + 'data/correlations_yearly.csv', index=False, encoding='utf-8-sig')

# ---------- figures
g = panel[panel.region == 'Gambela'].sort_values('year')
fig, axs = plt.subplots(1, 3, figsize=(16, 4.8))
ax = axs[0]
for reg, d in panel.groupby('region'):
    d = d.sort_values('year'); c = '#c0392b' if reg == 'Gambela' else '#b0b0b0'
    ax.plot(d.year, d.open_defecation_pop_pct, '-o', ms=3, color=c, lw=2.2 if reg == 'Gambela' else 1, zorder=3 if reg == 'Gambela' else 1)
ax.set_title('Open defecation, % of population (DHS)\nred = Gambela, grey = other regions', fontsize=10, loc='left'); ax.grid(alpha=.3)
ax = axs[1]
d = panel.dropna(subset=['gdl_gni_pc_ppp2017', 'open_defecation_pop_pct'])
ax.scatter(d.gdl_gni_pc_ppp2017, d.open_defecation_pop_pct, c=d.year, cmap='viridis', s=30)
gg = d[d.region == 'Gambela']; ax.plot(gg.gdl_gni_pc_ppp2017, gg.open_defecation_pop_pct, '-', color='#c0392b', lw=1.5)
for _, rr in gg.iterrows(): ax.annotate(str(rr.year), (rr.gdl_gni_pc_ppp2017, rr.open_defecation_pop_pct), fontsize=7, color='#c0392b')
r = cr[(cr['sample'] == 'pooled 2000-2024') & (cr.var_x == 'open_defecation_pop_pct') & (cr.var_y == 'gdl_gni_pc_ppp2017')].iloc[0]
ax.set_xscale('log'); ax.set_xlabel('GNI per capita, 2017 PPP $ (GDL, modelled)'); ax.set_ylabel('Open defecation (%)')
ax.set_title(f'Regions x survey years: rho = {r.spearman:.2f} (n = {r.n})\nred line = Gambela', fontsize=10, loc='left'); ax.grid(alpha=.3)
ax = axs[2]
ax.bar(y.year, y.anomaly_pct, color=np.where(y.anomaly_pct < 0, '#c8862a', '#3b78a8'), width=.8)
for yr in y.year[y.gam_flood_record == 1]: ax.axvline(yr, color='#1f4e79', alpha=.25, lw=4)
for yr in y.year[y.gam_drought_record == 1]: ax.plot(yr, -24, marker='v', color='#8a4b08', ms=8)
ax.set_title('Gambela rainfall anomaly (CHIRPS, % of mean)\nblue bands = flood record, triangles = drought record', fontsize=10, loc='left')
ax.set_ylim(-26, 26); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(R + 'maps/panel_sanitation_income_rain.png', dpi=200); plt.close(fig)

pd.set_option('display.width', 250)
print(g[['year', 'open_defecation_pop_pct', 'improved_sanitation_pop_pct', 'basic_sanitation_pop_pct', 'child_diarrhoea_pct', 'lowest_wealth_quintile_pop_pct', 'gdl_gni_pc_ppp2017', 'gdl_shdi']].to_string())
print(cr[cr.var_x.isin(['open_defecation_pop_pct', 'improved_sanitation_pop_pct']) | cr.var_y.isin(['open_defecation_pop_pct'])].to_string())
print(pd.DataFrame(yo).to_string())
print(panel[panel.year == 2019][['region', 'open_defecation_pop_pct', 'improved_sanitation_pop_pct', 'child_diarrhoea_pct', 'gdl_gni_pc_ppp2017', 'gdl_shdi']].sort_values('open_defecation_pop_pct').to_string())
