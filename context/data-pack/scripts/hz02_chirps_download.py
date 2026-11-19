"""Download CHIRPS v2.0 africa_monthly tifs 1981-2025, clip to the Gambella window, keep only the clip.
Usage: python hz02_chirps_download.py <root>
Output: raw/hazard/chirps_clip_1981_2025.npz (arr[year, month, row, col] mm/month; lats, lons = cell centres)"""
import sys, os, gzip, io, urllib.request, time, numpy as np, rasterio
from rasterio.windows import from_bounds
root = sys.argv[1]
BASE = "https://data.chc.ucsb.edu/products/CHIRPS/v2.0/africa_monthly/tifs/chirps-v2.0.{y}.{m:02d}.tif.gz"
W, S, E, N = 32.5, 5.5, 36.5, 9.5
tmpd = f"{root}/raw/hazard/chirps_cache"; os.makedirs(tmpd, exist_ok=True)
years = list(range(1981, 2026))
def fetch(ym):
    y, m = ym
    cache = f"{tmpd}/{y}_{m:02d}.npy"
    if os.path.exists(cache): return
    url = BASE.format(y=y, m=m)
    for attempt in range(6):
        try:
            raw = urllib.request.urlopen(url, timeout=180).read(); break
        except Exception as e:
            print("retry", url, e, flush=True); time.sleep(5)
    else:
        raise SystemExit("failed " + url)
    data = gzip.decompress(raw)
    with rasterio.MemoryFile(data) as mf, mf.open() as ds:
        win = from_bounds(W, S, E, N, ds.transform).round_offsets().round_lengths()
        a = ds.read(1, window=win).astype("float32")
        tr = ds.window_transform(win)
        meta = (tr.c, tr.f, tr.a, tr.e, ds.nodata)
    np.save(f"{tmpd}/meta_{y}_{m:02d}.npy", np.array(meta, dtype="float64"))
    np.save(cache + ".tmp.npy", a); os.replace(cache + ".tmp.npy", cache)
    print(y, m, len(raw), flush=True)
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(6) as ex:
    list(ex.map(fetch, [(y, m) for y in years for m in range(1, 13)]))
metas = np.array([np.load(f"{tmpd}/" + f) for f in sorted(os.listdir(tmpd)) if f.startswith("meta_")])
assert np.allclose(metas[:, :4], metas[0, :4]), "clip windows differ between files"   # column 4 = nodata tag (NaN when the file has none)
np.save(f"{tmpd}/meta.npy", metas[0])
arr = None
for yi, y in enumerate(years):
    for m in range(1, 13):
        a = np.load(f"{tmpd}/{y}_{m:02d}.npy")
        if arr is None: arr = np.full((len(years), 12) + a.shape, np.nan, "float32")
        arr[yi, m - 1] = a
x0, y0, dx, dy, nod = np.load(f"{tmpd}/meta.npy")
lons = x0 + dx * (np.arange(arr.shape[3]) + 0.5); lats = y0 + dy * (np.arange(arr.shape[2]) + 0.5)
arr[arr < 0] = np.nan   # CHIRPS no-data is -9999 (files carry no nodata tag); rainfall cannot be negative
np.savez_compressed(f"{root}/raw/hazard/chirps_clip_1981_2025.npz", arr=arr, lats=lats, lons=lons, years=np.array(years))
print("saved", arr.shape, lons[:3], lats[:3], "nodata", nod, "nan count", int(np.isnan(arr).sum()))
