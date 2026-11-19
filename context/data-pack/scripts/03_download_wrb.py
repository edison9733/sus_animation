"""Step 4 download: SoilGrids 2.0 WRB MostProbable class, native EPSG:4326 grid (0.0020833 deg), window over Gambela, read from the ISRIC VRT/COG.
Writes raw/soil/wrb_MostProbable_native.tif and data/soilgrids_wrb_legend.csv (legend parsed from the VRT raster attribute table)."""
import rasterio, re, csv
from rasterio.windows import from_bounds
R='C:/Users/janss/OneDrive/Research/gambella/'
u='/vsicurl/https://files.isric.org/soilgrids/latest/data/wrb/MostProbable.vrt'
with rasterio.Env(GDAL_HTTP_TIMEOUT='120',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.vrt,.tif'):
    with rasterio.open(u) as s:
        w=from_bounds(32.9,6.2,35.5,8.8,s.transform).round_offsets().round_lengths()
        a=s.read(1,window=w); p=s.profile.copy()
        p.update(driver='GTiff',height=a.shape[0],width=a.shape[1],transform=s.window_transform(w),compress='deflate')
        for k in ('blockxsize','blockysize','tiled'): p.pop(k,None)
        with rasterio.open(R+'raw/soil/wrb_MostProbable_native.tif','w',**p) as d: d.write(a,1)
        print(a.shape,a.dtype,s.nodata,sorted(set(a.ravel().tolist())))
x=open(R+'raw/soil/MostProbable.vrt',encoding='utf-8').read()
rows=re.findall(r'<Row index="\d+">\s*<F>(\d+)</F>\s*<F>([^<]+)</F>',x)
with open(R+'data/soilgrids_wrb_legend.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f); w.writerow(['value','wrb_reference_soil_group','source']); 
    for v,n in rows: w.writerow([v,n,'https://files.isric.org/soilgrids/latest/data/wrb/MostProbable.vrt (GDALRasterAttributeTable)'])
print(len(rows),rows)
