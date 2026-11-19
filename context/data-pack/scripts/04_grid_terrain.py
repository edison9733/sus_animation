"""Terrain / soil / population layer for Gambela Region on the common 0.05-degree grid.
Usage: python scripts/04_grid_terrain.py C:/Users/janss/OneDrive/Research/gambella
Inputs (see scripts/00_download_terrain_raw.sh, 01_boundaries.py, 02_download_soilgrids.py, 03_download_wrb.py):
  data/gambella_adm{1,2,3}.geojson (geoBoundaries 2016), data/gambella_adm3_cod2025.geojson (OCHA COD-AB v04)
  raw/dem/*.tif (Copernicus GLO-90), raw/pop/eth_ppp_2020_1km_Aggregated_UNadj.tif (WorldPop),
  raw/soil/*.tif (SoilGrids 2.0), raw/rivers/osm_waterways_gambella_v2.json (OSM), raw/groundwater/bgs_dtw/... (BGS)
Outputs: data/gambella_grid_terrain.csv, data/gambella_woreda_terrain.csv, data/gambella_elevation_bands.csv,
  data/gambella_refugee_camps.csv, scratch arrays in raw/derived/ for 05_maps.py
Everything written here is DERIVED (zonal statistics); methods are in the notes columns and in SOURCES_terrain.md.
"""
import sys, json, glob, struct, math
import numpy as np, pandas as pd
import rasterio
from rasterio.merge import merge
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
import pyproj, shapely
from shapely.geometry import shape, Point, LineString, box
from shapely.strtree import STRtree

R = sys.argv[1].rstrip('/') + '/'
import os
os.makedirs(R + 'raw/derived', exist_ok=True)
NF = 'NOT FOUND'

def load(p): return json.load(open(p, encoding='utf-8'))
LAEA = pyproj.Transformer.from_crs('EPSG:4326', '+proj=laea +lat_0=7.5 +lon_0=34.2 +datum=WGS84 +units=m', always_xy=True)
def to_laea(g): return shapely.transform(g, lambda c: np.column_stack(LAEA.transform(c[:, 0], c[:, 1])))
GEOD = pyproj.Geod(ellps='WGS84')

# ---------------- boundaries
adm1 = shape(load(R + 'data/gambella_adm1.geojson')['features'][0]['geometry']).buffer(0)
adm2 = [(f['properties']['shapeName'], shape(f['geometry']).buffer(0)) for f in load(R + 'data/gambella_adm2.geojson')['features']]
adm3 = [(f['properties']['shapeName'], f['properties']['zone'], shape(f['geometry']).buffer(0)) for f in load(R + 'data/gambella_adm3.geojson')['features']]
cod3 = [(f['properties']['adm3_name'], f['properties']['adm2_name'], shape(f['geometry']).buffer(0)) for f in load(R + 'data/gambella_adm3_cod2025.geojson')['features']]
cod1 = shape(load(R + 'data/gambella_adm1_cod2025.geojson')['features'][0]['geometry']).buffer(0)
print('ADM1 bounds', adm1.bounds, 'n adm2', len(adm2), 'n adm3', len(adm3), 'n cod3', len(cod3))

# ---------------- common grid
cells = []
for i in range(0, 60):
    lon = round(33.025 + 0.05 * i, 3)
    for j in range(0, 90):
        lat = round(5.025 + 0.05 * j, 3)
        if adm1.contains(Point(lon, lat)):
            cells.append((f"{lat:.3f}_{lon:.3f}", lat, lon, i, j))
grid = pd.DataFrame(cells, columns=['cell_id', 'lat', 'lon', 'i', 'j'])
N = len(grid)
LUT = -np.ones((90, 60), dtype=np.int32)
LUT[grid.j.values, grid.i.values] = np.arange(N)
print('grid cells', N)

def cell_index(lon, lat):
    """index of the grid cell that contains each (lon, lat); -1 if not a kept cell"""
    i = np.floor((np.asarray(lon) - 33.0) / 0.05 + 1e-9).astype(int)
    j = np.floor((np.asarray(lat) - 5.0) / 0.05 + 1e-9).astype(int)
    ok = (i >= 0) & (i < 60) & (j >= 0) & (j < 90)
    out = -np.ones(i.shape, dtype=np.int32)
    out[ok] = LUT[j[ok], i[ok]]
    return out

