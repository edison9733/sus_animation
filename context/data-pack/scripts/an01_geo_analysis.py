"""Grid-level analysis for Gambela: merge terrain + hazard, correlations, exposure, heat maps.
Usage: python an01_geo_analysis.py <gambella root>
Everything written here is derived (Claude's own analysis, 2026-11-16)."""
import sys, json
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, ListedColormap, BoundaryNorm
from shapely.geometry import shape

R = sys.argv[1].rstrip('/') + '/'
t = pd.read_csv(R + 'data/gambella_grid_terrain.csv', encoding='utf-8-sig')
h = pd.read_csv(R + 'data/gambella_grid_hazard.csv', encoding='utf-8-sig')
g = t.merge(h.drop(columns=['lat', 'lon', 'cell_area_km2', 'derived']), on='cell_id', validate='one_to_one')
assert len(g) == len(t) == len(h)
g.to_csv(R + 'data/gambella_grid_merged.csv', index=False, encoding='utf-8-sig')

V = {  # variable: label
    'elev_mean_m': 'Elevation (m)',
    'slope_mean_deg': 'Slope (deg)',
    'pop_density_km2': 'Population density (per km2)',
    'dist_to_river_km': 'Distance to river (km)',
    'clay_15_30': 'Clay 15-30 cm (%)',
    'chirps_mean_annual_mm': 'Mean annual rain (mm)',
    'chirps_cv_annual_pct': 'Rain variability, CV (%)',
    'chirps_dry_months_lt30mm_mean': 'Dry months per year (<30 mm)',
    'chirps_share_years_below80pct': 'Years with rain <80% of normal (%)',
    'spei12_share_months_le_m1': 'Months with SPEI-12 <= -1 (%)',
    'gsw_occ_ge1_pct': 'Area with surface water seen 1984-2021 (%)',
    'jrc_rp10_flooded_pct': 'Area flooded, 10-year river flood (%)',
    'jrc_rp100_flooded_pct': 'Area flooded, 100-year river flood (%)',
}
cols = list(V)

# ---- correlations at cell level (Spearman) and at 0.25-degree block level (spatial autocorrelation check)
g['blk'] = (np.floor(g.lat / 0.25)).astype(int).astype(str) + '_' + (np.floor(g.lon / 0.25)).astype(int).astype(str)
agg = {c: 'mean' for c in cols}; agg['pop_2020'] = 'sum'; agg['cell_area_km2'] = 'sum'
b = g.groupby('blk').agg(agg); b['pop_density_km2'] = b.pop_2020 / b.cell_area_km2
rows = []
for i, x in enumerate(cols):
    for y in cols[i + 1:]:
        r, p = stats.spearmanr(g[x], g[y]); rb, pb = stats.spearmanr(b[x], b[y]); rp, _ = stats.pearsonr(g[x], g[y])
        rows.append(dict(var_x=x, var_y=y, spearman_cells=round(r, 3), n_cells=len(g), pearson_cells=round(rp, 3),
                         spearman_blocks_025deg=round(rb, 3), n_blocks=len(b), p_blocks=float(f'{pb:.3g}'),
                         derived='yes', note='cell p-values not given: neighbouring cells are not independent; block p is a rough guide only'))
cor = pd.DataFrame(rows)
cor.to_csv(R + 'data/correlations_grid.csv', index=False, encoding='utf-8-sig')
M = g[cols].corr(method='spearman')
M.round(3).to_csv(R + 'data/correlation_matrix_grid_spearman.csv', encoding='utf-8-sig')

# ---- exposure: where people live relative to hazard
P = g.pop_2020.sum(); A = g.cell_area_km2.sum()
ex = []
def add(name, mask):
    ex.append(dict(group=name, cells=int(mask.sum()), area_km2=round(g.cell_area_km2[mask].sum()), share_area=round(g.cell_area_km2[mask].sum() / A, 4),
                   population_worldpop_2020=round(g.pop_2020[mask].sum()), share_population=round(g.pop_2020[mask].sum() / P, 4), derived='yes'))
add('all cells', g.lat > 0)
add('elevation < 450 m', g.elev_mean_m < 450)
add('elevation 450-600 m', (g.elev_mean_m >= 450) & (g.elev_mean_m < 600))
add('elevation >= 600 m', g.elev_mean_m >= 600)
for th in (10, 50):
    add(f'10-year river flood covers >= {th}% of cell', g.jrc_rp10_flooded_pct >= th)
    add(f'100-year river flood covers >= {th}% of cell', g.jrc_rp100_flooded_pct >= th)
