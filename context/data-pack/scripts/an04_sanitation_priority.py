"""Where would a flood/drought-safe toilet help most? Priority heat map + toilet-type zones for Gambela.
Usage: python an04_sanitation_priority.py <gambella root>
The index, weights and thresholds are Claude's own construction (2026-11-16), not from a source.
There is no cell-level sanitation data: DHS gives only one value for the whole region, so 'need' here
means people exposed to the conditions that break ordinary pit latrines (flood, swelling clay, dry season)."""
import sys, json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from shapely.geometry import shape

R = sys.argv[1].rstrip('/') + '/'
g = pd.read_csv(R + 'data/gambella_grid_merged.csv', encoding='utf-8-sig')
rk = lambda s: s.rank(pct=True, method='average')   # 0-1 percentile rank, robust to skew

# ---- components (each 0-1)
g['c_people'] = rk(np.log1p(g.pop_density_km2))
g['c_flood'] = rk(0.5 * g.jrc_rp10_flooded_pct + 0.5 * g.jrc_rp100_flooded_pct)
g['c_soil'] = rk(g.clay_15_30) * np.where(g.wrb_class == 'Vertisols', 1.0, 0.8)
g['c_dry'] = rk(g.chirps_dry_months_lt30mm_mean)
W = {'main (flood 50, soil 25, dry 25)': (.50, .25, .25),
     'flood only': (1.0, 0, 0),
     'equal (flood, soil, dry 1/3 each)': (1 / 3, 1 / 3, 1 / 3),
     'water-scarcity heavy (flood 25, soil 25, dry 50)': (.25, .25, .50)}
def score(w):
    hz = w[0] * g.c_flood + w[1] * g.c_soil + w[2] * g.c_dry
    return g.c_people * hz          # multiplicative: empty land scores low however hazardous
for i, (k, w) in enumerate(W.items()):
    g[f's{i}'] = score(w)
g['priority'] = g.s0 / g.s0.max()
SPARSE = 2.0  # people per km2
g.loc[g.pop_density_km2 < SPARSE, 'priority'] = np.nan
top = lambda col: g[col] >= g[col].quantile(.8)
g['top20_agreement'] = sum(top(f's{i}').astype(int) for i in range(len(W)))
g['priority_class'] = pd.cut(g.priority, [-.01, .2, .4, .6, .8, 1.01], labels=['very low', 'low', 'medium', 'high', 'very high'])

# ---- toilet-type zones (rules from data; thresholds are mine)
def zone(r):
    if r.pop_density_km2 < SPARSE: return 'E: too sparse for a programme'
    if r.jrc_rp10_flooded_pct >= 30 or r.jrc_rp100_flooded_pct >= 50: return 'A: raised / sealed above-ground unit'
    if r.jrc_rp100_flooded_pct >= 10: return 'B: raised slab + lined pit'
    if r.slope_mean_deg >= 8: return 'D: steep ground, site-specific'
    return 'C: lined pit (clay), low flood'
g['toilet_zone'] = g.apply(zone, axis=1)

out = g[['cell_id', 'lat', 'lon', 'woreda', 'zone', 'pop_2020', 'pop_density_km2', 'elev_mean_m', 'jrc_rp10_flooded_pct', 'jrc_rp100_flooded_pct',
         'clay_15_30', 'wrb_class', 'chirps_dry_months_lt30mm_mean', 'slope_mean_deg', 'c_people', 'c_flood', 'c_soil', 'c_dry',
         'priority', 'priority_class', 'top20_agreement', 'toilet_zone']].copy()
out['derived'] = 'yes'
out['note'] = ('priority = people rank x (0.5 flood + 0.25 soil + 0.25 dry-season rank), scaled 0-1; blank where < 2 people/km2; '
               'top20_agreement = in how many of 4 weightings the cell is in the top 20%; weights and zone thresholds are Claude\'s own choice; '
               'refugee camps not in WorldPop, see camps file')
out.to_csv(R + 'data/sanitation_priority_grid.csv', index=False, encoding='utf-8-sig')

# ---- woreda ranking
def wsum(d):
    p = d.pop_2020.sum()
    hi = d[d.priority >= .6].pop_2020.sum()
    z = d.groupby('toilet_zone').pop_2020.sum()
    return pd.Series(dict(people=round(p), people_high_priority=round(hi), share_high_priority=round(hi / p * 100, 1) if p else 0,
                          mean_priority=round(np.average(d.priority.fillna(0), weights=d.pop_2020 + 1e-9), 3),
                          people_zone_A=round(z.get('A: raised / sealed above-ground unit', 0)), people_zone_B=round(z.get('B: raised slab + lined pit', 0)),
                          people_zone_C=round(z.get('C: lined pit (clay), low flood', 0)), main_zone=z.idxmax(), derived='yes'))
wr = g.groupby('woreda').apply(wsum, include_groups=False).reset_index().sort_values('mean_priority', ascending=False)
camps = pd.read_csv(R + 'data/gambella_refugee_camps.csv', encoding='utf-8-sig')
camps = camps[pd.to_numeric(camps.population, errors='coerce').notna() & camps.lat.notna()].copy()
camps['population'] = camps.population.astype(int)
cz = camps.merge(g[['cell_id', 'toilet_zone', 'jrc_rp100_flooded_pct', 'clay_15_30']], on='cell_id', how='left')
cz[['camp', 'population', 'date', 'woreda_geoboundaries', 'cell_id', 'toilet_zone', 'jrc_rp100_flooded_pct', 'clay_15_30']].assign(derived='yes (zone from grid)').to_csv(
    R + 'data/sanitation_priority_camps.csv', index=False, encoding='utf-8-sig')