def agg(idx, val, valid, how):
    m = (idx >= 0) & valid
    k = idx[m]; v = val[m].astype('float64')
    cnt = np.bincount(k, minlength=N)
    if how == 'sum':
        return np.bincount(k, weights=v, minlength=N), cnt
    if how == 'mean':
        s = np.bincount(k, weights=v, minlength=N)
        with np.errstate(invalid='ignore', divide='ignore'):
            return np.where(cnt > 0, s / cnt, np.nan), cnt
    if how in ('min', 'max'):
        o = np.full(N, np.inf if how == 'min' else -np.inf)
        (np.minimum if how == 'min' else np.maximum).at(o, k, v)
        o[~np.isfinite(o)] = np.nan
        return o, cnt

# cell area (true ellipsoidal area of the 0.05 x 0.05 degree box)
def box_area_km2(lon, lat, h=0.025):
    a, _ = GEOD.polygon_area_perimeter([lon - h, lon + h, lon + h, lon - h], [lat - h, lat - h, lat + h, lat + h])
    return abs(a) / 1e6
grid['cell_area_km2'] = [box_area_km2(lo, la) for lo, la in zip(grid.lon, grid.lat)]

# woreda / zone of each cell centre
def which(polys, lon, lat):
    p = Point(lon, lat)
    for rec in polys:
        if rec[-1].contains(p): return rec, 'centre inside'
    d = [(rec[-1].distance(p), k) for k, rec in enumerate(polys)]
    return polys[min(d)[1]], 'nearest polygon (centre in a sliver between polygons)'
w = [which(adm3, lo, la) for lo, la in zip(grid.lon, grid.lat)]
grid['woreda'] = [x[0][0] for x in w]
grid['woreda_match'] = [x[1] for x in w]
z = [which(adm2, lo, la) for lo, la in zip(grid.lon, grid.lat)]
grid['zone'] = [x[0][0] for x in z]
c = [which(cod3, lo, la) if cod1.contains(Point(lo, la)) else ((NF, NF, None), 'centre outside COD-AB Gambela') for lo, la in zip(grid.lon, grid.lat)]
grid['woreda_cod2025'] = [x[0][0] for x in c]
grid['zone_cod2025'] = [x[0][1] for x in c]

# ---------------- DEM mosaic + slope
srcs = [rasterio.open(p) for p in sorted(glob.glob(R + 'raw/dem/*.tif'))]
dem, dtf = merge(srcs)
dem = dem[0].astype('float32')
H, W = dem.shape
print('DEM mosaic', dem.shape, dtf, 'min', dem.min(), 'max', dem.max())
res = dtf.a
lat_c = dtf.f - res * (np.arange(H) + 0.5)
lon_c = dtf.c + res * (np.arange(W) + 0.5)
phi = np.radians(lat_c)
m_per_deg_lat = 111132.92 - 559.82 * np.cos(2 * phi) + 1.175 * np.cos(4 * phi)
m_per_deg_lon = 111412.84 * np.cos(phi) - 93.5 * np.cos(3 * phi)
dy = (m_per_deg_lat * res)[:, None]
dx = (m_per_deg_lon * res)[:, None]
# Horn (1981) 3x3 slope with metric cell size per latitude row
p = np.pad(dem, 1, mode='edge')
a_, b_, c_ = p[:-2, :-2], p[:-2, 1:-1], p[:-2, 2:]
d_, f_ = p[1:-1, :-2], p[1:-1, 2:]
g_, h_, i_ = p[2:, :-2], p[2:, 1:-1], p[2:, 2:]
dzdx = ((c_ + 2 * f_ + i_) - (a_ + 2 * d_ + g_)) / (8 * dx)
dzdy = ((g_ + 2 * h_ + i_) - (a_ + 2 * b_ + c_)) / (8 * dy)
slope = np.degrees(np.arctan(np.hypot(dzdx, dzdy))).astype('float32')
del p, a_, b_, c_, d_, f_, g_, h_, i_, dzdx, dzdy
pix_area_km2 = (dx * dy / 1e6).astype('float64') * np.ones((1, W))
LON, LAT = np.meshgrid(lon_c, lat_c)
didx = cell_index(LON, LAT)
allv = np.ones(dem.shape, bool)
grid['elev_mean_m'], n_dem = agg(didx, dem, allv, 'mean')
grid['elev_min_m'], _ = agg(didx, dem, allv, 'min')
grid['elev_max_m'], _ = agg(didx, dem, allv, 'max')
grid['slope_mean_deg'], _ = agg(didx, slope, allv, 'mean')
grid['n_dem_px'] = n_dem

