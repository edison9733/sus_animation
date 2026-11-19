"""fd05_build_yearly.py - derived yearly tables + README note.
 1. data/gambella_flood_drought_yearly.csv  (from data/gambella_flood_drought_events.csv; GAP rows ignored)
 2. data/ethiopia_flood_drought_yearly.csv  (EM-DAT event rows via OWID, counted by start year)
 3. data/README_flood_drought_events.md
Run: python -P scripts/fd05_build_yearly.py   (after fd04)
"""
import os, csv
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, 'raw', 'fd_rerun')
D = os.path.join(ROOT, 'data')
LOG = {}
for line in open(os.path.join(RR, 'download_log.tsv'), encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 5:
        LOG[p[1]] = p

ev = pd.read_csv(os.path.join(D, 'gambella_flood_drought_events.csv'), encoding='utf-8-sig', dtype=str, keep_default_na=False)
real = ev[~ev.event_id.str.startswith('GAP')].copy()
real['year'] = real['year'].astype(int)


def num(s):
    return pd.to_numeric(s.where(s.str.fullmatch(r'\d+')), errors='coerce')


for c in ('people_affected', 'people_displaced', 'deaths'):
    real[c + '_n'] = num(real[c])
# rows the independent check marked verified=no (figure not specific to Gambella) do not enter the yearly maxima
if 'verified' in real.columns:
    for c in ('people_affected', 'people_displaced', 'deaths'):
        real.loc[real.verified == 'no', c + '_n'] = float('nan')

# one line per event: maximum across its source rows (never a sum across sources)
per_event = real.groupby(['event_id', 'event_type', 'year']).agg(aff=('people_affected_n', 'max'), disp=('people_displaced_n', 'max'),
                                                                 dead=('deaths_n', 'max'), n_src=('source', 'size')).reset_index()
Y0, Y1 = int(real.year.min()), 2026


def tot(df, col):
    if len(df) == 0:
        return 0
    v = df[col].dropna()
    return '' if len(v) == 0 else int(v.sum())


rows = []
for y in range(Y0, Y1 + 1):
    fl = per_event[(per_event.year == y) & (per_event.event_type == 'flood')]
    dr = per_event[(per_event.year == y) & (per_event.event_type == 'drought')]
    src = real[real.year == y]
    notes = []
    if len(fl) == 0 and len(dr) == 0:
        notes.append('no record found in the sources opened (not proof that no flood or drought happened)')
    for _, e in pd.concat([fl, dr]).iterrows():
        miss = [k for k, c in (('affected', 'aff'), ('displaced', 'disp')) if pd.isna(e[c])]
        if miss:
            notes.append('%s: no numeric %s figure' % (e.event_id, '/'.join(miss)))
    if 'verified' in src.columns:
        for _, r in src[src.verified == 'no'].iterrows():
            notes.append('%s: %s row verified=no, its figures are not used here' % (r.event_id, r.source.split(',')[0]))
    rng = src[src.people_affected.str.contains('-') & ~src.people_affected.str.fullmatch(r'\d+')]
    for _, r in rng.iterrows():
        notes.append('%s: affected given as range %s, not summed' % (r.event_id, r.people_affected))
    rows.append(dict(year=y, flood_events=len(fl), drought_events=len(dr), flood_affected=tot(fl, 'aff'), drought_affected=tot(dr, 'aff'),
                     n_sources=len(src), flood_displaced=tot(fl, 'disp'), flood_deaths=tot(fl, 'dead'),
                     geography='Gambella Region, Ethiopia', admin_level='region', derived='yes',
                     note='; '.join(notes)))
ycols = ['year', 'flood_events', 'drought_events', 'flood_affected', 'drought_affected', 'n_sources', 'flood_displaced', 'flood_deaths',
         'geography', 'admin_level', 'derived', 'note']
with open(os.path.join(D, 'gambella_flood_drought_yearly.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=ycols)
    w.writeheader()
    w.writerows(rows)
gy = pd.DataFrame(rows)

# ---------------------------------------------------------------- Ethiopia national, EM-DAT via OWID
pq = os.path.join(RR, 'emdat', 'natural_disasters.parquet')
em = pd.read_parquet(pq).reset_index(drop=True)
EM_COLS = list(em.columns)
et = em[(em.country.astype(str) == 'Ethiopia') & em['type'].astype(str).isin(['Flood', 'Drought'])].copy()
et['type'] = et['type'].astype(str)
lg = LOG['emdat/natural_disasters.parquet']
erows = []
EY0 = int(et.start_year.min())
for y in range(EY0, 2027):
    r = dict(year=y)
    for t, k in (('Flood', 'flood'), ('Drought', 'drought')):
        s = et[(et.start_year == y) & (et['type'] == t)]
        r[k + '_events'] = len(s)
        r[k + '_total_affected'] = int(s.total_affected.fillna(0).sum())
        r[k + '_affected'] = int(s.affected.fillna(0).sum())
        r[k + '_deaths'] = int(s.total_dead.fillna(0).sum())
        r[k + '_events_without_affected_figure'] = int(s.total_affected.isna().sum())
    r.update(geography='Ethiopia', admin_level='country (national)',
             source='EM-DAT (CRED / UCLouvain) event table as republished by Our World in Data, meadow/emdat/2026-10-21/natural_disasters',
             source_type='official statistics / disaster database', url=lg[2], accessed=lg[0][:10], derived='yes',
             note='count of EM-DAT event rows (type Flood / Drought, country Ethiopia) by start_year; total_affected (= affected + injured + homeless), affected and total_dead summed over those rows, missing = 0; multi-year droughts counted once in their start year; OWID yearly n_events not used')
    erows.append(r)
ecols = ['year', 'flood_events', 'drought_events', 'flood_total_affected', 'drought_total_affected', 'flood_affected', 'drought_affected',
         'flood_deaths', 'drought_deaths', 'flood_events_without_affected_figure', 'drought_events_without_affected_figure',
         'geography', 'admin_level', 'source', 'source_type', 'url', 'accessed', 'derived', 'note']
with open(os.path.join(D, 'ethiopia_flood_drought_yearly.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=ecols)
    w.writeheader()
    w.writerows(erows)
ey = pd.DataFrame(erows)

# ---------------------------------------------------------------- README
n_ev = per_event.groupby('event_type').size().to_dict()
fy = gy[gy.flood_events > 0]
dy = gy[gy.drought_events > 0]
n_empty = len(gy) - len(gy[(gy.flood_events > 0) | (gy.drought_events > 0)])
L = []
A = L.append
A('# Gambella flood and drought records - notes')
A('')
A('Built by `scripts/fd01_download.py` -> `fd02_download_web.py` -> `fd03_to_text.py` -> `fd04_build_events.py` -> `fd05_build_yearly.py`.')
A('Downloads of this run are in `raw/fd_rerun/` with `download_log.tsv` (UTC time, file, URL, HTTP status, bytes). `accessed` in the CSVs is the UTC date of that download.')
A('')
A('## Files')
A('| file | rows | what |')
A('|---|---|---|')
A('| `gambella_flood_drought_events.csv` | %d | one row per event x source: %d source rows for %d events (%d flood, %d drought) + %d gap rows (`event_id` starts with `GAP`, values `NOT FOUND` / `NOT ACCESSED`) |'
  % (len(ev), len(real), len(per_event), n_ev.get('flood', 0), n_ev.get('drought', 0), len(ev) - len(real)))
A('| `gambella_flood_drought_yearly.csv` | %d | %d-%d, derived from the event file |' % (len(gy), Y0, Y1))
A('| `ethiopia_flood_drought_yearly.csv` | %d | Ethiopia national, EM-DAT event rows by start year, %d-2026 |' % (len(ey), EY0))
A('')
A('## Read this before using the numbers')
A('- **Absence of a record is not absence of a flood.** %d of the %d years have 0 events only because no source that could be opened mentions Gambella for that year. The sources themselves say the Baro, Akobo, Gilo and Alwero overflow almost every year (Abaya et al. 2009; UNDP-EUE 1999). Reporting is much denser after 2019, so the series must not be read as a trend in flood frequency.' % (n_empty, len(gy)))
A('- The same event appears on several rows (shared `event_id`), one per source. Figures were **not merged**. Sources disagree, count different things (affected / displaced / relief beneficiaries / camp population) and report at different dates.')
A('- Yearly `flood_affected`, `drought_affected`, `flood_displaced`, `flood_deaths` are derived (`derived=yes`): for each event the **largest** numeric value among its source rows, then summed over the events that start in that year. Empty = there is an event but no numeric figure; 0 = no event recorded. `n_sources` = number of source rows in that year.')
A('- `people_affected` is not one consistent quantity. Examples: 1996 = relief beneficiaries (89,968); 2014 = population of the flooded camp (about 40,000); 2022 = either the non-displaced affected (79,631, OCHA via news / GDACS) or affected and displaced together (over 187,000, Protection Cluster); 2002 drought = people needing food aid in 2003 (58,400).')
A('- Event boundaries are my choice (`event_id`): one id per rainy-season flood unless place and month clearly differ (2023 June vs September; 2024 August vs September in Jikawo; 2025 July Gambella city vs September Nuer zone). 2024-01 and 2024-02 may be one season counted twice.')
A('- Independent check 2026-11-16 (`scripts/fdcheck01_redownload.py`, `fdcheck02_context.py`, `fdcheck03_apply.py`; downloads in `raw/fd_check2/`): column `verified` (yes / no / not_checked) with the reason at the end of `note`. Rows with verified=no are kept but left out of the yearly maxima. Fixed: 2007 IFRC Table 1 Gambella value is 20,000, not 36,090 (36,090 was the five-region total). Build order: fd04 -> fdcheck03 -> fd05.')
A('- Every hand-entered row has `evidence_quote`; `fd04` checks that each quote is present in the downloaded document text before it writes the CSV. GDACS and DFO rows are generated from the downloaded JSON.')
A('- DFO and some GDACS rows are matched to Gambella only by polygon centroid or by date/figure match (`derived` says so); the DFO archive has no place names and the copy used ends in October 2021.')
A('- EM-DAT (OWID copy) columns: %s. No location text, so no Gambella rows can be taken from it.' % ', '.join(EM_COLS))
A('- Drought: no source gives a Gambella drought impact figure after 2002. Drought rows are rain-failure / food-insecurity episodes; the 2016 row is indirect and the 2025 row is a remote-sensing alert.')
A('- Latrines: the only explicit latrine damage records are Leitchuor camp 2014 (MSF: latrines overflowed, some collapsed; no count) and a GDACS text for October 2019 (latrines, school buildings and health facilities damaged; region field "Gambela, Somali Region"; no count). The 2022 flood sources count water schemes (250-270 non-functional), health facilities and schools, not latrines.')
A('- Doubt flagged in the file: 11,749 displaced is attached to April-July 2021 by one news article, while web search snippets (documents not opened) attach it to August 2020.')
A('- Not accessed (bot checks / timeouts, not bypassed): reliefweb.int and its API, addisstandard.com, thenewhumanitarian.org, floodlist.com, dtm.iom.int, edrmc.gov.et, the original DFO files. See the GAP rows.')
A('')
A('## Years with records')
A('- flood: ' + ', '.join(str(y) for y in fy.year))
A('- drought / rain failure: ' + ', '.join(str(y) for y in dy.year))
A('')
open(os.path.join(D, 'README_flood_drought_events.md'), 'w', encoding='utf-8').write('\n'.join(L))

print(gy[(gy.flood_events > 0) | (gy.drought_events > 0)][ycols[:8]].to_string(index=False))
print(len(gy), 'yearly rows;', len(ey), 'Ethiopia rows; EM-DAT Ethiopia flood/drought event rows:', len(et), et['type'].value_counts().to_dict())
print(ey[['flood_events', 'drought_events', 'flood_total_affected', 'drought_total_affected', 'flood_deaths', 'drought_deaths']].sum().to_dict())
print(ey[ey.year >= 2015][ecols[:9]].to_string(index=False))
