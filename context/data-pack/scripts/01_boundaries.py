"""Step 1: select Gambela ADM1/2/3 from geoBoundaries gbOpen ETH (2016) and, as a check, OCHA COD-AB (valid_on 2025-01-01).
Inputs (downloaded with curl, see SOURCES_terrain.md): raw/boundaries/geoBoundaries-ETH-ADM{1,2,3}.geojson, raw/boundaries/cod_ab/eth_admin{1,2,3}.geojson
Outputs: data/gambella_adm{1,2,3}.geojson (geoBoundaries), data/gambella_adm{1,2,3}_cod2025.geojson (COD-AB), data/gambella_boundary_comparison.csv
"""
import json, csv
from shapely.geometry import shape
from shapely.ops import transform
import pyproj
R='C:/Users/janss/OneDrive/Research/gambella/'
b=R+'raw/boundaries/'
laea=pyproj.Transformer.from_crs('EPSG:4326','+proj=laea +lat_0=7.5 +lon_0=34.2 +datum=WGS84 +units=m',always_xy=True).transform
def km2(g): return transform(laea,g).area/1e6
def load(p): return json.load(open(p,encoding='utf-8'))
def dump(feats,p):
    json.dump({'type':'FeatureCollection','features':feats},open(p,'w',encoding='utf-8'),ensure_ascii=False)
a1=load(b+'geoBoundaries-ETH-ADM1.geojson')
g=[f for f in a1['features'] if f['properties']['shapeName']=='Gambela']
G=shape(g[0]['geometry']).buffer(0)
g[0]['properties']['area_km2_derived']=round(km2(G),1)
dump(g,R+'data/gambella_adm1.geojson')
rows=[]
rows.append(dict(source='geoBoundaries gbOpen ETH 2016',level='ADM1',name='Gambela',parent='',code=g[0]['properties']['shapeID'],area_km2=round(km2(G),1),note='area derived: LAEA projection of polygon'))
zones={}
a2=load(b+'geoBoundaries-ETH-ADM2.geojson'); sel=[]
for f in a2['features']:
    s=shape(f['geometry']).buffer(0)
    if G.contains(s.centroid):
        f['properties']['area_km2_derived']=round(km2(s),1); sel.append(f); zones[f['properties']['shapeName']]=s
        rows.append(dict(source='geoBoundaries gbOpen ETH 2016',level='ADM2',name=f['properties']['shapeName'],parent='Gambela',code=f['properties']['shapeID'],area_km2=round(km2(s),1),note='area derived'))
dump(sel,R+'data/gambella_adm2.geojson')
a3=load(b+'geoBoundaries-ETH-ADM3.geojson'); sel=[]
for f in a3['features']:
    s=shape(f['geometry']).buffer(0)
    if G.contains(s.centroid):
        z=[n for n,zs in zones.items() if zs.contains(s.representative_point())]
        f['properties']['zone']=z[0] if z else 'NOT FOUND'
        f['properties']['area_km2_derived']=round(km2(s),1); sel.append(f)
        rows.append(dict(source='geoBoundaries gbOpen ETH 2016',level='ADM3',name=f['properties']['shapeName'],parent=f['properties']['zone'],code=f['properties']['shapeID'],area_km2=round(km2(s),1),note='area derived; zone = ADM2 polygon containing woreda representative point'))
dump(sel,R+'data/gambella_adm3.geojson')
# COD-AB
for lvl in (1,2,3):
    d=load(b+f'cod_ab/eth_admin{lvl}.geojson')
    sel=[f for f in d['features'] if f['properties']['adm1_name']=='Gambela']
    dump(sel,R+f'data/gambella_adm{lvl}_cod2025.geojson')
    for f in sel:
        p=f['properties']; s=shape(f['geometry']).buffer(0)
        rows.append(dict(source='OCHA COD-AB ETH (valid_on 2025-01-01)',level=f'ADM{lvl}',name=p[f'adm{lvl}_name'],parent=p.get(f'adm{lvl-1}_name','') if lvl>1 else '',code=p[f'adm{lvl}_pcode'],area_km2=round(km2(s),1),note=f"area derived (same LAEA); file attribute area_sqkm={p['area_sqkm']:.1f}"))
    if lvl==1:
        C=shape(sel[0]['geometry']).buffer(0)
        inter=transform(laea,G).intersection(transform(laea,C)).area/1e6
        print('ADM1 area gB',km2(G),'COD',km2(C),'intersection',inter,'union',km2(G)+km2(C)-inter)
        rows.append(dict(source='comparison',level='ADM1',name='Gambela overlap geoBoundaries vs COD-AB',parent='',code='',area_km2=round(inter,1),note=f'intersection area; = {100*inter/km2(G):.1f}% of geoBoundaries polygon and {100*inter/km2(C):.1f}% of COD-AB polygon (derived)'))
with open(R+'data/gambella_boundary_comparison.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.DictWriter(fh,fieldnames=['source','level','name','parent','code','area_km2','note']); w.writeheader(); w.writerows(rows)
for r in rows: print(r['source'][:14],r['level'],r['name'],'|',r['parent'],r['area_km2'])