# ---------------- population (WorldPop 2020 1 km UN-adjusted)
with rasterio.open(R + 'raw/pop/eth_ppp_2020_1km_Aggregated_UNadj.tif') as s:
    pop_full = s.read(1); ptf_full = s.transform; pnod = s.nodata
    eth_total = float(pop_full[pop_full != pnod].sum())
    win = rasterio.windows.from_bounds(max(32.9, s.bounds.left), 6.0, 35.7, 9.0, ptf_full)  # fix 2026-11-16: a window starting west of the raster edge was clipped on read and shifted population 0.1 deg west.round_offsets().round_lengths()
    pop = s.read(1, window=win); ptf = s.window_transform(win)
pvalid = pop != pnod
PH, PW = pop.shape
plon = ptf.c + ptf.a * (np.arange(PW) + 0.5)
plat = ptf.f + ptf.e * (np.arange(PH) + 0.5)
PLON, PLAT = np.meshgrid(plon, plat)
pidx = cell_index(PLON, PLAT)
grid['pop_2020'], n_pop = agg(pidx, pop, pvalid, 'sum')
grid['n_pop_px'] = n_pop
grid['pop_density_km2'] = grid.pop_2020 / grid.cell_area_km2
print('WorldPop ETH total', eth_total, 'pop window', pop.shape, ptf)

# ---------------- soil texture (SoilGrids 2.0, Homolosine 250 m, values in g/kg -> %)
soil = {}
for k, name in [('clay_0_5', 'clay_0-5cm_mean'), ('sand_0_5', 'sand_0-5cm_mean'), ('silt_0_5', 'silt_0-5cm_mean'),
                ('clay_15_30', 'clay_15-30cm_mean'), ('sand_15_30', 'sand_15-30cm_mean'), ('silt_15_30', 'silt_15-30cm_mean')]:
    with rasterio.open(R + f'raw/soil/{name}.tif') as s:
        a = s.read(1); stf = s.transform; scrs = s.crs; snod = s.nodata
    soil[k] = (a, a != snod)
SH, SW = a.shape
sx = stf.c + stf.a * (np.arange(SW) + 0.5)
sy = stf.f + stf.e * (np.arange(SH) + 0.5)
SX, SY = np.meshgrid(sx, sy)
T_s2ll = pyproj.Transformer.from_crs(scrs, 'EPSG:4326', always_xy=True)
SLON, SLAT = T_s2ll.transform(SX, SY)
sidx = cell_index(SLON, SLAT)
for k, (a, v) in soil.items():
    grid[k], n = agg(sidx, a / 10.0, v, 'mean')
grid['n_soil_px'] = n

# ---------------- WRB most probable class (EPSG:4326, 0.0020833 deg)
with rasterio.open(R + 'raw/soil/wrb_MostProbable_native.tif') as s:
    wrb = s.read(1); wtf = s.transform; wnod = s.nodata
leg = pd.read_csv(R + 'data/soilgrids_wrb_legend.csv', encoding='utf-8-sig')
LEG = dict(zip(leg.value, leg.wrb_reference_soil_group))
WH, WW = wrb.shape
wlon = wtf.c + wtf.a * (np.arange(WW) + 0.5); wlat = wtf.f + wtf.e * (np.arange(WH) + 0.5)
WLON, WLAT = np.meshgrid(wlon, wlat)
widx = cell_index(WLON, WLAT)
wvalid = (wrb != wnod) & (widx >= 0)
tab = np.zeros((N, 256), dtype=np.int32)
np.add.at(tab, (widx[wvalid], wrb[wvalid]), 1)
maj = tab.argmax(1); cnt = tab.sum(1)
grid['wrb_class'] = [LEG.get(int(m), NF) if n > 0 else NF for m, n in zip(maj, cnt)]
grid['wrb_class_share'] = np.where(cnt > 0, tab.max(1) / np.maximum(cnt, 1), np.nan)

