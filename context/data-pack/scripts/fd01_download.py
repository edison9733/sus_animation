"""fd01_download.py - re-download the API sources for the Gambella flood/drought event file.
Saves into raw/fd_rerun/<source>/ and appends to raw/fd_rerun/download_log.tsv.
Run: python -P scripts/fd01_download.py
Downloaded files are data only."""
import os, sys, json, time, subprocess, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'raw', 'fd_rerun')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-download'
LOG = os.path.join(OUT, 'download_log.tsv')

def fetch(sub, name, url, force=False):
    d = os.path.join(OUT, sub); os.makedirs(d, exist_ok=True)
    out = os.path.join(d, name)
    if os.path.exists(out) and os.path.getsize(out) > 0 and not force:
        return out
    r = subprocess.run(['curl', '-sLg', '-m', '120', '-A', UA, '-o', out, '-w', '%{http_code}\t%{size_download}\t%{content_type}', url],
                       capture_output=True, text=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write('%s\t%s/%s\t%s\t%s\n' % (datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), sub, name, url, r.stdout))
    print(sub, name, r.stdout.replace('\t', ' '))
    time.sleep(0.5)
    return out

def load(p):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('  not json:', p, e); return None

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # 1 EM-DAT via OWID
    fetch('emdat', 'natural_disasters.parquet', 'https://catalog.ourworldindata.org/meadow/emdat/2026-10-21/natural_disasters/natural_disasters.parquet')
    # 2 IFRC GO: appeals + events for Ethiopia (country id 65); dtype 12 flood, 20 drought, 27 pluvial/flash flood, 21 food insecurity
    for dt in (12, 20, 27, 21):
        fetch('ifrc', 'appeal_c65_dtype%d.json' % dt, 'https://goadmin.ifrc.org/api/v2/appeal/?country=65&dtype=%d&limit=200' % dt)
        fetch('ifrc', 'event_c65_dtype%d.json' % dt, 'https://goadmin.ifrc.org/api/v2/event/?countries__in=65&dtype=%d&limit=200' % dt)
    # field reports mentioning Gambella
    fetch('ifrc', 'field_report_c65_flood.json', 'https://goadmin.ifrc.org/api/v2/field-report/?countries__in=65&dtype=12&limit=200')
    # 3 GDACS: event list for Ethiopia, floods + droughts
    fetch('gdacs', 'eth_fl_dr.json', 'https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventlist=FL;DR&country=ETH&fromdate=2000-01-01&todate=2026-11-16&alertlevel=green;orange;red&pagesize=100&pagenumber=1')
    fetch('gdacs', 'eth_fl_dr_p2.json', 'https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventlist=FL;DR&country=ETH&fromdate=2000-01-01&todate=2026-11-16&alertlevel=green;orange;red&pagesize=100&pagenumber=2')
    for p in ('eth_fl_dr.json', 'eth_fl_dr_p2.json'):
        j = load(os.path.join(OUT, 'gdacs', p))
        for x in (j or {}).get('features', []):
            pr = x['properties']
            if 'Ethiopia' not in (pr.get('country') or ''): continue
            fetch('gdacs', '%s_%s.json' % (pr['eventtype'], pr['eventid']),
                  'https://www.gdacs.org/gdacsapi/api/events/geteventdata?eventtype=%s&eventid=%s' % (pr['eventtype'], pr['eventid']))
    # 4 Dartmouth Flood Observatory archive (ArcGIS mirror; floodobservatory.colorado.edu file links returned 236-byte stubs on 2026-11-15)
    base = 'https://services1.arcgis.com/AXaYBvnJsB5Q7sDF/ArcGIS/rest/services/Global_Archive_of_large_flood_events/FeatureServer/0/query'
    fetch('dfo', 'dfo_layer0.json', base.replace('/query', '') + '?f=json')
    # polygons intersecting the Gambella bounding box (32.9-35.5E, 5.9-8.8N), attributes only
    fetch('dfo', 'dfo_bbox_gambella.json', base + '?where=1%3D1&geometry=32.9,5.9,35.5,8.8&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json')
    fetch('dfo', 'dfo_ethiopia.json', base + "?where=COUNTRY+LIKE+%27%25thiopia%25%27+OR+OTHERCOUNT+LIKE+%27%25thiopia%25%27&outFields=*&returnGeometry=false&f=json")
    fetch('dfo', 'dfo_maxdate.json', base + '?where=1%3D1&outStatistics=%5B%7B%22statisticType%22%3A%22max%22%2C%22onStatisticField%22%3A%22BEGAN%22%2C%22outStatisticFieldName%22%3A%22maxbegan%22%7D%2C%7B%22statisticType%22%3A%22count%22%2C%22onStatisticField%22%3A%22ID%22%2C%22outStatisticFieldName%22%3A%22n%22%7D%5D&f=json')
    # 5 ReliefWeb API (may need a registered appname)
    fetch('reliefweb', 'rw_api_gambella_flood.json', 'https://api.reliefweb.int/v1/reports?appname=gambella-student-research&query[value]=Gambella%20flood&filter[field]=country.iso3&filter[value]=eth&limit=100&fields[include][]=title&fields[include][]=date.original&fields[include][]=source.shortname&fields[include][]=url&sort[]=date:desc')
    fetch('reliefweb', 'rw_api_v2_gambella_flood.json', 'https://api.reliefweb.int/v2/reports?appname=gambella-student-research&query[value]=Gambella%20flood&limit=100&fields[include][]=title&fields[include][]=date.original&fields[include][]=source.shortname&fields[include][]=url&sort[]=date:desc')
    fetch('reliefweb', 'rw_api_disasters_eth.json', 'https://api.reliefweb.int/v1/disasters?appname=gambella-student-research&filter[field]=country.iso3&filter[value]=eth&limit=200&fields[include][]=name&fields[include][]=glide&fields[include][]=date.event&fields[include][]=type.name&fields[include][]=url')
