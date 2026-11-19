"""Economy+sanitation: build data/gambella_economy_sanitation.csv (long format, UTF-8 with BOM) from raw/econ_san/.
Run after es01_download.py, es02_epmc.py, es03_download_docs.py, es04_download_hdx.py (all re-run on 2026-11-16).
Usage: python scripts/es06_build.py
Nothing is estimated or interpolated here. Rows with derived=yes are sums / transformations described in the note."""
import os, sys, re, csv, json, math, html, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import xlsx_min
import es05_manual_facts as MF

ROOT = os.path.normpath(os.path.join(HERE, '..'))
RAW = os.path.join(ROOT, 'raw', 'econ_san')
OUT = os.path.join(ROOT, 'data', 'gambella_economy_sanitation.csv')
ACC = '2026-11-16'
COLS = ['theme', 'indicator', 'value', 'unit', 'year', 'geography', 'admin_level', 'disaggregation', 'source', 'source_type', 'url', 'accessed', 'derived', 'note']
rows = []


def add(theme, indicator, value, unit, year, geo, lvl, disagg, source, stype, url, derived='no', note=''):
    if isinstance(value, float):
        value = repr(round(value, 6)).rstrip('0').rstrip('.') if value != int(value) else str(int(value))
    rows.append([theme, indicator, str(value), unit, str(year), geo, lvl, disagg, source, stype, url, ACC, derived, note])


# ------------------------------------------------------------------ World Bank
WB = {'NY.GDP.MKTP.CD': 'current US$', 'NY.GDP.MKTP.KD': 'constant 2015 US$', 'NY.GDP.MKTP.PP.CD': 'current international $ (PPP)',
      'NY.GDP.PCAP.CD': 'current US$ per person', 'NY.GDP.PCAP.KD': 'constant 2015 US$ per person', 'NY.GDP.PCAP.PP.CD': 'current international $ (PPP) per person',
      'NY.GDP.PCAP.PP.KD': 'constant 2021 international $ (PPP) per person', 'NY.GDP.MKTP.KD.ZG': '% per year', 'SI.POV.DDAY': '% of population',
      'SI.POV.NAHC': '% of population', 'SI.POV.GINI': 'index 0-100', 'SP.POP.TOTL': 'persons', 'SP.URB.TOTL.IN.ZS': '% of population'}
for code, unit in WB.items():
    meta, data = json.load(open(os.path.join(RAW, 'worldbank', code + '.json'), encoding='utf-8'))
    theme = 'population' if code.startswith('SP.') else 'economy'
    n = 0
    for d in sorted(data, key=lambda d: d['date']):
        if d['value'] is None: continue
        add(theme, d['indicator']['value'], d['value'], unit, d['date'], 'Ethiopia', 'national', '', 'World Bank World Development Indicators (API v2)',
            'official statistics (international compilation)', 'https://api.worldbank.org/v2/country/ETH/indicator/%s?format=json&per_page=200' % code, 'no',
            'indicator code %s; unit as named in the indicator title; API lastupdated %s' % (code, meta.get('lastupdated', '')))
        n += 1
    if n == 0:
        add(theme, code, 'NOT FOUND', unit, '', 'Ethiopia', 'national', '', 'World Bank World Development Indicators (API v2)', 'official statistics (international compilation)',
            'https://api.worldbank.org/v2/country/ETH/indicator/%s?format=json&per_page=200' % code, 'no', 'API returned no non-null values')

# ------------------------------------------------------------------ DHS Program API
THEME = (('WS_TLET', 'sanitation'), ('WS_TLOC', 'sanitation'), ('WS_ERWA', 'sanitation'), ('WS_MHEX', 'sanitation'), ('WS_HNDW', 'hygiene'), ('WS_MHYG', 'hygiene'),
         ('WS_', 'water'), ('CH_DIAR', 'health'), ('CH_DSTL', 'sanitation'), ('HC_WIXQ', 'economy'), ('HC_ELEC', 'economy'))
surveys = {s['SurveyId']: s for s in json.load(open(os.path.join(RAW, 'dhs', 'surveys.json'), encoding='utf-8'))['Data']}
ind = {i['IndicatorId']: i for i in json.load(open(os.path.join(RAW, 'dhs', 'indicators.json'), encoding='utf-8'))['Data']}


