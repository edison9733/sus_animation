"""Drought metrics per grid cell (CHIRPS v2.0, 1981-2025) + CHC SPEI-12 comparison + region-average yearly series.
Usage: python hz05_drought.py <root>  -> raw/hazard/drought_metrics.csv, data/gambella_rainfall_yearly.csv"""
import sys, os, numpy as np, pandas as pd
from scipy import stats
root = sys.argv[1]; R = f"{root}/raw/hazard/"
g = pd.read_csv(R + "grid_cells.csv")
z = np.load(R + "chirps_clip_1981_2025.npz"); arr, lats, lons, years = z["arr"], z["lats"], z["lons"], z["years"]
col = np.round((g.lon.values - lons[0]) / 0.05).astype(int); row = np.round((lats[0] - g.lat.values) / 0.05).astype(int)
assert np.allclose(lons[col], g.lon.values, atol=1e-4) and np.allclose(lats[row], g.lat.values, atol=1e-4), "CHIRPS pixel centres do not match grid"   # CHIRPS geotransform is stored in float32 precision (offset ~1e-6 deg)
P = arr[:, :, row, col].astype("float64")            # year x month x cell
assert not np.isnan(P).any() and (P >= 0).all()
ny, nc = P.shape[0], P.shape[2]
ann = P.sum(axis=1); jjas = P[:, 5:9].sum(axis=1); jja = P[:, 5:8].sum(axis=1)

def spi_gamma(x):
    """SPI of a 1-D series: 2-parameter gamma (loc fixed at 0) fitted by maximum likelihood (scipy.stats.gamma.fit, floc=0)
    to the non-zero values; mixed distribution H = q + (1-q)*G for zeros (q = share of zeros); SPI = norm.ppf(H)."""
    x = np.asarray(x, float); nz = x > 0; q = 1 - nz.mean()
    a, _, sc = stats.gamma.fit(x[nz], floc=0)
    H = q + (1 - q) * stats.gamma.cdf(x, a, loc=0, scale=sc)
    return stats.norm.ppf(np.clip(H, 1e-6, 1 - 1e-6))

def mann_kendall_p(x):
    """Two-sided Mann-Kendall p-value, normal approximation with tie correction and continuity correction."""
    x = np.asarray(x); n = len(x)
    s = sum(np.sign(x[j + 1:] - x[j]).sum() for j in range(n - 1))
    _, cnt = np.unique(x, return_counts=True)
    var = (n * (n - 1) * (2 * n + 5) - (cnt * (cnt - 1) * (2 * cnt + 5)).sum()) / 18.0
    zz = 0.0 if s == 0 else (s - np.sign(s)) / np.sqrt(var)
    return 2 * (1 - stats.norm.cdf(abs(zz)))

yrs = years.astype(float)
out = g[["cell_id", "lat", "lon"]].copy()
m = ann.mean(axis=0)
out["chirps_mean_annual_mm"] = m
out["chirps_mean_jjas_mm"] = jjas.mean(axis=0)
out["chirps_jjas_share_pct"] = 100 * jjas.mean(axis=0) / m
out["chirps_cv_annual_pct"] = 100 * ann.std(axis=0, ddof=1) / m
out["chirps_min_annual_mm"] = ann.min(axis=0)
out["chirps_min_annual_year"] = years[ann.argmin(axis=0)]
out["chirps_p10_annual_mm"] = np.percentile(ann, 10, axis=0)
out["chirps_dry_months_lt30mm_mean"] = (P < 30).sum(axis=1).mean(axis=0)
below = ann < 0.8 * m
out["chirps_n_years_below80pct"] = below.sum(axis=0)
out["chirps_share_years_below80pct"] = 100 * below.mean(axis=0)
spi = np.column_stack([spi_gamma(jja[:, k]) for k in range(nc)])       # year x cell
out["spi3_jja_n_years_le_m1"] = (spi <= -1).sum(axis=0)
out["spi3_jja_share_years_le_m1"] = 100 * (spi <= -1).mean(axis=0)
out["spi3_jja_n_years_le_m1_5"] = (spi <= -1.5).sum(axis=0)
out["spi3_jja_share_years_le_m1_5"] = 100 * (spi <= -1.5).mean(axis=0)
ts = [stats.theilslopes(ann[:, k], yrs) for k in range(nc)]
out["chirps_annual_trend_mm_per_decade"] = [10 * t[0] for t in ts]
out["chirps_annual_trend_mk_p"] = [mann_kendall_p(ann[:, k]) for k in range(nc)]
out["chirps_jjas_trend_mm_per_decade"] = [10 * stats.theilslopes(jjas[:, k], yrs)[0] for k in range(nc)]
out["chirps_jjas_trend_mk_p"] = [mann_kendall_p(jjas[:, k]) for k in range(nc)]

