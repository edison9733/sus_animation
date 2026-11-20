"""Draw the two map images for the film (scene 2 "map" and scene 5 "zones") so the colours follow the region's own borders.

The team's maps (data pack an04_sanitation_priority.py) paint each 0.05° grid cell as a square, so the colour
spills over the district lines in steps. This redraws the same grid data (sanitation_priority_grid.csv) as a
smooth surface and cuts it to the Gambela outline (geoBoundaries ETH ADM3 2016, the source the team used),
with the district lines, names, Gambela town and the refugee camps on top, like the original.

It keeps the original framing exactly (415.8 px per degree, the top-left corner at 33.0° E, 8.7° N), so the
film's camera moves, ring and tags still land in the same places. It writes the images at twice the size
(2000 px wide) so they stay sharp when the camera zooms in.

Usage: python make_scene_maps.py <repo root>    (needs numpy, pandas, scipy, shapely, matplotlib, Pillow)
Writes animation/motion/assets/gambella-priority.webp and gambella-zones.webp.
"""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.colors import ListedColormap
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from scipy.ndimage import gaussian_filter
from PIL import Image
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
DP = ROOT / "context/data-pack"
OUT = ROOT / "animation/motion/assets"
K = 2                                   # output scale: 2 = 2000 px wide
LON0, LAT1, SPAN = 33.0, 8.7, 2.4       # the original axes: 33.0–35.4° E, 6.3–8.7° N
AX_W, AX_H = 998 * K, 1007 * K          # the axes in pixels (415.8 px/deg across, 419.6 down: aspect 1/cos 7.7°)
CELL = 0.05
SIGMA = 0.5                             # smoothing, in grid cells

g = pd.read_csv(DP / "data_csv/sanitation_priority_grid.csv", encoding="utf-8-sig")
camps = pd.read_csv(DP / "data_csv/gambella_refugee_camps.csv", encoding="utf-8-sig")
camps = camps[pd.to_numeric(camps.population, errors="coerce").notna() & camps.lat.notna()].copy()
camps["population"] = camps.population.astype(float)
adm3 = json.load(open(DP / "data_geo/gambella_adm3.geojson", encoding="utf-8"))
polys = [(f["properties"]["shapeName"], shape(f["geometry"]).buffer(0)) for f in adm3["features"]]
region = unary_union([p for _, p in polys]).buffer(0)

# ---- the grid as an array, cell k covering [LON0 + k*CELL, LON0 + (k+1)*CELL)
n = int(round(SPAN / CELL))
col = np.floor((g.lon - LON0) / CELL + 1e-9).astype(int)
row = np.floor((LAT1 - g.lat) / CELL + 1e-9).astype(int)
def grid(values):
    a = np.full((n, n), np.nan)
    a[row, col] = values
    return a

# ---- a fine pixel grid over the axes; each pixel looks up its cell, then everything is smoothed
px_lon = LON0 + (np.arange(AX_W) + 0.5) / AX_W * SPAN
px_lat = LAT1 - (np.arange(AX_H) + 0.5) / AX_H * SPAN
ci = np.clip(((px_lon - LON0) / CELL).astype(int), 0, n - 1)
ri = np.clip(((LAT1 - px_lat) / CELL).astype(int), 0, n - 1)
sig = SIGMA * AX_W / n                  # in pixels
has_cell = ~np.isnan(grid(np.ones(len(g))))

def fill_nearest(a, ok):
    """Copy each missing cell from the nearest cell that has data, so the surface reaches the border before it is cut."""
    from scipy.ndimage import distance_transform_edt
    idx = distance_transform_edt(~ok, return_distances=False, return_indices=True)
    return a[tuple(idx)]

def fine(a):
    return gaussian_filter(a[np.ix_(ri, ci)], sig, mode="nearest")

# priority (0-1, blank where fewer than 2 people/km²)
pr = grid(g.priority.values)
pr_ok = ~np.isnan(pr)
prio = np.clip(fine(fill_nearest(pr, pr_ok)), 0, 1)
sparse_p = fine((has_cell & ~pr_ok).astype(float) + (~has_cell) * 0.0) > 0.5

# toilet zones: smooth each zone's share, then take the largest
ZN = ["A: raised / sealed above-ground unit", "B: raised slab + lined pit", "C: lined pit (clay), low flood",
      "D: steep ground, site-specific", "E: too sparse for a programme"]
