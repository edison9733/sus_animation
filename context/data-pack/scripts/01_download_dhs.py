"""Download DHS Program API data for Ethiopia (national + subnational) for WASH, diarrhoea, wealth indicators.
Usage: python scripts/01_download_dhs.py   -> raw/dhs/dhs_et_<breakdown>.json"""
import json, urllib.request, urllib.parse, os, time
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw', 'dhs')
ind = json.load(open(os.path.join(ROOT, 'indicators.json'), encoding='utf-8'))['Data']
ids = sorted({i['IndicatorId'] for i in ind if i['IndicatorId'].startswith(('WS_', 'CH_DIAR_C', 'CH_DSTL_C_SAF', 'HC_WIXQ', 'HC_ELEC_H_ELC', 'HC_ELEC_P_ELC'))})
print(len(ids), 'indicator ids')
for bd in ('national', 'subnational'):
    out = []
    for k in range(0, len(ids), 25):
        chunk = ','.join(ids[k:k+25])
        page = 1
        while True:
            url = ('https://api.dhsprogram.com/rest/dhs/data?countryIds=ET&breakdown=%s&indicatorIds=%s&f=json&perpage=1000&page=%d'
                   % (bd, chunk, page))
            for attempt in range(4):
                try:
                    d = json.load(urllib.request.urlopen(url, timeout=120)); break
                except Exception as e:
                    print('retry', e); time.sleep(5)
            out += d['Data']
            if page >= d['TotalPages']: break
            page += 1
    json.dump(out, open(os.path.join(ROOT, 'dhs_et_%s.json' % bd), 'w', encoding='utf-8'))
    print(bd, len(out))