# ---------------- rivers (OSM waterways)
osm = load(R + 'raw/rivers/osm_waterways_gambella_v2.json')
riv, allw = [], []
for e in osm['elements']:
    if e['type'] != 'way' or len(e.get('geometry', [])) < 2: continue
    ln = LineString([(q['lon'], q['lat']) for q in e['geometry']])
    allw.append(ln)
    if e['tags'].get('waterway') == 'river': riv.append(ln)
print('OSM ways', len(allw), 'rivers', len(riv), 'osm base', osm['osm3s']['timestamp_osm_base'])
riv_l = [to_laea(g) for g in riv]; all_l = [to_laea(g) for g in allw]
t_r, t_a = STRtree(riv_l), STRtree(all_l)
cx, cy = LAEA.transform(grid.lon.values, grid.lat.values)
pts = [Point(x, y) for x, y in zip(cx, cy)]
grid['dist_to_river_km'] = [pt.distance(riv_l[t_r.nearest(pt)]) / 1000 for pt in pts]
grid['dist_to_waterway_km'] = [pt.distance(all_l[t_a.nearest(pt)]) / 1000 for pt in pts]

# ---------------- groundwater: BGS depth-to-groundwater class (modelled, 5 km points)
bg = pd.read_csv(R + 'raw/groundwater/bgs_dtw/182832/DepthToGroundwater/DepthToGroundwater_V2/xyzASCII_dtwmap_v2.txt', sep='\t')
bg = bg[(bg.X > 32.8) & (bg.X < 35.6) & (bg.Y > 6.0) & (bg.Y < 9.0)].reset_index(drop=True)
KEY = {'VS': '0-7', 'S': '7-25', 'SM': '25-50', 'M': '50-100', 'D': '100-250', 'VD': '>250'}
from scipy.spatial import cKDTree
kd = cKDTree(bg[['X', 'Y']].values)
dd, ii = kd.query(grid[['lon', 'lat']].values)
grid['gw_depth_class_bgs_mbgl'] = [KEY[bg.DTWAFRICA_[k]] if d <= 0.03 else NF for d, k in zip(dd, ii)]
grid['groundwater_depth_m'] = NF
print('BGS match max offset deg', dd.max(), grid.gw_depth_class_bgs_mbgl.value_counts().to_dict())

# ---------------- pit note (screening only; rule set by the analyst, see SOURCES_terrain.md)
def usda(sand, silt, clay):
    """USDA soil texture class (standard texture-triangle boundaries), inputs in %"""
    if any(pd.isna(v) for v in (sand, silt, clay)): return NF
    t = sand + silt + clay
    sand, silt, clay = 100 * sand / t, 100 * silt / t, 100 * clay / t
    if silt + 1.5 * clay < 15: return 'sand'
    if silt + 1.5 * clay >= 15 and silt + 2 * clay < 30: return 'loamy sand'
    if (7 <= clay < 20 and sand > 52 and silt + 2 * clay >= 30) or (clay < 7 and silt < 50 and silt + 2 * clay >= 30): return 'sandy loam'
    if 7 <= clay < 27 and 28 <= silt < 50 and sand <= 52: return 'loam'
    if (silt >= 50 and 12 <= clay < 27) or (50 <= silt < 80 and clay < 12): return 'silt loam'
    if silt >= 80 and clay < 12: return 'silt'
    if 20 <= clay < 35 and silt < 28 and sand > 45: return 'sandy clay loam'
    if 27 <= clay < 40 and 20 < sand <= 45: return 'clay loam'
    if 27 <= clay < 40 and sand <= 20: return 'silty clay loam'
    if clay >= 35 and sand > 45: return 'sandy clay'
    if clay >= 40 and silt >= 40: return 'silty clay'
    if clay >= 40 and sand <= 45 and silt < 40: return 'clay'
    return 'unclassified'