zi = grid(g.toilet_zone.map({z: i for i, z in enumerate(ZN)}).values)
zi = fill_nearest(zi, ~np.isnan(zi)).astype(int)
zone = np.argmax(np.stack([fine((zi == k).astype(float)) for k in range(len(ZN))]), axis=0)

# ---- drawing
PAL = ["#1F5A8C", "#7DB3DA", "#D2AD6A", "#8C6A5A", "#E4E0D8"]   # the film's zone colours (scene-zones.js), E pale
PALE = "#ECE7DD"                                                    # inside the region, fewer than 2 people/km²
BG = "#F0F0F0"
plt.rcParams["font.family"] = "Arial"

def region_path():
    verts, codes = [], []
    for p in (region.geoms if region.geom_type == "MultiPolygon" else [region]):
        for ring in [p.exterior, *p.interiors]:
            xy = np.asarray(ring.coords)
            verts += xy.tolist(); codes += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
    return MPath(verts, codes)

def draw(rgba, name, canvas_h, off_x, off_y, legend=False):
    W, H = 1000 * K, canvas_h * K
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=BG)
    ax = fig.add_axes([off_x * K / W, (H - off_y * K - AX_H) / H, AX_W / W, AX_H / H])
    ax.set_facecolor(BG)
    ext = [LON0, LON0 + SPAN, LAT1 - SPAN, LAT1]
    clip = PathPatch(region_path(), transform=ax.transData, facecolor="none", edgecolor="none")
    ax.add_patch(clip)
    im = ax.imshow(rgba, extent=ext, origin="upper", interpolation="bilinear", zorder=1)
    im.set_clip_path(clip)
    for nm, p in polys:
        for q in (p.geoms if p.geom_type == "MultiPolygon" else [p]):
            x, y = q.exterior.xy
            ax.plot(x, y, color="#2B2B2B", lw=0.5 * 4 * K / 2, alpha=0.85, zorder=3, solid_joinstyle="round")
        if p.area > .03:
            c = p.representative_point()
            ax.text(c.x, c.y, nm, fontsize=6.5 * 4 * K / 2, ha="center", va="center", color="#111", zorder=5,
                    path_effects=[patheffects.withStroke(linewidth=2.2 * K, foreground=(1, 1, 1, 0.75))])
    for p in (region.geoms if region.geom_type == "MultiPolygon" else [region]):
        x, y = p.exterior.xy
        ax.plot(x, y, color="#1E1E1E", lw=1.4 * K, zorder=4, solid_joinstyle="round")
    ax.plot(34.59, 8.25, marker="*", color="white", mec="black", mew=0.8 * K, ms=12 * 4 * K / 2, zorder=6)
    ax.scatter(camps.lon, camps.lat, s=(20 + camps.population / 800) * (4 * K / 2) ** 2, marker="o", facecolor="none",
               edgecolor="#c2185b", lw=1.6 * 4 * K / 2, zorder=6)
    if legend:
        zp = g.groupby("toilet_zone").pop_2020.sum()
        h = [plt.Rectangle((0, 0), 1, 1, color=c) for c in PAL] + [plt.Line2D([], [], marker="o", ls="", mfc="none", mec="#c2185b", mew=1.6 * 2 * K, ms=9 * 2 * K)]
        ax.legend(h, [f"{z}  ({zp.get(z, 0) / 1000:,.0f}k people)" for z in ZN] + ["refugee camp (size = registered refugees)"],
                  fontsize=7.5 * 2 * K, loc="lower left", framealpha=.92, borderpad=0.6, handlelength=1.6)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("auto")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color("#222"); s.set_linewidth(0.8 * K)
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "m.png"
        fig.savefig(png, dpi=100, facecolor=BG); plt.close(fig)
        Image.open(png).convert("RGB").save(OUT / name, "WEBP", quality=88, method=6)
    print("wrote", OUT / name)

cmap = plt.get_cmap("YlOrRd")
rgba = cmap(prio)
rgba[sparse_p] = matplotlib.colors.to_rgba(PALE)
draw(rgba, "gambella-priority.webp", 1010, 1, 4)

zrgba = ListedColormap(PAL)(zone)
draw(zrgba, "gambella-zones.webp", 1015, 2, 1, legend=True)