def dhs_rows(path, keep, geo, lvl, bd):
    for x in sorted(json.load(open(path, encoding='utf-8')), key=lambda x: (x['IndicatorOrder'], x['SurveyYear'], x['ByVariableLabel'])):
        if not keep(x): continue
        iid = x['IndicatorId']
        theme = next(t for p, t in THEME if iid.startswith(p))
        s = surveys.get(x['SurveyId'], {})
        meas = (ind.get(iid, {}).get('MeasurementType') or '').lower()
        unit = '%' if meas == 'percent' else (meas or 'see indicator')
        if x['IndicatorType'] in ('D', 'U'): unit = 'number (weighted)' if x['IndicatorType'] == 'D' else 'number (unweighted)'
        note = 'indicator id %s; survey %s (%s, fieldwork %s to %s)' % (iid, x['SurveyId'], s.get('SurveyType', ''), s.get('FieldworkStart', ''), s.get('FieldworkEnd', ''))
        if x.get('DenominatorUnweighted') not in (None, ''): note += '; unweighted denominator %s' % x['DenominatorUnweighted']
        if x.get('CILow') not in (None, ''): note += '; 95%% CI %s-%s' % (x['CILow'], x['CIHigh'])
        add(theme, x['Indicator'], x['Value'], unit, x['SurveyYear'], geo, lvl, x['ByVariableLabel'] or '', 'DHS Program STATcompiler API (%s %s)' % (s.get('SurveyYearLabel', x['SurveyYear']), s.get('SurveyType', 'DHS')),
            'official statistics (household survey)', 'https://api.dhsprogram.com/rest/dhs/data?countryIds=ET&breakdown=%s&indicatorIds=%s&surveyIds=%s&f=json' % (bd, iid, x['SurveyId']), 'no', note)


n0 = len(rows)
dhs_rows(os.path.join(RAW, 'dhs', 'dhs_et_subnational.json'), lambda x: x['CharacteristicCategory'] == 'Region' and x['CharacteristicLabel'] == 'Gambela', 'Gambella Region', 'region', 'subnational')
n_dhs_g = len(rows) - n0; n0 = len(rows)
dhs_rows(os.path.join(RAW, 'dhs', 'dhs_et_national.json'), lambda x: x['CharacteristicLabel'] == 'Total', 'Ethiopia', 'national', 'national')
n_dhs_n = len(rows) - n0

# ------------------------------------------------------------------ JMP (national only)
JP = os.path.join(RAW, 'jmp', 'ETH_household.xlsx')
s = xlsx_min.read_sheet(JP, 'Estimates')
JCOL = {5: 'water', 6: 'water', 7: 'water', 8: 'water', 9: 'water', 15: 'water', 16: 'sanitation', 17: 'sanitation', 18: 'sanitation', 19: 'sanitation', 20: 'sanitation',
        21: 'sanitation', 22: 'sanitation', 23: 'sanitation', 27: 'sanitation', 29: 'hygiene', 30: 'hygiene'}
r = 5
while s.get((r, 1)):
    yr = s.get((r, 2)); setting = s.get((r, 3))
    try: yr = int(float(yr))
    except Exception: r += 1; continue
    if yr <= 2024:
        for c, theme in JCOL.items():
            v = s.get((r, c))
            if v in (None, '', '#N/A'): continue
            head = re.sub(r'\s+', ' ', str(s.get((4, c)))).strip()
            grp = {21: 'improved sanitation incl. shared: ', 22: 'improved sanitation incl. shared: ', 23: 'improved sanitation incl. shared: ', 29: 'handwashing facility: ', 30: 'handwashing facility: '}.get(c, '')
            add(theme, 'JMP: ' + grp + head, float(v), '% of population', yr, 'Ethiopia', 'national', setting.lower(), 'WHO/UNICEF JMP country file Ethiopia (household estimates, updated August 2025)',
                'official statistics (international compilation, modelled trend estimates)', 'https://washdata.org/data/country/ETH/household/download', 'no',
                'sheet "Estimates", column %d; JMP estimates are regression-smoothed from surveys/censuses; rows after 2024 in the sheet were not used' % c + ('; DOUBT: the Introduction sheet says "Insufficient data to estimate safely managed sanitation services at national level" although this cell holds a value' if c == 27 else ''))
    r += 1