add('surface water ever seen on >= 5% of cell', g.gsw_occ_ge1_pct >= 5)
q = g.chirps_share_years_below80pct.quantile(.75)
add(f'rain-deficit years in top quarter (>= {q:.1f}% of years below 80% of normal)', g.chirps_share_years_below80pct >= q)
add('mean annual rain < 1000 mm', g.chirps_mean_annual_mm < 1000)
add('Vertisols (swelling clay) dominant', g.wrb_class == 'Vertisols')
add('100-year flood >= 50% AND Vertisols', (g.jrc_rp100_flooded_pct >= 50) & (g.wrb_class == 'Vertisols'))
pd.DataFrame(ex).to_csv(R + 'data/population_exposure.csv', index=False, encoding='utf-8-sig')

# pixel-weighted flood exposure by woreda (cell approximation)
w = g.groupby('woreda').apply(lambda d: pd.Series(dict(
    cells=len(d), pop_2020=round(d.pop_2020.sum()), elev_mean_m=round(np.average(d.elev_mean_m), 1),
    rain_mean_mm=round(d.chirps_mean_annual_mm.mean()), rain_cv_pct=round(d.chirps_cv_annual_pct.mean(), 1),
    dry_months=round(d.chirps_dry_months_lt30mm_mean.mean(), 2),
    years_below80pct_share=round(d.chirps_share_years_below80pct.mean(), 1), spei12_le_m1_share=round(d.spei12_share_months_le_m1.mean(), 1),
    flood_rp10_area_pct=round(d.jrc_rp10_flooded_pct.mean(), 1), flood_rp100_area_pct=round(d.jrc_rp100_flooded_pct.mean(), 1),
    pop_weighted_flood_rp100_pct=round(np.average(d.jrc_rp100_flooded_pct, weights=d.pop_2020), 1),
    surface_water_area_pct=round(d.gsw_occ_ge1_pct.mean(), 2), clay_15_30=round(d.clay_15_30.mean(), 1),
    dominant_soil=d.wrb_class.mode().iat[0], derived='yes'))).reset_index()
w.to_csv(R + 'data/gambella_woreda_hazard.csv', index=False, encoding='utf-8-sig')

# ---- maps
adm3 = json.load(open(R + 'data/gambella_adm3.geojson', encoding='utf-8'))
polys = [shape(f['geometry']) for f in adm3['features']]
camps = pd.read_csv(R + 'data/gambella_refugee_camps.csv', encoding='utf-8-sig')
camps = camps[pd.to_numeric(camps.population, errors='coerce').notna() & camps.lat.notna()]
lons = np.round(np.arange(g.lon.min(), g.lon.max() + 1e-6, 0.05), 3); lats = np.round(np.arange(g.lat.min(), g.lat.max() + 1e-6, 0.05), 3)
ix = {v: i for i, v in enumerate(lons)}; iy = {v: i for i, v in enumerate(lats)}
def raster(col):
    a = np.full((len(lats), len(lons)), np.nan)
    for la, lo, v in zip(g.lat.round(3), g.lon.round(3), g[col]): a[iy[la], ix[lo]] = v
    return a
ext = [lons[0] - .025, lons[-1] + .025, lats[0] - .025, lats[-1] + .025]
def outlines(ax, labels=False):
    for p in polys:
        for q in (p.geoms if p.geom_type == 'MultiPolygon' else [p]):
            x, y = q.exterior.xy; ax.plot(x, y, color='#222', lw=.5)
    ax.plot(34.59, 8.25, marker='*', color='white', mec='black', ms=11, zorder=5)
    ax.scatter(camps.lon, camps.lat, marker='^', s=22, color='white', edgecolor='black', lw=.7, zorder=5)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1 / np.cos(np.radians(7.7)))
    ax.tick_params(labelsize=7)
def panel(ax, col, title, cmap, norm=None, unit=''):
    a = raster(col)
    if norm is not None and isinstance(norm, LogNorm): a = np.where(a < norm.vmin, norm.vmin, a)
    im = ax.imshow(a, origin='lower', extent=ext, cmap=cmap, norm=norm, interpolation='nearest')
    outlines(ax); ax.set_title(title, fontsize=10, loc='left')
    cb = plt.colorbar(im, ax=ax, shrink=.8, pad=.02); cb.ax.tick_params(labelsize=7); cb.set_label(unit, fontsize=8)
SPEC = [
    ('elev_mean_m', 'Elevation', 'terrain', LogNorm(390, 2300), 'm (log scale)'),
    ('pop_density_km2', 'Population density (WorldPop 2020)', 'magma_r', LogNorm(1, 1500), 'people per km2 (log scale)'),
    ('chirps_share_years_below80pct', 'Drought likelihood: years with rain below 80% of normal', 'YlOrBr', None, '% of years, 1981-2025'),
    ('chirps_dry_months_lt30mm_mean', 'Dry-season length', 'YlOrBr', None, 'months per year under 30 mm'),
    ('spei12_share_months_le_m1', 'Drought likelihood: months with SPEI-12 <= -1', 'YlOrBr', None, '% of months, 1982-2025'),
    ('jrc_rp100_flooded_pct', 'Flood likelihood: area under a 100-year river flood', 'Blues', None, '% of cell'),
]
fig, axs = plt.subplots(3, 2, figsize=(13, 15))
for ax, s in zip(axs.ravel(), SPEC): panel(ax, *s)
fig.suptitle('Gambela Region, Ethiopia - terrain, people, drought and flood (0.05-degree cells, about 5.5 km)\n'
             'star = Gambela town, triangles = refugee camps, lines = woredas (geoBoundaries 2016)', fontsize=12, y=.995)
