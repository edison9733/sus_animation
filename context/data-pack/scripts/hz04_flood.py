"""Flood metrics per 0.05-degree grid cell from JRC Global Surface Water v1.4 and JRC/CEMS-GloFAS river flood hazard v2.1.2.
Usage: python hz04_flood.py <root>   -> raw/hazard/flood_metrics.csv"""
import sys, numpy as np, pandas as pd, rasterio
from rasterio.windows import from_bounds, Window
root = sys.argv[1]; R = f"{root}/raw/hazard/"
g = pd.read_csv(R + "grid_cells.csv")
W, S, E, N = 33.0, 6.3, 35.4, 8.7           # covers all cell edges (cells 33.025..35.375, 6.325..8.675)
assert g.lon.min() - 0.025 >= W - 1e-9 and g.lon.max() + 0.025 <= E + 1e-9 and g.lat.min() - 0.025 >= S - 1e-9 and g.lat.max() + 0.025 <= N + 1e-9
nx, ny = round((E - W) / 0.05), round((N - S) / 0.05)
ci = np.round((g.lon.values - 0.025 - W) / 0.05).astype(int); rj = np.round((N - (g.lat.values + 0.025)) / 0.05).astype(int)

# ---- JRC Global Surface Water (0.00025 deg, pixel-aligned with the grid: 200 x 200 pixels per cell)
def gsw(path):
    with rasterio.open(R + path) as ds:
        c0 = round((W - ds.transform.c) / ds.transform.a); r0 = round((ds.transform.f - N) / -ds.transform.e)
        a = ds.read(1, window=Window(c0, r0, nx * 200, ny * 200))
    return a.reshape(ny, 200, nx, 200).transpose(0, 2, 1, 3).reshape(ny, nx, 40000)
def pct(mask): return (100.0 * mask.mean(axis=2))[rj, ci]
# v1.4 = 1984-2021 (prefix gsw_), v1.5 = 1984-2024 (prefix gsw15_)
for pre, fe, fo in (("gsw_", "gsw/extent_30E_10Nv1_4_2021.tif", "gsw/occurrence_30E_10Nv1_4_2021.tif"),
                    ("gsw15_", "gsw_v15/extent_30E_10N_v1_5_2024.tif", "gsw_v15/occurrence_30E_10N_v1_5_2024.tif")):
    ext = gsw(fe); occ = gsw(fo)
    assert ext.max() <= 1 and occ.max() <= 100, "unexpected codes (255 = no data) inside window"
    g[pre + "ever_water_pct"] = pct(ext == 1)
    g[pre + "occ_ge1_pct"] = pct(occ >= 1)
    g[pre + "occ_5_95_pct"] = pct((occ >= 5) & (occ <= 95))
    g[pre + "occ_gt95_pct"] = pct(occ > 95)
    g[pre + "occ_ge50_pct"] = pct(occ >= 50)
    g[pre + "occ_max_pct"] = occ.max(axis=2)[rj, ci]
del ext, occ

# ---- JRC / CEMS-GloFAS river flood hazard (3 arc-second; not aligned -> pixels assigned to the cell containing the pixel centre)
def load(fn):
    with rasterio.open(R + "jrc_flood/" + fn) as ds:
        win = from_bounds(W - 0.01, S - 0.01, E + 0.01, N + 0.01, ds.transform).round_offsets().round_lengths()
        a = ds.read(1, window=win); tr = ds.window_transform(win); nod = ds.nodata
    xs = tr.c + tr.a * (np.arange(a.shape[1]) + 0.5); ys = tr.f + tr.e * (np.arange(a.shape[0]) + 0.5)
    cx = np.floor((xs - W) / 0.05).astype(int); cy = np.floor((N - ys) / 0.05).astype(int)
    okx = (cx >= 0) & (cx < nx); oky = (cy >= 0) & (cy < ny)
    a = a[oky][:, okx]; idx = (cy[oky][:, None] * nx + cx[okx][None, :]).ravel()
    return a.ravel(), idx, nod
def agg(v, idx): return np.bincount(idx, weights=v.astype("float64"), minlength=nx * ny).reshape(ny, nx)[rj, ci]
pw, idx, nod = load("ID150_N10_E30_permanent_water.tif")
npx = agg(np.ones_like(pw, dtype="float64"), idx)
perm = (pw == 1)
g["jrc_n_pixels"] = npx.astype(int)
g["jrc_permwater_pct"] = 100 * agg(perm, idx) / npx
for rp in (10, 100):
    d, idx2, nod = load(f"ID150_N10_E30_RP{rp}_depth.tif"); assert np.array_equal(idx, idx2)
    wet = (d != nod) & (d > 0)
    nwet = agg(wet, idx)
    g[f"jrc_rp{rp}_flooded_pct"] = 100 * nwet / npx
    g[f"jrc_rp{rp}_flooded_excl_permwater_pct"] = 100 * agg(wet & ~perm, idx) / npx
    with np.errstate(invalid="ignore", divide="ignore"):
        g[f"jrc_rp{rp}_mean_depth_flooded_m"] = np.where(nwet > 0, agg(np.where(wet, d, 0), idx) / nwet, np.nan)
    g[f"jrc_rp{rp}_mean_depth_cell_m"] = agg(np.where(wet, d, 0), idx) / npx
    g[f"jrc_rp{rp}_depth_ge1m_pct"] = 100 * agg(wet & (d >= 1), idx) / npx
    g[f"jrc_rp{rp}_max_depth_m"] = [d[wet & (idx == k)].max() if n > 0 else np.nan for k, n in zip(rj * nx + ci, nwet)] if rp == 100 else np.nan
    print(rp, "zero-depth pixels (valid, depth==0):", int(((d != nod) & (d == 0)).sum()), "wet:", int(wet.sum()))
g = g.drop(columns=["jrc_rp10_max_depth_m"])
g.drop(columns=["i", "j"]).to_csv(R + "flood_metrics.csv", index=False)
print(g.describe().T.to_string())
