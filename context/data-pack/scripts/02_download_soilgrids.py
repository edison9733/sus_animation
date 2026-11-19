"""Step 4 download: SoilGrids 2.0 texture (250 m, native Interrupted Goode Homolosine) read as a window from the ISRIC COG VRTs
https://files.isric.org/soilgrids/latest/data/<prop>/<prop>_<depth>_mean.vrt  -> raw/soil/<prop>_<depth>_mean.tif (unresampled native pixels).
(A first attempt through the WCS returned slightly resampled grids and was discarded.)"""
import pyproj, rasterio
from rasterio.windows import from_bounds
R='C:/Users/janss/OneDrive/Research/gambella/raw/soil/'
covs=['clay_0-5cm_mean','clay_15-30cm_mean','sand_0-5cm_mean','sand_15-30cm_mean','silt_0-5cm_mean','silt_15-30cm_mean']
with rasterio.Env(GDAL_HTTP_TIMEOUT='120',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.vrt,.tif'):
    for c in covs:
        u=f'/vsicurl/https://files.isric.org/soilgrids/latest/data/{c.split("_")[0]}/{c}.vrt'
        with rasterio.open(u) as s:
            t=pyproj.Transformer.from_crs('EPSG:4326',s.crs,always_xy=True)
            xs=[];ys=[]
            for lon in (32.9,34.2,35.5):
                for lat in (6.2,7.5,8.8):
                    x,y=t.transform(lon,lat); xs.append(x); ys.append(y)
            w=from_bounds(min(xs),min(ys),max(xs),max(ys),s.transform).round_offsets().round_lengths()
            a=s.read(1,window=w); p=s.profile.copy()
            p.update(driver='GTiff',height=a.shape[0],width=a.shape[1],transform=s.window_transform(w),compress='deflate')
            for k in ('blockxsize','blockysize','tiled'): p.pop(k,None)
            with rasterio.open(R+c+'.tif','w',**p) as d: d.write(a,1)
            print(c,a.shape,a.dtype,'nodata',s.nodata,'res',s.res,'min',a[a!=s.nodata].min(),'max',a.max(),'n_nodata',(a==s.nodata).sum(),s.tags(1))