add('sanitation', 'JMP sub-national (Gambella) sanitation estimates', 'NOT FOUND', '% of population', '', 'Gambella Region', 'region', '', 'WHO/UNICEF JMP country file Ethiopia (household estimates, updated August 2025)',
    'official statistics (international compilation, modelled trend estimates)', 'https://washdata.org/data/country/ETH/household/download', 'no',
    'The country file sheet "Estimates" has only Total/Rural/Urban rows for Ethiopia; no regional sheet. JMP inequalities/sub-national database on washdata.org was not opened.')

# ------------------------------------------------------------------ Global Data Lab (modelled, interpolated between surveys)
def gdl(f):
    t = open(f, encoding='utf-8').read()
    title = html.unescape(re.search(r'<title>(.*?)</title>', t, re.S).group(1)).split(' - ')[0].strip()
    years = re.findall(r'<th class="year" title="(\d+)"', t)
    out = {}
    for m in re.finditer(r'<tr>\s*<td class="(?:region|country|total)[^"]*">(.*?)</td>(.*?)</tr>', t, re.S):
        name = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        out[name] = [re.sub(r'<[^>]+>', '', v).strip() for v in re.findall(r'<td[^>]*>(.*?)</td>', m.group(2), re.S)]
    ver = re.search(r'"version": "([^"]+)"', t)
    return title, years, out, (ver.group(1) if ver else '')


GDL = [('shdi/table/shdi/ETH/', 'economy', 'index 0-1'), ('shdi/table/lgnic/ETH/', 'economy', 'natural log of 2017 PPP US$ per person'), ('shdi/table/incindex/ETH/', 'economy', 'index 0-1'),
       ('shdi/table/healthindex/ETH/', 'health', 'index 0-1'), ('shdi/table/edindex/ETH/', 'economy', 'index 0-1'), ('shdi/table/lifexp/ETH/', 'health', 'years'),
       ('shdi/table/pop/ETH/', 'population', 'thousand persons'), ('wealth/table/iwi/ETH/', 'economy', 'IWI score 0-100'), ('wealth/table/iwipov35/ETH/', 'economy', '% of households'),
       ('wealth/table/iwipov50/ETH/', 'economy', '% of households'), ('wealth/table/iwipov70/ETH/', 'economy', '% of households'), ('demographics/table/urban/ETH/', 'population', '% of population'),
       ('demographics/table/regpopm/ETH/', 'population', 'million persons')]
for path, theme, unit in GDL:
    f = os.path.join(RAW, 'gdl', path.replace('/', '_') + '.html')
    title, years, tab, ver = gdl(f)
    url = 'https://globaldatalab.org/' + path
    for name, geo, lvl in (('Gambela', 'Gambella Region', 'region'), ('Total', 'Ethiopia', 'national')):
        for y, v in zip(years, tab[name]):
            if v == '': continue
            add(theme, 'GDL: ' + title, v, unit, y, geo, lvl, 'modelled', 'Global Data Lab %s (table view%s)' % ('Subnational HDI' if path.startswith('shdi') else path.split('/')[0].capitalize() + ' database', ', v' + ver if ver else ''),
                'modelled dataset (survey-based, interpolated/extrapolated between survey years)', url, 'no',
                'MODELLED: GDL values are derived from DHS/other survey microdata and national UNDP data, with interpolation between surveys and extrapolation after the last survey; region code ETHr108')
            if 'lgnic' in path:
                add(theme, 'GDL: GNI per capita (2017 PPP US$), back-transformed from log', round(math.exp(float(v)), 0), '2017 PPP US$ per person', y, geo, lvl, 'modelled', 'Global Data Lab Subnational HDI (table view%s)' % (', v' + ver if ver else ''),
                    'modelled dataset (survey-based, interpolated/extrapolated between survey years)', url, 'yes',
                    'DERIVED: exp(log GNI per capita %s) rounded to whole dollars; underlying value is MODELLED by GDL (national GNI distributed over regions with a wealth-index based model)' % v)