# ---- CHC CHIRPS3/FLDAS SPEI-12
sp_ok = os.path.exists(R + "spei_chc/spei12_clip.npz")
if sp_ok:
    s = np.load(R + "spei_chc/spei12_clip.npz"); S, ym = s["arr"], s["yyyymm"]
    c2 = np.round((g.lon.values - s["lons"][0]) / 0.05).astype(int); r2 = np.round((s["lats"][0] - g.lat.values) / 0.05).astype(int)
    assert np.allclose(s["lons"][c2], g.lon.values, atol=1e-6) and np.allclose(s["lats"][r2], g.lat.values, atol=1e-6)
    S = S[:, r2, c2].astype("float64")                 # month x cell
    print("SPEI months", len(ym), ym.min(), ym.max(), "NaN values", int(np.isnan(S).sum()), "non-finite", int((~np.isfinite(S)).sum()))
    valid = np.isfinite(S)
    out["spei12_n_months"] = valid.sum(axis=0)
    out["spei12_share_months_le_m1"] = 100 * ((S <= -1) & valid).sum(axis=0) / valid.sum(axis=0)
    out["spei12_share_months_le_m1_5"] = 100 * ((S <= -1.5) & valid).sum(axis=0) / valid.sum(axis=0)
    out["spei12_min"] = np.nanmin(np.where(valid, S, np.nan), axis=0)
out.to_csv(R + "drought_metrics.csv", index=False)
print(out.describe().T.to_string())

# ---- region-average yearly series (cos-latitude weighted mean over the 1002 cells)
w = np.cos(np.deg2rad(g.lat.values)); w = w / w.sum()
ra = ann @ w; rj = jjas @ w; rjja = jja @ w
yr = pd.DataFrame({"year": years, "annual_mm": ra, "jjas_mm": rj, "anomaly_pct": 100 * (ra / ra.mean() - 1),
                   "jjas_anomaly_pct": 100 * (rj / rj.mean() - 1), "jja_mm": rjja,
                   "spi_jja": spi_gamma(rjja), "spi_jja_cell_mean": spi @ w,
                   "share_cells_spi_jja_le_m1_pct": 100 * ((spi <= -1) @ w),
                   "share_cells_annual_below80pct": 100 * (below @ w)})
if sp_ok:
    for y in years:
        k = np.where(ym == y * 100 + 12)[0]; mm = np.where(ym // 100 == y)[0]
        if len(k):
            v = S[k[0]]; ok = np.isfinite(v)
            yr.loc[yr.year == y, "spei12_dec_mean"] = (v[ok] * w[ok]).sum() / w[ok].sum()
            yr.loc[yr.year == y, "share_cells_spei12_dec_le_m1_pct"] = 100 * ((v[ok] <= -1) * w[ok]).sum() / w[ok].sum()
        if len(mm) == 12:
            yr.loc[yr.year == y, "spei12_mean_of_12_months"] = np.nanmean(np.nansum(np.where(np.isfinite(S[mm]), S[mm], 0) * w, axis=1) / (np.isfinite(S[mm]) * w).sum(axis=1))
yr["source"] = "CHIRPS v2.0 africa_monthly (rain); CHC CHIRPS3/FLDAS SPEI-12 (spei columns)"
yr["derived"] = "yes"
yr.to_csv(f"{root}/data/gambella_rainfall_yearly.csv", index=False, encoding="utf-8-sig", float_format="%.3f")
print(yr.round(2).to_string())
print("region mean annual", ra.mean(), "jjas", rj.mean(), "cv", 100 * ra.std(ddof=1) / ra.mean(),
      "trend mm/dec", 10 * stats.theilslopes(ra, yrs)[0], "MK p", mann_kendall_p(ra))