fig.tight_layout(); fig.savefig(R + 'maps/gambella_heatmap_panel.png', dpi=200); plt.close(fig)
for col, title, cmap, norm, unit in SPEC + [('jrc_rp10_flooded_pct', 'Flood likelihood: area under a 10-year river flood', 'Blues', None, '% of cell'),
                                            ('chirps_mean_annual_mm', 'Mean annual rainfall (CHIRPS 1981-2025)', 'YlGnBu', None, 'mm'),
                                            ('clay_15_30', 'Clay content at 15-30 cm (SoilGrids 2.0)', 'copper_r', None, '%')]:
    fig, ax = plt.subplots(figsize=(8, 6.5)); panel(ax, col, title, cmap, norm, unit); fig.tight_layout()
    fig.savefig(R + f'maps/map_{col}.png', dpi=200); plt.close(fig)
# soil class map
cls = [c for c in g.wrb_class.value_counts().index]
code = {c: i for i, c in enumerate(cls)}; g['_s'] = g.wrb_class.map(code)
pal = ['#b08d57', '#4a4a4a', '#d9a441', '#9e9e9e', '#c0504d', '#5b8db8', '#e07b39', '#8c4a2f', '#6a5d7b'][:len(cls)]
fig, ax = plt.subplots(figsize=(8, 6.5))
ax.imshow(raster('_s'), origin='lower', extent=ext, cmap=ListedColormap(pal), norm=BoundaryNorm(np.arange(-.5, len(cls)), len(cls)), interpolation='nearest')
outlines(ax); ax.set_title('Dominant soil group per cell (SoilGrids 2.0 WRB, modelled)', fontsize=10, loc='left')
ax.legend([plt.Rectangle((0, 0), 1, 1, color=c) for c in pal], [f'{c} ({(g.wrb_class == c).sum()} cells)' for c in cls], fontsize=7, loc='lower left')
fig.tight_layout(); fig.savefig(R + 'maps/map_soil_class.png', dpi=200); plt.close(fig)

# scatter: elevation vs population density and vs hazards
fig, axs = plt.subplots(2, 2, figsize=(11, 9))
for ax, (y, lab, logy) in zip(axs.ravel(), [('pop_density_km2', V['pop_density_km2'], True), ('chirps_share_years_below80pct', V['chirps_share_years_below80pct'], False),
                                            ('chirps_dry_months_lt30mm_mean', V['chirps_dry_months_lt30mm_mean'], False), ('jrc_rp100_flooded_pct', V['jrc_rp100_flooded_pct'], False)]):
    yy = g[y].clip(lower=.5) if logy else g[y]
    ax.scatter(g.elev_mean_m, yy, s=6, alpha=.5, color='#2a6f97'); ax.set_xscale('log')
    if logy: ax.set_yscale('log')
    r = stats.spearmanr(g.elev_mean_m, g[y])[0]
    ax.set_xlabel('Elevation (m, log scale)'); ax.set_ylabel(lab); ax.set_title(f'Spearman rho = {r:.2f} (n = {len(g)} cells)', fontsize=10, loc='left'); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(R + 'maps/scatter_elevation.png', dpi=200); plt.close(fig)

# correlation matrix figure
fig, ax = plt.subplots(figsize=(10, 8.5))
im = ax.imshow(M.values, cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(len(cols))); ax.set_yticks(range(len(cols)))
ax.set_xticklabels([V[c] for c in cols], rotation=45, ha='right', fontsize=7); ax.set_yticklabels([V[c] for c in cols], fontsize=7)
for i in range(len(cols)):
    for j in range(len(cols)):
        ax.text(j, i, f'{M.values[i, j]:.2f}', ha='center', va='center', fontsize=6.5, color='white' if abs(M.values[i, j]) > .6 else 'black')
plt.colorbar(im, ax=ax, shrink=.8, label='Spearman rho'); ax.set_title(f'Rank correlations between grid cells (n = {len(g)})', loc='left', fontsize=10)
fig.tight_layout(); fig.savefig(R + 'maps/correlation_matrix_grid.png', dpi=200); plt.close(fig)

pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 80)
key = cor[(cor.var_x.isin(['elev_mean_m', 'pop_density_km2'])) | (cor.var_y == 'pop_density_km2')]
print(key[['var_x', 'var_y', 'spearman_cells', 'spearman_blocks_025deg', 'p_blocks']].to_string())
print(pd.DataFrame(ex).to_string()); print(w.to_string())