# ------------------------------------------------------------------ Kummu et al. downscaled GDP per capita (modelled)
KS = 'Kummu, Kosonen & Masoumzadeh Sayyar (2025) Downscaled gridded global GDP per capita PPP dataset, Zenodo record 18429133 (v. 1990-2024)'
KT = 'modelled dataset (gridded/downscaled)'
KU = 'https://zenodo.org/api/records/18429133/files/%s/content'
for fn, sel, geo_of, lvl in (('tabulated_adm0_gdp_perCapita.csv', lambda r: r.get('iso3') == 'ETH', lambda r: 'Ethiopia', 'national'),
                             ('tabulated_adm2_gdp_perCapita.csv', lambda r: r.get('GID_2', '').startswith('ETH.6.'), lambda r: r['NAME_2'] + ' zone (GADM ' + r['GID_2'] + ')', 'zone')):
    for r in csv.DictReader(open(os.path.join(RAW, 'zenodo_kummu', fn), encoding='utf-8-sig')):
        if not sel(r): continue
        for y in range(1990, 2025):
            v = r.get(str(y))
            if v in (None, '', 'NA'): continue
            note = 'MODELLED. Unit per Zenodo record: 2021 international dollars (PPP). '
            note += ('National series (World Bank based, per adm1_metaData.csv: Ethiopia source "WB", no sub-national input data).' if lvl == 'national' else
                     'Admin-2 value downscaled by the authors\' model from the NATIONAL figure (adm1_metaData.csv lists no reported sub-national GDP for Ethiopia), so zone differences come from the downscaling covariates, not from regional accounts.')
            add('economy', 'GDP per capita PPP, downscaled (Kummu et al.)', v, '2021 international $ (PPP) per person', y, geo_of(r), lvl, 'modelled', KS, KT, KU % fn, 'no', note)

# zonal sum of total GDP raster over the region polygon
try:
    import rasterio, rasterio.mask, numpy as np
    tif = os.path.join(RAW, 'zenodo_kummu', 'rast_gdpTot_1990_2024_5arcmin.tif')
    gj = json.load(open(os.path.join(ROOT, 'data', 'gambella_adm1.geojson'), encoding='utf-8'))
    geoms = [f['geometry'] for f in gj['features']]
    with rasterio.open(tif) as ds:
        arr, _ = rasterio.mask.mask(ds, geoms, crop=True, all_touched=False, filled=False)
        ncell = int((~arr[0].mask).sum()) if hasattr(arr, 'mask') else arr[0].size
        for b in range(ds.count):
            a = arr[b].astype('float64')
            tot = float(np.ma.masked_invalid(a).sum())
            y = 1990 + b
            add('economy', 'Total GDP PPP inside Gambella boundary, zonal sum of gridded GDP (Kummu et al.)', round(tot / 1e6, 1), 'million 2021 international $ (PPP)', y, 'Gambella Region', 'region', 'modelled', KS, KT,
                KU % 'rast_gdpTot_1990_2024_5arcmin.tif', 'yes',
                'DERIVED + MODELLED: sum of 5-arc-min cells of band %d (year %d) whose centre lies inside the geoBoundaries ADM1 polygon data/gambella_adm1.geojson (%d cells with data, rasterio.mask all_touched=False); raster = downscaled GDP per capita x gridded population, so refugees are counted only as far as the population grid includes them; edge cells make the sum approximate' % (b + 1, y, ncell))
        ZONAL = 'ok, %d bands, %d cells' % (ds.count, ncell)
except Exception as e:
    ZONAL = 'FAILED: %r' % e
    add('economy', 'Total GDP PPP inside Gambella boundary, zonal sum of gridded GDP (Kummu et al.)', 'NOT FOUND', '', '', 'Gambella Region', 'region', 'modelled', KS, KT, KU % 'rast_gdpTot_1990_2024_5arcmin.tif', 'no', 'zonal statistics failed: %r' % e)

