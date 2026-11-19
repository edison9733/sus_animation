"""Build the fixed 0.05-degree Gambella grid (cell centres inside the geoBoundaries Gambela ADM1 polygon).
Usage: python hz01_grid.py <root>"""
import sys, json, numpy as np, pandas as pd
from shapely.geometry import shape, Point
from shapely.prepared import prep
root = sys.argv[1]
g = json.load(open(f"{root}/raw/hazard/geoBoundaries-ETH-ADM1.geojson", encoding="utf-8"))
feat = [f for f in g["features"] if f["properties"]["shapeName"] in ("Gambela", "Gambella")]
assert len(feat) == 1
poly = shape(feat[0]["geometry"]); pp = prep(poly)
minx, miny, maxx, maxy = poly.bounds
print("bounds", poly.bounds)
rows = []
for i in range(0, 200):
    lon = round(33.025 + 0.05 * i, 3)
    if lon < minx - 0.1 or lon > maxx + 0.1: continue
    for j in range(0, 200):
        lat = round(5.025 + 0.05 * j, 3)
        if lat < miny - 0.1 or lat > maxy + 0.1: continue
        if pp.contains(Point(lon, lat)):
            rows.append((f"{lat:.3f}_{lon:.3f}", lat, lon, i, j))
df = pd.DataFrame(rows, columns=["cell_id", "lat", "lon", "i", "j"])
df.to_csv(f"{root}/raw/hazard/grid_cells.csv", index=False)
print(len(df), df.lat.min(), df.lat.max(), df.lon.min(), df.lon.max())
