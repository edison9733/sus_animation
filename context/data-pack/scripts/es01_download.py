"""Economy + sanitation: download all machine-readable sources into raw/econ_san/.
Usage: python scripts/es01_download.py [wb] [dhs] [gdl] [jmp] [zenodo]   (no args = all)
Every request is logged to raw/econ_san/download_log.tsv (utc time, file, url, http status, bytes)."""
import json, os, sys, time, urllib.request, urllib.error, datetime

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw', 'econ_san'))
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-download'
os.makedirs(ROOT, exist_ok=True)


def fetch(rel, url, tries=3, timeout=180):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    status, n = '000', 0
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read(); status = str(r.status)
            open(path, 'wb').write(data); n = len(data)
            break
        except urllib.error.HTTPError as e:
            status = str(e.code)
            if e.code in (401, 403, 404): break
            time.sleep(4)
        except Exception as e:
            status = 'ERR:' + type(e).__name__
            time.sleep(4)
    with open(os.path.join(ROOT, 'download_log.tsv'), 'a', encoding='utf-8') as f:
        f.write('%s\t%s\t%s\t%s\t%d\n' % (datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), rel, url, status, n))
    print(status, n, rel)
    return path if status == '200' else None


WB = ['NY.GDP.MKTP.CD', 'NY.GDP.MKTP.KD', 'NY.GDP.MKTP.PP.CD', 'NY.GDP.PCAP.CD', 'NY.GDP.PCAP.KD',
      'NY.GDP.PCAP.PP.CD', 'NY.GDP.PCAP.PP.KD', 'NY.GDP.MKTP.KD.ZG', 'SI.POV.DDAY', 'SI.POV.NAHC',
      'SI.POV.GINI', 'SP.POP.TOTL', 'SP.URB.TOTL.IN.ZS']


def wb():
    for i in WB:
        fetch('worldbank/%s.json' % i, 'https://api.worldbank.org/v2/country/ETH/indicator/%s?format=json&per_page=200' % i)


DHS_PREFIX = ('WS_', 'CH_DIAR_C', 'CH_DSTL_C_SAF', 'HC_WIXQ', 'HC_ELEC_H_ELC', 'HC_ELEC_P_ELC')


def dhs():
    fetch('dhs/indicators.json', 'https://api.dhsprogram.com/rest/dhs/indicators?f=json&perpage=5000')
    fetch('dhs/surveys.json', 'https://api.dhsprogram.com/rest/dhs/surveys?countryIds=ET&f=json')
    ind = json.load(open(os.path.join(ROOT, 'dhs', 'indicators.json'), encoding='utf-8'))['Data']
    ids = sorted({i['IndicatorId'] for i in ind if i['IndicatorId'].startswith(DHS_PREFIX)})
    print(len(ids), 'DHS indicator ids')
    for bd in ('national', 'subnational'):
        out, urls = [], []
        for k in range(0, len(ids), 25):
            chunk = ','.join(ids[k:k + 25]); page = 1
            while True:
                url = ('https://api.dhsprogram.com/rest/dhs/data?countryIds=ET&breakdown=%s&indicatorIds=%s&f=json&perpage=1000&page=%d'
                       % (bd, chunk, page))
                p = fetch('dhs/parts/%s_%03d_p%d.json' % (bd, k, page), url)
                d = json.load(open(p, encoding='utf-8'))
                out += d['Data']
                if page >= d['TotalPages']: break
                page += 1
        json.dump(out, open(os.path.join(ROOT, 'dhs', 'dhs_et_%s.json' % bd), 'w', encoding='utf-8'))
        print(bd, len(out), 'rows')


def gdl():
    for code in ('shdi', 'lgnic', 'incindex', 'healthindex', 'edindex', 'lifexp', 'esch', 'msch', 'pop'):
        fetch('gdl/shdi_%s.html' % code, 'https://globaldatalab.org/shdi/table/%s/ETH/' % code)


def jmp():
    fetch('jmp/ETH_household.xlsx', 'https://washdata.org/data/country/ETH/household/download')


def zenodo():
    base = 'https://zenodo.org/api/records/18429133/files/%s/content'
    for f in ('tabulated_adm0_gdp_perCapita.csv', 'tabulated_adm1_gdp_perCapita.csv', 'tabulated_adm2_gdp_perCapita.csv', 'adm1_metaData.csv'):
        fetch('zenodo_kummu/' + f, base % f)
    fetch('zenodo_dose/DOSE_V2.14.csv', 'https://zenodo.org/api/records/20035157/files/DOSE_V2.14.csv/content')


if __name__ == '__main__':
    todo = sys.argv[1:] or ['wb', 'dhs', 'gdl', 'jmp', 'zenodo']
    for t in todo:
        globals()[t]()