# ------------------------------------------------------------------ DOSE (reported regional output) - no Gambella
dose_regions = set()
with open(os.path.join(RAW, 'zenodo_dose', 'DOSE_V2.14.csv'), encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        if r.get('GID_0') == 'ETH': dose_regions.add(r['region'])
add('economy', 'Reported regional GDP (gross regional product), DOSE v2.14', 'NOT FOUND', 'LCU / US$', '', 'Gambella Region', 'region', '', 'DOSE - Global dataset of reported subnational economic output v2.14 (Zenodo record 20035157)',
    'compiled official statistics', 'https://zenodo.org/api/records/20035157/files/DOSE_V2.14.csv/content', 'no',
    'DOSE_V2.14.csv has Ethiopia rows only for: %s. No Gambella rows.' % ', '.join(sorted(dose_regions)))

# ------------------------------------------------------------------ HDX COD-PS population (CSA projections)
HS = 'OCHA/HDX COD-PS Ethiopia Subnational Population Statistics (source: Central Statistics Agency projections)'
HT = 'official statistics (projection, redistributed by OCHA)'
HB = 'https://data.humdata.org/dataset/cod-ps-eth'
hmeta = {r['name']: r['url'] for r in json.load(open(os.path.join(RAW, 'hdx', 'cod_ps_eth.json'), encoding='utf-8'))['result']['resources']}
for lvlname, fn, namecol, lvl in (('adm1', 'eth_admpop_adm1_2022_v2.csv', 'admin1Name_en', 'region'), ('adm2', 'eth_admpop_adm2_2022_v2.csv', 'admin2Name_en', 'zone'), ('adm3', 'eth_admpop_adm3_2022_v2.csv', 'admin3Name_en', 'woreda')):
    for r in csv.DictReader(open(os.path.join(RAW, 'hdx', fn), encoding='utf-8-sig')):
        if r.get('admin1Pcode') != 'ET12': continue
        geo = 'Gambella Region' if lvl == 'region' else r[namecol]
        pc = r.get('admin3Pcode') or r.get('admin2Pcode') or r.get('admin1Pcode')
        for col, d in (('T_TL', 'total'), ('M_TL', 'male'), ('F_TL', 'female')):
            add('population', 'Population, projected (COD-PS 2022 v2)', r[col], 'persons', 2022, geo, lvl, d, HS, HT, hmeta[fn], 'no', 'P-code %s; file %s; projection based on the 2007 census, not a count; host population only (refugees not included)' % (pc, fn))
for r in csv.DictReader(open(os.path.join(RAW, 'hdx', 'eth_admpop_adm0_2022_v2.csv'), encoding='utf-8-sig')):
    add('population', 'Population, projected (COD-PS 2022 v2)', r['T_TL'], 'persons', 2022, 'Ethiopia', 'national', 'total', HS, HT, hmeta['eth_admpop_adm0_2022_v2.csv'], 'no', 'file eth_admpop_adm0_2022_v2.csv')
X23 = os.path.join(RAW, 'hdx', 'eth_admpop_2023.xlsx')
for sheet, lvl, namec in (('ETH_admpop_adm0_2023', 'national', 'admin0Name_en'), ('ETH_admpop_adm1_2023', 'region', 'admin1Name_en'), ('ETH_admpop_adm2_2023', 'zone', 'admin2Name_en'), ('ETH_admpop_adm3_2023', 'woreda', 'admin3Name_en')):
    sh = xlsx_min.read_sheet(X23, sheet)
    mc = max(k[1] for k in sh); mr = max(k[0] for k in sh)
    hdr = {sh.get((1, c)): c for c in range(1, mc + 1)}
    for rr in range(2, mr + 1):
        if lvl != 'national' and sh.get((rr, hdr['admin1Pcode'])) != 'ET12': continue
        geo = 'Ethiopia' if lvl == 'national' else ('Gambella Region' if lvl == 'region' else sh.get((rr, hdr[namec])))
        for col, d in (('Total', 'total'), ('Male', 'male'), ('Female', 'female')):
            v = sh.get((rr, hdr[col]))
            if v in (None, ''): continue
            add('population', 'Population, projected (COD-PS 2023)', float(v), 'persons', 2023, geo, lvl, d, HS, HT, hmeta['eth_admpop_2023.xlsx'], 'no', 'sheet %s of eth_admpop_2023.xlsx; projection, host population only' % sheet)
X26 = os.path.join(RAW, 'hdx', 'table_eth_codps_2026.xlsx')
sh = xlsx_min.read_sheet(X26, 'COD_PS')
mc = max(k[1] for k in sh); mr = max(k[0] for k in sh)
hdr = {sh.get((1, c)): c for c in range(1, mc + 1)}
tot = {'Total': 0.0, 'Male': 0.0, 'Female': 0.0}; zt = {}; nw = 0
for rr in range(2, mr + 1):
    if str(sh.get((rr, hdr['admin1_name']))).strip().lower() not in ('gambela', 'gambella'): continue
    nw += 1
    for col, d in (('Total', 'total'), ('Male', 'male'), ('Female', 'female')):
        v = sh.get((rr, hdr[col]))
        if v in (None, ''): continue
        v = float(v); tot[col] += v
        if col == 'Total': zt[sh.get((rr, hdr['admin2_name']))] = zt.get(sh.get((rr, hdr['admin2_name'])), 0.0) + v
        add('population', 'Population, projected (COD-PS 2026)', v, 'persons', 2026, sh.get((rr, hdr['admin3Name'])), 'woreda', d, HS, HT, hmeta['table_eth_codps_2026.xlsx'], 'no',
            'sheet COD_PS, P-code %s, zone %s; based on CSA 2025 projection at woreda level (HDX metadata: reference year 2025, uniform growth rate per region)' % (sh.get((rr, hdr['admin3_pcod'])), sh.get((rr, hdr['admin2_name']))))
for col, d in (('Total', 'total'), ('Male', 'male'), ('Female', 'female')):
    add('population', 'Population, projected (COD-PS 2026)', round(tot[col], 0), 'persons', 2026, 'Gambella Region', 'region', d, HS, HT, hmeta['table_eth_codps_2026.xlsx'], 'yes', 'DERIVED: sum of the %d Gambella woreda rows in sheet COD_PS' % nw)
for z, v in sorted(zt.items()):
    add('population', 'Population, projected (COD-PS 2026)', round(v, 0), 'persons', 2026, str(z), 'zone', 'total', HS, HT, hmeta['table_eth_codps_2026.xlsx'], 'yes', 'DERIVED: sum of woreda rows of this zone in sheet COD_PS')

# ------------------------------------------------------------------ hand-read facts
for (theme, indicator, value, unit, year, geo, lvl, disagg, key, derived, note) in MF.F:
    sname, stype, url = MF.SOURCES[key]
    add(theme, indicator, value, unit, year, geo, lvl, disagg, sname, stype, url, derived, note)

# ------------------------------------------------------------------ gaps (NOT FOUND / NOT ACCESSED)
G = [
 ('economy', 'Official regional GDP / GDP per capita (regional accounts)', 'NOT FOUND', 'Gambella Region', 'region', 'Ethiopia Planning and Development Commission / Ministry of Planning and Development; Gambella BoFED', 'official statistics', '',
  'No official regional GDP series found. Looked at: web search 2026-11-16 (regional GDP, BoFED, PDC), DOSE v2.14 (Ethiopia rows only for Oromia and Amhara), Kummu et al. metadata (Ethiopia: national data only). Only a JICA projection table and modelled products (GDL, Kummu) are in this file.'),
 ('economy', 'Gridded GDP, Wang & Sun (2022) 1-km GDP product: Gambella zonal value', 'NOT ACCESSED', 'Gambella Region', 'region', 'Wang & Sun (2022) Global gridded GDP data set consistent with the shared socioeconomic pathways, Scientific Data', 'modelled dataset (gridded/downscaled)', 'https://doi.org/10.1038/s41597-022-01300-x',
  'Not downloaded in this run (large global rasters); the Kummu et al. product was used for the modelled regional GDP instead.'),
 ('economy', 'Night-time lights (VIIRS/DMSP) tabulated for Gambella', 'NOT FOUND', 'Gambella Region', 'region', 'no ready-made regional table opened', 'modelled dataset (gridded/downscaled)', '',
  'No tabulated regional night-lights series was opened in this run; would need zonal statistics on VIIRS annual composites (EOG, registration required) - not done.'),
 ('population', 'Population, 2007 Population and Housing Census (CSA)', 'NOT ACCESSED', 'Gambella Region', 'region', 'Central Statistical Agency, 2007 Population and Housing Census', 'official statistics', 'https://www.statsethiopia.gov.et/',
  'statsethiopia.gov.et did not resolve/timed out on 2026-11-16 (curl 000, DNS ENOTFOUND); mirrors tried returned 403/404/202. A web-search snippet (Wikipedia, citing the census) gives 307,096 for Gambella - NOT verified against the census report, so not entered as a value.'),
 ('population', 'CSA population projections 2014-2017 / wereda projections (original PDFs)', 'NOT ACCESSED', 'Gambella Region', 'region', 'Central Statistical Agency / Ethiopian Statistics Service', 'official statistics', 'https://www.statsethiopia.gov.et/',
  'Site unreachable (see above). CSA-based projections are included via HDX COD-PS (2022, 2023, 2026) and as quoted by UNICEF (2019) and by a paper (2013 E.C.).'),
 ('sanitation', 'UNHCR WASH dashboard indicators per Gambella camp (current)', 'NOT ACCESSED', 'Gambella refugee camps', 'camp', 'UNHCR WASH dashboard for refugee settings (wash.unhcr.org)', 'UN agency report', 'https://wash.unhcr.org/wash-dashboard-for-refugee-settings/',
  'wash.unhcr.org returned HTTP 301 to https://www.unhcr.org/handbooks/wash/ and the dashboard could not be loaded; data.unhcr.org document search returned HTTP 503. Camp WASH values in this file come from UNHCR PDF documents (2015, 2017-2020, 2025, 2026) only; no values for 2016, 2021-2024.'),
 ('sanitation', 'Ethiopia Socioeconomic Survey (ESS/LSMS) regional sanitation tables', 'NOT ACCESSED', 'Gambella Region', 'region', 'Ethiopian Statistics Service / World Bank LSMS-ISA', 'official statistics (household survey)', 'https://microdata.worldbank.org/index.php/catalog/lsms',
  'ESS survey reports/microdata were not opened in this run (microdata need a World Bank Microdata Library account). The 2019 Mini-DHS regional values are included via the DHS API.'),
 ('sanitation', 'Addis Standard news article on 2025 Gambella cholera outbreak', 'NOT ACCESSED', 'Gambella Region', 'region', 'Addis Standard', 'news', 'https://addisstandard.com/cholera-outbreak-in-gambella-region-claims-14-lives-over-200-cases-reported',
  'HTTP 403 (bot check) - not bypassed. Cholera 2025 figures taken from UNICEF sitrep and WHO AFRO release instead.'),
 ('sanitation', 'Lutheran World Federation article on hygiene in flooded Gambella camps', 'NOT ACCESSED', 'Gambella refugee camps', 'camp', 'Lutheran World Federation Ethiopia', 'NGO self-report', 'https://ethiopia.lutheranworld.org/node/10046', 'HTTP 403 (bot check) - not bypassed.'),
 ('sanitation', 'UNHCR Gambella WASH documents in UNHCR web archive (data2.unhcr.org ids 52303, 30837, 29693)', 'NOT ACCESSED', 'Gambella refugee camps', 'camp', 'UNHCR web archive (MirrorWeb)', 'UN agency report', 'https://webarchive.archive.unhcr.org/20180621143954mp_/https://data2.unhcr.org/fr/documents/download/52303',
  'Archive served a "Verifying your browser" Cloudflare page - not bypassed.'),
 ('sanitation', 'DHS 2024-25 Gambella fact sheet (OF54) PDF', 'NOT ACCESSED', 'Gambella Region', 'region', 'DHS Program', 'official statistics (household survey)', 'https://dhsprogram.com/pubs/pdf/OF54/OF54.Gambella.pdf', 'Guessed URL returned 404; the 2024-25 EDHS regional indicators are included from the DHS API instead.'),
]
for theme, indicator, value, geo, lvl, sname, stype, url, note in G:
    add(theme, indicator, value, '', '', geo, lvl, '', sname, stype, url, 'no', note)

# ------------------------------------------------------------------ write
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(COLS); w.writerows(rows)
import collections
print('rows', len(rows), '| DHS Gambela', n_dhs_g, 'national', n_dhs_n, '| zonal', ZONAL)
print(collections.Counter(r[0] for r in rows))
print(collections.Counter(r[6] for r in rows))
print(collections.Counter(r[9] for r in rows).most_common())
print('NOT FOUND/ACCESSED', sum(1 for r in rows if r[2].startswith('NOT')), '| derived', sum(1 for r in rows if r[12] == 'yes'))