grid['usda_texture_15_30'] = [usda(s, si, c) for s, si, c in zip(grid.sand_15_30, grid.silt_15_30, grid.clay_15_30)]
def pit_note(r):
    if pd.isna(r.clay_15_30) or pd.isna(r.sand_15_30): return 'no soil data'
    parts = [f"texture 15-30 cm: {r.usda_texture_15_30} (clay {r.clay_15_30:.0f}%, sand {r.sand_15_30:.0f}%)"]
    if r.clay_15_30 >= 40: parts.append('clay>=40%: heavy clay flag (slow infiltration; shrink-swell possible)')
    elif r.clay_15_30 >= 27: parts.append('clay 27-40%: moderately fine flag')
    if r.sand_15_30 >= 70: parts.append('sand>=70%: loose sandy flag (pit wall support)')
    if r.wrb_class == 'Vertisols': parts.append('WRB Vertisols: swelling clay class')
    if r.wrb_class == 'Fluvisols': parts.append('WRB Fluvisols: floodplain deposit class')
    if r.slope_mean_deg >= 15: parts.append('mean slope>=15 deg: steep flag')
    elif r.slope_mean_deg >= 5: parts.append('mean slope 5-15 deg: sloping')
    else: parts.append('mean slope<5 deg: flat')
    parts.append('groundwater depth NOT FOUND (only BGS modelled class ' + r.gw_depth_class_bgs_mbgl + ' m bgl)')
    return '; '.join(parts)
grid['pit_suitability_note'] = [pit_note(r) for r in grid.itertuples()]

# ---------------- write grid csv
out = grid.copy()
rnd = {'cell_area_km2': 3, 'elev_mean_m': 1, 'elev_min_m': 1, 'elev_max_m': 1, 'slope_mean_deg': 2, 'pop_2020': 1, 'pop_density_km2': 2,
       'clay_0_5': 1, 'sand_0_5': 1, 'silt_0_5': 1, 'clay_15_30': 1, 'sand_15_30': 1, 'silt_15_30': 1, 'wrb_class_share': 2,
       'dist_to_river_km': 2, 'dist_to_waterway_km': 2}
for k, d in rnd.items(): out[k] = out[k].round(d)
out['derived'] = 'yes'
cols = ['cell_id', 'lat', 'lon', 'woreda', 'zone', 'woreda_cod2025', 'zone_cod2025', 'cell_area_km2', 'elev_mean_m', 'elev_min_m', 'elev_max_m',
        'slope_mean_deg', 'pop_2020', 'pop_density_km2', 'clay_0_5', 'sand_0_5', 'silt_0_5', 'clay_15_30', 'sand_15_30', 'silt_15_30',
        'wrb_class', 'wrb_class_share', 'usda_texture_15_30', 'dist_to_river_km', 'dist_to_waterway_km', 'gw_depth_class_bgs_mbgl',
        'groundwater_depth_m', 'pit_suitability_note', 'woreda_match', 'n_dem_px', 'n_pop_px', 'n_soil_px', 'derived']
out[cols].to_csv(R + 'data/gambella_grid_terrain.csv', index=False, encoding='utf-8-sig', na_rep=NF)
print('grid csv rows', len(out), 'NaN counts', out[cols].isna().sum()[out[cols].isna().sum() > 0].to_dict())
print(out[cols].describe().T[['min', 'mean', 'max']])

# ---------------- zonal statistics per polygon (pixel-centre rule, native pixels)
T_ll2s = pyproj.Transformer.from_crs('EPSG:4326', scrs, always_xy=True)
def to_soilcrs(g): return shapely.transform(shapely.segmentize(g, 0.01), lambda c: np.column_stack(T_ll2s.transform(c[:, 0], c[:, 1])))
def labels(polys, tf, shp, conv=None):
    return rasterize([((conv(g) if conv else g), k + 1) for k, g in enumerate(polys)], out_shape=shp, transform=tf, fill=0, dtype='int16')

