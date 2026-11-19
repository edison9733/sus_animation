"""Read the Gambella window of every final CHC CHIRPS3/FLDAS SPEI-12 GeoTIFF (HTTP range requests, no full download).
Usage: python hz03_spei_chc_download.py <root>
Output: raw/hazard/spei_chc/spei12_clip.npz (arr[t,row,col], yyyymm, lats, lons)"""
import sys, os, re, urllib.request, numpy as np, rasterio, time
from rasterio.windows import from_bounds
from concurrent.futures import ThreadPoolExecutor
root = sys.argv[1]
BASE = "https://data.chc.ucsb.edu/products/SPEI/C3_FLDAS_SPEI/12_month/"
out = f"{root}/raw/hazard/spei_chc"; cache = out + "/cache"; os.makedirs(cache, exist_ok=True)
html = urllib.request.urlopen(BASE, timeout=120).read().decode()
open(out + "/listing_12_month.html", "w", encoding="utf-8").write(html)
files = sorted(set(re.findall(r'href="(SPEI_C3_FLDAS_Global_12_(\d{6})\.tif)"', html)))   # final files only (no _PRELIM)
files = [(f, ym) for f, ym in files if int(ym[:4]) <= 2025]
print(len(files), files[0], files[-1], flush=True)
W, S, E, N = 32.5, 5.5, 36.5, 9.5
def fetch(fy):
    f, ym = fy
    c = f"{cache}/{ym}.npy"
    if os.path.exists(c): return
    for attempt in range(12):
        try:
            with rasterio.Env(GDAL_HTTP_TIMEOUT=120, GDAL_HTTP_MAX_RETRY=4, GDAL_HTTP_RETRY_DELAY=15, CPL_VSIL_CURL_NON_CACHED="/vsicurl/https://data.chc.ucsb.edu", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
                with rasterio.open("/vsicurl/" + BASE + f) as ds:
                    win = from_bounds(W, S, E, N, ds.transform).round_offsets().round_lengths()
                    a = ds.read(1, window=win).astype("float32")
                    tr = ds.window_transform(win)
                    assert (tr.c, tr.f, tr.a, tr.e) == (32.5, 9.5, 0.05, -0.05), tr
            break
        except AssertionError: raise
        except Exception as e:
            print("retry", f, e, flush=True); time.sleep(20 + 10 * attempt)
    else:
        raise SystemExit("failed " + f)
    np.save(c + ".tmp.npy", a); os.replace(c + ".tmp.npy", c); print(ym, flush=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(fetch, files))
arr = np.stack([np.load(f"{cache}/{ym}.npy") for _, ym in files])
lons = 32.5 + 0.05 * (np.arange(arr.shape[2]) + 0.5); lats = 9.5 - 0.05 * (np.arange(arr.shape[1]) + 0.5)
np.savez_compressed(out + "/spei12_clip.npz", arr=arr, yyyymm=np.array([int(ym) for _, ym in files]), lats=lats, lons=lons)
print("saved", arr.shape, np.nanmin(arr), np.nanmax(arr), int(np.isnan(arr).sum()))
