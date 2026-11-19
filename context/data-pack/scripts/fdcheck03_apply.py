"""fdcheck03_apply.py - writes the independent check (2026-11-16) into data/gambella_flood_drought_events.csv.
Adds column 'verified' (yes / no / not_checked) and appends the reason to 'note'.
Basis: scripts/fdcheck01_redownload.py run with FDCHECK_OUT=raw/fd_check2 (fresh re-download of every source URL,
own PyMuPDF / HTML text, quote + number test: raw/fd_check2/check_results.tsv) plus reading every figure in context
with scripts/fdcheck02_context.py, and the DFO / GDACS JSON records read directly.
Run after fd04 and before fd05:  python scripts/fdcheck03_apply.py"""
import os, csv
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data', 'gambella_flood_drought_events.csv')
d = pd.read_csv(P, dtype=str, keep_default_na=False, encoding='utf-8-sig')
if 'verified' in d.columns:
    d = d.drop(columns=['verified'])
    d['note'] = d['note'].str.replace(r' \| CHECK 2026-11-16:.*$', '', regex=True)

# keyed by (event_id, source prefix) so the result does not depend on row order
SPECIAL = {
    ('GAM-FL-2007-01', 'IFRC Operations Update no. 1'): ('yes', 'value corrected 36,090 -> 20,000: 36,090 is the five-region total of Table 1; Gambella row = 20,000 (PyMuPDF table extraction of the re-downloaded PDF).'),
    ('GAM-FL-2007-01', 'Dartmouth Flood Observatory'): ('no', 'values 42,000 displaced / 17 dead match DFO record 3146, but its flood polygon is 714,220 km2 (most of Ethiopia; Gambella ADM1 is about 30,600 km2), so the figures are not Gambella-specific. Gambella sources for 2007 give 11,886 displaced and 1 dead (29-31 July) and over 8,000 displaced (Sept). Excluded from yearly maxima.'),
    ('GAM-FL-1998-01', 'Dartmouth Flood Observatory'): ('yes', 'values match DFO record 1430 (66,000 displaced, 3 dead, 10-17 Aug 1998); centroid 34.02E 7.75N inside Gambella (re-tested), polygon 28,907 km2 is about the size of Gambella. No place name in DFO, so attribution stays a centroid match; no second source found.'),
    ('GAM-FL-2008-01', 'Dartmouth Flood Observatory'): ('yes', 'values match DFO record 3367 and the Reuters report of 25 Aug 2008 (18,000 displaced, 3 dead); centroid about 14 km outside Gambella (re-tested).'),
    ('GAM-FL-2007-01', 'Mail & Guardian'): ('yes', '11,886 displaced and 1 killed confirmed in the article text (number printed with a non-breaking space).'),
    ('GAM-FL-2021-01', 'Gambella Community Development Council'): ('yes', 'text confirmed: the article attaches 11,749 displaced to April-July 2021; the year doubt in the note remains (not resolved).'),
    ('GAM-FL-2019-01', 'GDACS'): ('yes', 'GDACS sendai records for region Gambela: affected 3,324, displaced 11,128, text "a total of 14,452 people were affected of which 11,128 individuals displaced" (3,324 = 14,452 - 11,128). Differs from OCHA 1,405 displaced in Gambella town (3 Oct 2019); GDACS gives no date of its OCHA figure.'),
    ('GAM-FL-2023-02', 'Addis Standard via allAfrica'): ('yes', 'HTTP 403 again, but the returned page carries the article teaser with both quotes; no number to check.'),
    ('GAM-FL-2025-01', 'Addis Standard via allAfrica'): ('yes', 'HTTP 403 again, but the returned page carries the article teaser: "More than 50 homes have been damaged in Gambella city".'),
    ('GAM-FL-2024-02', 'Prensa Latina'): ('yes', 'text says "More than 20 thousand people displaced"; Jikawo named; 9 Sept 2024.'),
    ('GAM-DR-1990-01', 'Ayenew & Shimels'): ('yes', 'range confirmed: "between 15,000 and 20, 000 people in Akobo had been affected" (1990).'),
}
GAP = {
    'GAP-FL-2026': ('yes', 'GDACS FL list for Ethiopia 2026-01-01..2026-11-16 re-queried: one event (9-11 Mar 2026, 37.26E 6.17N, outside Gambella); UNICEF mid-year 2026 sitrep re-downloaded: no Gambella flood mention.'),
    'GAP-DFO-ORIGINAL': ('yes', 'FloodArchive.xlsx re-tested: HTTP 404, 236 bytes.'),
    'GAP-DR-GAMBELLA': ('not_checked', 'IFRC GO drought list re-downloaded (HTTP 200) but its 16 events were not re-read; web searches not repeated.'),
    'GAP-EDRMC': ('yes', 'edrmc.gov.et re-tested: no connection (HTTP 000).'),
    'GAP-EMDAT-LOCATION': ('yes', 'parquet re-downloaded: columns have no location text ("region" = continent, "event" = disease / volcano names only).'),
    'GAP-NEWS-BLOCKED': ('yes', 'addisstandard.com ?p=29184 re-tested: HTTP 403 (not bypassed). Other sites not re-tested.'),
    'GAP-RELIEFWEB': ('yes', 'reliefweb.int disaster page re-tested: HTTP 202 with empty body; API v2 now answers HTTP 400 without an appname (not bypassed).'),
    'GAP-UNHCR-CAMPS': ('not_checked', 'search for camp flood reports not repeated.'),
}
ver, why = [], []
for _, r in d.iterrows():
    v = None
    if r.event_id in GAP:
        v = GAP[r.event_id]
    else:
        for (eid, pre), val in SPECIAL.items():
            if r.event_id == eid and r.source.startswith(pre):
                v = val
        if v is None:
            v = ('yes', 'source re-downloaded; evidence quote(s) and every number in the people/deaths fields found in the re-downloaded text, and the figure, year and place read in context.')
    ver.append(v[0]); why.append(v[1])
d['verified'] = ver
d['note'] = [n + ' | CHECK 2026-11-16: ' + w for n, w in zip(d['note'], why)]
with open(P, 'w', encoding='utf-8-sig', newline='') as f:
    d.to_csv(f, index=False, quoting=csv.QUOTE_MINIMAL)
print(d.verified.value_counts().to_dict())