def zonal(names, polys, level, bset, parents):
    Ld = labels(polys, dtf, dem.shape); Lp = labels(polys, ptf, pop.shape)
    Lw = labels(polys, wtf, wrb.shape); Ls = labels(polys, stf, (SH, SW), to_soilcrs)
    rows = []
    for k, (nm, g) in enumerate(zip(names, polys)):
        m = Ld == k + 1; e = dem[m]; ar = pix_area_km2[m]; A = ar.sum()
        pm = (Lp == k + 1) & pvalid; P = float(pop[pm].sum())
        area = to_laea(g).area / 1e6
        wm = (Lw == k + 1) & (wrb != wnod); vals, cn = np.unique(wrb[wm], return_counts=True)
        order = np.argsort(-cn)
        sm = Ls == k + 1
        def smean(key):
            a, v = soil[key]; q = sm & v
            return round(float(a[q].mean()) / 10, 1) if q.any() else NF
        rows.append(dict(boundary_set=bset, admin_level=level, geography=nm, parent=parents[k], area_km2=round(area, 1),
            pop_2020=round(P), pop_density=round(P / area, 2),
            elev_mean_m=round(float((e * ar).sum() / A), 1), elev_min_m=round(float(e.min()), 1), elev_max_m=round(float(e.max()), 1),
            share_area_below_450m=round(float(ar[e < 450].sum() / A), 4), share_area_450_600m=round(float(ar[(e >= 450) & (e < 600)].sum() / A), 4),
            share_area_above_600m=round(float(ar[e >= 600].sum() / A), 4), slope_mean_deg=round(float((slope[m] * ar).sum() / A), 2),
            dominant_wrb_class=LEG.get(int(vals[order[0]]), NF) if len(vals) else NF,
            dominant_wrb_share=round(float(cn[order[0]] / cn.sum()), 3) if len(vals) else NF,
            second_wrb_class=LEG.get(int(vals[order[1]]), NF) if len(vals) > 1 else '',
            second_wrb_share=round(float(cn[order[1]] / cn.sum()), 3) if len(vals) > 1 else '',
            clay_0_5_mean=smean('clay_0_5'), sand_0_5_mean=smean('sand_0_5'), clay_15_30_mean=smean('clay_15_30'), sand_15_30_mean=smean('sand_15_30'),
            derived='yes',
            note='area = polygon area in LAEA projection; pop = sum of WorldPop 2020 1 km UN-adj pixels whose centre is inside the polygon; density = pop/area; '
                 'elevation, slope = area-weighted over Copernicus GLO-90 pixels (centre inside); WRB = most frequent SoilGrids MostProbable class; clay/sand = mean SoilGrids 250 m pixels, %'))
    return rows
rows = []
rows += zonal(['Gambela (region)'], [adm1], 'ADM1', 'geoBoundaries_2016', ['Ethiopia'])
rows += zonal([a[0] for a in adm2], [a[1] for a in adm2], 'ADM2', 'geoBoundaries_2016', ['Gambela'] * len(adm2))
rows += zonal([a[0] for a in adm3], [a[2] for a in adm3], 'ADM3', 'geoBoundaries_2016', [a[1] for a in adm3])
rows += zonal(['Gambela (region)'], [cod1], 'ADM1', 'COD-AB_2025_v04', ['Ethiopia'])
rows += zonal([a[0] for a in cod3], [a[2] for a in cod3], 'ADM3', 'COD-AB_2025_v04', [a[1] for a in cod3])
# national comparison: population only
eth0 = shape(load(R + 'raw/boundaries/cod_ab/eth_admin0.geojson')['features'][0]['geometry']).buffer(0)
c0 = eth0.centroid
L0 = pyproj.Transformer.from_crs('EPSG:4326', f'+proj=laea +lat_0={c0.y} +lon_0={c0.x} +datum=WGS84 +units=m', always_xy=True)
eth_area = shapely.transform(eth0, lambda c: np.column_stack(L0.transform(c[:, 0], c[:, 1]))).area / 1e6
nat = {k: 'NOT COMPUTED' for k in rows[0]}
nat.update(boundary_set='COD-AB_2025_v04', admin_level='ADM0', geography='Ethiopia (national, comparison)', parent='', area_km2=round(eth_area, 1),
           pop_2020=round(eth_total), pop_density=round(eth_total / eth_area, 2), derived='yes',
           note='pop = sum of all pixels of the WorldPop ETH 2020 1 km UN-adj raster; area = COD-AB admin0 polygon in LAEA; terrain/soil not computed nationally (tiles outside Gambela not downloaded)')
