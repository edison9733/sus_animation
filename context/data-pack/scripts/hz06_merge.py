"""Merge drought + flood metrics into data/gambella_grid_hazard.csv (UTF-8 with BOM) and print summary figures.
Usage: python hz06_merge.py <root>"""
import sys, numpy as np, pandas as pd
root = sys.argv[1]; R = f"{root}/raw/hazard/"
d = pd.read_csv(R + "drought_metrics.csv"); f = pd.read_csv(R + "flood_metrics.csv")
assert list(d.cell_id) == list(f.cell_id) and len(d) == 1002
m = d.merge(f.drop(columns=["lat", "lon"]), on="cell_id", validate="one_to_one")
m["cell_area_km2"] = (0.05 * 111.320 * np.cos(np.deg2rad(m.lat))) * (0.05 * 110.574)   # approximate spherical cell area
m["derived"] = "yes"
assert m.drop(columns=[c for c in m if "mean_depth_flooded" in c or "max_depth" in c]).notna().all().all()
m.to_csv(f"{root}/data/gambella_grid_hazard.csv", index=False, encoding="utf-8-sig", float_format="%.4f")
print("rows", len(m), "cols", len(m.columns)); print(list(m.columns))
a = m.cell_area_km2; A = a.sum(); print("grid area km2", round(A, 1))
def aw(c): return (m[c] * a).sum() / A
for c in ["gsw_ever_water_pct", "gsw_occ_5_95_pct", "gsw_occ_ge1_pct", "gsw15_ever_water_pct", "gsw15_occ_5_95_pct", "gsw15_occ_gt95_pct", "jrc_permwater_pct",
          "jrc_rp10_flooded_pct", "jrc_rp100_flooded_pct", "jrc_rp10_flooded_excl_permwater_pct", "jrc_rp100_flooded_excl_permwater_pct",
          "jrc_rp10_depth_ge1m_pct", "jrc_rp100_depth_ge1m_pct", "chirps_mean_annual_mm"]:
    print(f"area-weighted {c}: {aw(c):.3f}   km2-equivalent: {aw(c) * A / 100:.0f}")
for rp in (10, 100):
    wet = m[f"jrc_rp{rp}_flooded_pct"] * a
    print(f"RP{rp} mean depth over flooded area (area-weighted) m:", round((m[f"jrc_rp{rp}_mean_depth_flooded_m"].fillna(0) * wet).sum() / wet.sum(), 3),
          "| median of cell means:", round(m[f"jrc_rp{rp}_mean_depth_flooded_m"].median(), 3))
    for t in (0, 10, 50):
        print(f"  cells with RP{rp} flooded share > {t}%:", int((m[f"jrc_rp{rp}_flooded_pct"] > t).sum()))
print("cells gsw_ever_water>0:", int((m.gsw_ever_water_pct > 0).sum()), ">1%:", int((m.gsw_ever_water_pct > 1).sum()), "| v1.5 >0:", int((m.gsw15_ever_water_pct > 0).sum()), ">1%:", int((m.gsw15_ever_water_pct > 1).sum()))
print("trend annual: cells p<0.05:", int((m.chirps_annual_trend_mk_p < 0.05).sum()), "positive slope cells:", int((m.chirps_annual_trend_mm_per_decade > 0).sum()))
print("trend jjas: cells p<0.05:", int((m.chirps_jjas_trend_mk_p < 0.05).sum()), "positive:", int((m.chirps_jjas_trend_mm_per_decade > 0).sum()))
print("n_years_below80 value counts:", m.chirps_n_years_below80pct.value_counts().sort_index().to_dict())
print("spi<=-1 n years counts:", m.spi3_jja_n_years_le_m1.value_counts().sort_index().to_dict())
print("spi<=-1.5 n years counts:", m.spi3_jja_n_years_le_m1_5.value_counts().sort_index().to_dict())
cols = ["chirps_mean_annual_mm", "chirps_cv_annual_pct", "chirps_share_years_below80pct", "spi3_jja_share_years_le_m1", "spei12_share_months_le_m1", "chirps_dry_months_lt30mm_mean",
        "jrc_rp100_flooded_pct", "gsw_ever_water_pct", "gsw15_ever_water_pct", "lon"]
print(m[cols].corr(method="spearman").round(2).to_string())
q = m[cols + ["chirps_mean_jjas_mm", "chirps_annual_trend_mm_per_decade", "spi3_jja_share_years_le_m1_5", "spei12_share_months_le_m1_5", "gsw_occ_5_95_pct", "gsw15_occ_5_95_pct", "jrc_rp10_flooded_pct"]]
print(q.describe(percentiles=[.05, .5, .95]).T.round(2).to_string())
west = m.lon < 34.5
print("cells lon<34.5:", int(west.sum()), "mean rp100 flooded %:", round(m.loc[west, "jrc_rp100_flooded_pct"].mean(), 1), "| lon>=34.5:", int((~west).sum()), round(m.loc[~west, "jrc_rp100_flooded_pct"].mean(), 1))
print("mean annual mm west/east:", round(m.loc[west, "chirps_mean_annual_mm"].mean()), round(m.loc[~west, "chirps_mean_annual_mm"].mean()))