wr.to_csv(R + 'data/sanitation_priority_woredas.csv', index=False, encoding='utf-8-sig')

# ---- maps
adm3 = json.load(open(R + 'data/gambella_adm3.geojson', encoding='utf-8'))
polys = [(f['properties'].get('shapeName', ''), shape(f['geometry'])) for f in adm3['features']]
lons = np.round(np.arange(g.lon.min(), g.lon.max() + 1e-6, .05), 3); lats = np.round(np.arange(g.lat.min(), g.lat.max() + 1e-6, .05), 3)
ix = {v: i for i, v in enumerate(lons)}; iy = {v: i for i, v in enumerate(lats)}
def raster(v):
    a = np.full((len(lats), len(lons)), np.nan)
    for la, lo, x in zip(g.lat.round(3), g.lon.round(3), v): a[iy[la], ix[lo]] = x
    return a
ext = [lons[0] - .025, lons[-1] + .025, lats[0] - .025, lats[-1] + .025]
def base(ax, labels=True):
    for nm, p in polys:
        for q in (p.geoms if p.geom_type == 'MultiPolygon' else [p]):
            x, y = q.exterior.xy; ax.plot(x, y, color='#333', lw=.5)
        if labels and p.area > .03:
            c = p.representative_point(); ax.text(c.x, c.y, nm, fontsize=6.5, ha='center', color='#111', alpha=.75)
    ax.plot(34.59, 8.25, marker='*', color='white', mec='black', ms=12, zorder=6)
    s = 20 + camps.population / 800
    ax.scatter(camps.lon, camps.lat, s=s, marker='o', facecolor='none', edgecolor='#c2185b', lw=1.6, zorder=6)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1 / np.cos(np.radians(7.7))); ax.tick_params(labelsize=7)
    ax.set_facecolor('#f2f2f2')

fig, axs = plt.subplots(1, 2, figsize=(16, 8.2))
ax = axs[0]
im = ax.imshow(raster(g.priority), origin='lower', extent=ext, cmap='YlOrRd', vmin=0, vmax=1, interpolation='nearest')
base(ax); cb = plt.colorbar(im, ax=ax, shrink=.75, pad=.02); cb.set_label('priority (0 = low, 1 = highest)', fontsize=8)
ax.set_title('Where a flood- and drought-safe toilet would help most people\n'
             'people x (flood 50% + swelling clay 25% + dry season 25%); grey = fewer than 2 people/km²', fontsize=10, loc='left')
ax = axs[1]
ZN = ['A: raised / sealed above-ground unit', 'B: raised slab + lined pit', 'C: lined pit (clay), low flood', 'D: steep ground, site-specific', 'E: too sparse for a programme']
pal = ['#1f5f8b', '#7fb3d5', '#d9b26f', '#8d6e63', '#e6e6e6']
zr = raster(g.toilet_zone.map({z: i for i, z in enumerate(ZN)}))
ax.imshow(zr, origin='lower', extent=ext, cmap=ListedColormap(pal), norm=BoundaryNorm(np.arange(-.5, 5), 5), interpolation='nearest')
base(ax)
zp = g.groupby('toilet_zone').pop_2020.sum()
ax.legend([plt.Rectangle((0, 0), 1, 1, color=c) for c in pal] + [plt.Line2D([], [], marker='o', ls='', mfc='none', mec='#c2185b', mew=1.6, ms=9)],
          [f'{z}  ({zp.get(z, 0) / 1000:,.0f}k people)' for z in ZN] + ['refugee camp (size = registered refugees)'], fontsize=7.5, loc='lower left', framealpha=.92)
ax.set_title('Which toilet type fits the ground\nA: 10-yr flood ≥30% or 100-yr ≥50% of cell · B: 100-yr flood 10–50% · D: slope ≥8°', fontsize=10, loc='left')
fig.suptitle('Gambela Region — sanitation improvement areas (my index from flood, soil, rainfall and population data; star = Gambela town)', fontsize=12, y=.995)
fig.tight_layout(rect=[0, 0, 1, .955]); fig.savefig(R + 'maps/sanitation_priority.png', dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 7))
ag = raster(g.top20_agreement.where(g.pop_density_km2 >= SPARSE))
im = ax.imshow(ag, origin='lower', extent=ext, cmap=ListedColormap(['#ffffff', '#fde0c5', '#f9a65a', '#e8590c', '#a61e05']), norm=BoundaryNorm(np.arange(-.5, 5), 5), interpolation='nearest')
base(ax); cb = plt.colorbar(im, ax=ax, shrink=.75, ticks=range(5)); cb.set_label('in the top 20% under how many of 4 weightings', fontsize=8)
ax.set_title('How robust is the priority map?\n4 = top 20% whatever the weights (flood only, equal, water-heavy, main)', fontsize=10, loc='left')
fig.tight_layout(); fig.savefig(R + 'maps/sanitation_priority_robustness.png', dpi=200); plt.close(fig)

pd.set_option('display.width', 250)
print(wr.to_string()); print(zp.round()); print(cz[['camp', 'population', 'toilet_zone', 'jrc_rp100_flooded_pct']].to_string())
rob = g[g.top20_agreement == 4]; print('robust top cells', len(rob), 'people', round(rob.pop_2020.sum()), rob.woreda.value_counts().to_dict())
print('high+ priority people', round(g[g.priority >= .6].pop_2020.sum()), 'of', round(g.pop_2020.sum()))