rows.append(nat)
wt = pd.DataFrame(rows)
wt.to_csv(R + 'data/gambella_woreda_terrain.csv', index=False, encoding='utf-8-sig')
print(wt.drop(columns=['note']).to_string())

# ---------------- elevation bands (100 m), region = geoBoundaries ADM1
Ld = labels([adm1], dtf, dem.shape) == 1
Lp = (labels([adm1], ptf, pop.shape) == 1) & pvalid
dem_on_pop = np.zeros(pop.shape, 'float32')
reproject(dem, dem_on_pop, src_transform=dtf, src_crs='EPSG:4326', dst_transform=ptf, dst_crs='EPSG:4326', resampling=Resampling.average)
e = dem[Ld]; ar = pix_area_km2[Ld]
pe = dem_on_pop[Lp]; pp = pop[Lp].astype('float64')
lo = int(math.floor(e.min() / 100) * 100); hi = int(math.floor(e.max() / 100) * 100)
br = []
for b in range(lo, hi + 100, 100):
    m = (e >= b) & (e < b + 100); q = (pe >= b) & (pe < b + 100)
    br.append(dict(band_m=f'{b}-{b + 100}', band_low_m=b, band_high_m=b + 100, area_km2=round(float(ar[m].sum()), 1), share_area=round(float(ar[m].sum() / ar.sum()), 4),
                   population=round(float(pp[q].sum())), share_population=round(float(pp[q].sum() / pp.sum()), 4), derived='yes',
                   note='area: Copernicus GLO-90 pixels (centre inside geoBoundaries Gambela ADM1) by pixel elevation; population: WorldPop 2020 1 km UN-adj pixels (centre inside) by the mean GLO-90 elevation of the 1 km pixel'))
bt = pd.DataFrame(br)
bt.to_csv(R + 'data/gambella_elevation_bands.csv', index=False, encoding='utf-8-sig')
print(bt.drop(columns=['note']).to_string())
print('band totals area', bt.area_km2.sum(), 'pop', bt.population.sum(), 'pixel-sum region pop', pp.sum())

# ---------------- refugee camps
p = R + 'raw/camps/shp2019/Eth_refugee_camps_unhcr_2019.dbf'
b = open(p, 'rb').read()
n, hl, rl = struct.unpack('<IHH', b[4:12])
fields = []; o = 32
while b[o] != 0x0D:
    fields.append((b[o:o + 11].split(b'\0')[0].decode(), b[o + 16])); o += 32
recs = []
for r in range(n):
    rec = b[hl + r * rl: hl + (r + 1) * rl]; pos = 1; d = {}
    for nm, l in fields:
        d[nm] = rec[pos:pos + l].decode('utf-8', 'replace').strip(); pos += l
    recs.append(d)
URL22 = 'https://data.unhcr.org/ar/documents/download/94526'
URLSHP = 'https://data.humdata.org/dataset/19ba356b-170e-430e-82d8-7d1acdb58ffc/resource/b469e2cb-7eb6-4e62-a303-41ad51f9e0b7/download/eth_refugee_camps_unhcr_2019.zip'
# populations read from the table "Refugee's children and adults per camp" (as of 30 June 2022) of the UNHCR infographic; see raw/web/unhcr_94526.txt
P22 = {'Nguenyiel': 110178, 'Tierkidi': 69677, 'Jewi': 65901, 'Kule': 51343, 'Pugnido': 48731, 'Okugo': 13472, 'Pugnido 2': 10343, 'Akula': 1917}
NAME22 = {'Pugnido': 'Pinyudo', 'Pugnido 2': 'Pinyudo 2'}
crow = []
for d in recs:
    lat, lon = float(d['Latitude']), float(d['Longitude'])
    if not (adm1.buffer(0.05).contains(Point(lon, lat))): continue
    nm = d['Name']; ci = cell_index(np.array([lon]), np.array([lat]))[0]
    cid = grid.cell_id[ci] if ci >= 0 else NF
    wp = round(float(grid.pop_2020[ci])) if ci >= 0 else NF
    if ci >= 0:
        nb = grid[(abs(grid.i - grid.i[ci]) <= 1) & (abs(grid.j - grid.j[ci]) <= 1)]
        wp9 = round(float(nb.pop_2020.sum()))
    else: wp9 = NF
    wname = which(adm3, lon, lat)[0][0] if adm1.contains(Point(lon, lat)) else NF
    crow.append(dict(camp=nm, lat=lat, lon=lon, population=P22.get(nm, NF), date='2022-06-30' if nm in P22 else NF,
        url=URL22 if nm in P22 else URLSHP, geography='Gambela Region', admin_level='camp', location_type=d['LocationTy'], active_2019=d['Active'][:1],
        woreda_in_source=d['Woreda'], woreda_geoboundaries=wname, cell_id=cid, worldpop_2020_cell=wp, worldpop_2020_cell_3x3=wp9,
        source_type='official statistics (UNHCR / RRS registration)' if nm in P22 else 'official dataset (OCHA/UNHCR camp points)', derived='no (worldpop_* columns: yes)',
        note=('population: UNHCR infographic "Refugee in Gambella Sub-Office and IDPs in Gambella Region" as of 30 June 2022, table per camp'
              + (f' (camp is named {NAME22[nm]} there)' if nm in NAME22 else '')
              + (' (table total 51,343; map label on the same page 51,342)' if nm == 'Kule' else '')
              + '; ' if nm in P22 else 'no per-camp population in the sources opened; ')
             + f'lat/lon: OCHA Ethiopia "Eth_refugee_camps_unhcr_2019" shapefile on HDX ({URLSHP}); worldpop_2020_cell = WorldPop 2020 population of the 0.05-degree cell holding the point, _3x3 = that cell plus its 8 neighbours inside the region'))
crow.sort(key=lambda r: -(r['population'] if isinstance(r['population'], int) else 0))
api = load(R + 'raw/camps/unhcr_api_geo235_run2.json')['data'][0]
crow.append(dict(camp='ALL camps Gambela sub-office (sum of the 8 camps)', lat='', lon='', population=371562, date='2022-06-30', url=URL22, geography='Gambela Region',
    admin_level='ADM1', location_type='total', active_2019='', woreda_in_source='', woreda_geoboundaries='', cell_id='', worldpop_2020_cell='', worldpop_2020_cell_3x3='',
    source_type='official statistics (UNHCR / RRS registration)', derived='no', note='total printed in the infographic ("371,562 Individuals"); equals the sum of the 8 camp rows'))
crow.append(dict(camp='ALL registered refugees, Gambela (UNHCR data portal)', lat='', lon='', population=int(api['individuals']), date=api['date'],
    url='https://data.unhcr.org/population/get/sublocation?geo_id=235&admin_level=3&population_group=4747,4770,4784,4949', geography='Gambela Region',
    admin_level='ADM1', location_type='total', active_2019='', woreda_in_source='', woreda_geoboundaries='', cell_id='', worldpop_2020_cell='', worldpop_2020_cell_3x3='',
    source_type='official statistics (UNHCR data portal API, source field "' + api['source'] + '")', derived='no',
    note='registered refugees in Gambela: ' + api['population_groups_concat'] + f"; households {api['households']}; per-camp breakdown not returned by the API (camp pages redirect to a privileged login: NOT ACCESSED)"))
ct = pd.DataFrame(crow)
ct.to_csv(R + 'data/gambella_refugee_camps.csv', index=False, encoding='utf-8-sig')
print(ct.drop(columns=['note', 'url', 'source_type']).to_string())

# ---------------- arrays for the maps
np.savez_compressed(R + 'raw/derived/terrain_arrays.npz', dem=dem[::4, ::4], dem_ext=np.array([dtf.c, dtf.c + res * W, dtf.f - res * H, dtf.f]),
                    pop=np.where(pvalid, pop, np.nan), pop_ext=np.array([ptf.c, ptf.c + ptf.a * PW, ptf.f + ptf.e * PH, ptf.f]),
                    pop_area=np.array([box_area_km2(34.2, la, abs(ptf.e) / 2) for la in plat]),
                    wrb=wrb, wrb_ext=np.array([wtf.c, wtf.c + wtf.a * WW, wtf.f + wtf.e * WH, wtf.f]))
print('done')
