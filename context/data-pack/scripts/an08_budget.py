"""Pilot budget estimate (low / mid / high, USD 2026) for FloodSafe Sanitation Gambella.
Usage: python an08_budget.py <gambella root>  ->  data/budget_estimate.csv, data/budget_assumptions.csv
EVERYTHING HERE IS AN ESTIMATE built by Claude (2026-11-17) from published unit costs elsewhere in Ethiopia/East Africa.
No Gambella-specific cost data were found; Phase 1 must replace these with real quotes."""
import sys
import pandas as pd

R = sys.argv[1].rstrip('/') + '/'
FX = 161.3  # ETB per USD, mid-market 16 Nov 2026 (xe.com / aggregators); used only to convert ETB anchors

# ---------------- assumptions (change here) — all are the team's/Claude's choices, not data
A = dict(hh_total=500, hh_zoneA=400, hh_zoneB=100, hh_size=5.8, masons=30, mason_train_days=10, helpers=20,
         survey_rounds=2, survey_hh_per_round=1000, swap_points=2, camp_shared_units=20)
assump = pd.DataFrame([
    ['Pilot households', A['hh_total'], 'Assumption: 3 woredas (Jikawo, Wantawo, Lare); 80% zone A, 20% zone B, matching the zone mix there'],
    ['Zone A households', A['hh_zoneA'], 'Assumption'], ['Zone B households', A['hh_zoneB'], 'Assumption'],
    ['People reached (households x 5.8)', round(A['hh_total'] * A['hh_size']), 'Household size 5.8 = Ethiopia CLTS sample (Crocker et al. 2021, Table 2); Gambela-specific size not in data pack'],
    ['Shared units in one refugee camp', A['camp_shared_units'], 'Assumption: sex-separated blocks with lock and light'],
    ['Masons trained', A['masons'], 'Assumption'], ['Local warning helpers', A['helpers'], 'Assumption'],
    ['Survey households per round (pilot + comparison)', A['survey_hh_per_round'], 'Assumption: 500 pilot + 500 comparison; baseline and endline'],
    ['Exchange rate ETB per USD', FX, 'Mid-market 16 Nov 2026 (xe.com and other aggregators); parallel market ~182'],
], columns=['assumption', 'value', 'basis'])

U = {  # unit costs USD: (low, mid, high, basis, source, url, confidence)
 'zoneA': (400, 600, 800, 'Raised/sealed above-ground unit (UDDT-type, two chambers) on a plinth; plinth adds to a standard UDDT',
           'UNHCR UDDT SOP (Gambella): about USD 500 to build; UNHCR Innovation: UDDT USD 700 cut to 400, then ~600 for quality; Kenya GTZ 2009: KSh 51,000 cut to 25,023; SDI raised "sky-loo" double chamber USD 350-500',
           'https://www.unhcr.org/innovation/?p=553 ; https://sdinet.org/tag/toilets/ ; https://susana.org/_resources/documents/default/2-513-blume-2009-cost-optimization-uddts-kenya-final-draft.pdf', 'medium'),
 'zoneB': (200, 350, 500, 'Lined pit + slab and squat hole raised above flood level + superstructure with door',
           'Rural Ethiopia model latrine ~4,000 ETB (~USD 110, unlined, 2023); VIP latrine USD 441 (Senegal, AICD); improved pit with slab/superstructure USD 36-350 per person (IRC WASHCost); Ethiopian slab alone USD 12-18',
           'https://www.tandfonline.com/doi/full/10.1080/13549839.2023.2184781 ; https://www.eu-africa-infrastructure-tf.net/attachments/library/aicd-background-paper-13-sanit-sect-summary-en.pdf ; https://academic.oup.com/heapro/article/39/2/daae034/7643325', 'medium-low'),
 'camp_unit': (500, 800, 1200, 'Shared sex-separated stance in a camp block with lock, light, handwashing', 'Own estimate scaled from zone A/B unit costs plus handwashing and lighting', '', 'low'),
 'safety': (15, 30, 50, 'Per household unit: inside lock, small solar light, door upgrade', 'Small solar lanterns USD 1-20 (TechXLab catalogue range); lock and door upgrade own estimate', 'https://techxlab.org/solutions/sun-king-pro/', 'low'),
 'site_check': (5, 10, 15, 'Per household site check: flood mark, soil test pit, well distance', 'Own estimate (staff time + test pits)', '', 'low'),
 'engineering': (3000, 6000, 10000, 'Lump sum: civil engineer, flood test of sealed unit and lining, prototypes of each zone', 'Own estimate', '', 'low'),
 'mason_day': (8, 12, 18, 'Per mason per training day: stipend, trainer share, materials', 'Own estimate; context: civil-service minimum 6,000 ETB/month (Sept 2025) = ~USD 37/month', 'https://allafrica.com/stories/202508190208.html', 'low'),
 'toolkit': (80, 150, 250, 'Per mason: moulds, tools', 'Own estimate', '', 'low'),
 'gauge_pack': (25, 40, 60, 'Per household: groundwater gauge pipe and pegs (~USD 5-10) + emergency hygiene/sanitation pack', 'Own estimate', '', 'low'),
 'swap_point': (3000, 6000, 10000, 'Per high-ground swap point (shared toilets, water, shelter for long floods)', 'Own estimate', '', 'low'),
 'behaviour': (20, 30, 40, 'Per household: hygiene promotion, facilitation, follow-up visits, school sessions',
               'Ethiopia CLTS programme cost USD 16.5-22.6 per household in 2012-14 USD (Crocker et al. 2021, Table 3; total cost / households), raised for inflation', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7873587/', 'medium'),
 'interview': (8, 12, 18, 'Per completed household interview incl. female enumerators for safety module, supervision, tablets', 'Own estimate; no Ethiopia per-interview cost found', '', 'low'),
}
L = []
def add(n, line, item, qty, key, unit='unit', share=None):
    lo, mi, hi, basis, src, url, conf = U[key]
    L.append(dict(line_no=n, budget_line=line, item=item, quantity=qty, unit=unit, unit_low=lo, unit_mid=mi, unit_high=hi,
                  total_low=qty * lo, total_mid=qty * mi, total_high=qty * hi, basis=basis, source=src, url=url, confidence=conf))
add(1, 'Site checks, consultation, baseline survey', 'Site checks', A['hh_total'], 'site_check', 'household')
add(1, 'Site checks, consultation, baseline survey', 'Baseline survey interviews', A['survey_hh_per_round'], 'interview', 'interview')
add(2, 'Prototypes, materials tests, engineering advice', 'Engineering and prototypes (lump sum)', 1, 'engineering', 'lump sum')
add(3, 'Toilet units — zone A', 'Raised / sealed units', A['hh_zoneA'], 'zoneA', 'household unit')
add(4, 'Toilet units — zone B', 'Raised slab + lined pit', A['hh_zoneB'], 'zoneB', 'household unit')
add(4, 'Toilet units — zone B', 'Shared stances, one refugee camp', A['camp_shared_units'], 'camp_unit', 'stance')
add(5, "Safety features: locks, lights, women's units", 'Lock, light, door upgrade', A['hh_total'], 'safety', 'household')
add(6, 'Mason and helper training, tools', 'Mason training', A['masons'] * A['mason_train_days'], 'mason_day', 'mason-day')
add(6, 'Mason and helper training, tools', 'Mason toolkits', A['masons'], 'toolkit', 'mason')
add(7, 'Gauges, pegs, emergency packs, swap point', 'Gauge, pegs, emergency pack', A['hh_total'], 'gauge_pack', 'household')
add(7, 'Gauges, pegs, emergency packs, swap point', 'High-ground swap points', A['swap_points'], 'swap_point', 'site')
add(8, 'Behaviour and hygiene activities', 'Hygiene promotion and follow-up', A['hh_total'], 'behaviour', 'household')
add(9, 'Monitoring and endline survey', 'Endline survey interviews', A['survey_hh_per_round'], 'interview', 'interview')
d = pd.DataFrame(L)
direct = d[['total_low', 'total_mid', 'total_high']].sum()
# management share from Ethiopia CLTS: management 8,690 of 36,739 = 23.7% of total (Crocker et al. 2021, Table 3)
mg = (0.20, 0.24, 0.28)
for k, col in enumerate(['low', 'mid', 'high']):
    pass
L.append(dict(line_no=10, budget_line='Staff, transport, management', item='Management, staff, transport', quantity=1, unit='share of direct costs',
              unit_low=mg[0], unit_mid=mg[1], unit_high=mg[2], total_low=round(direct.total_low * mg[0]), total_mid=round(direct.total_mid * mg[1]), total_high=round(direct.total_high * mg[2]),
              basis='20 / 24 / 28% of direct costs', source='Ethiopia CLTS: management USD 8,690 of 36,739 total = 23.7% (Crocker et al. 2021, Table 3)', url='https://pmc.ncbi.nlm.nih.gov/articles/PMC7873587/', confidence='medium'))
sub = pd.DataFrame(L)[['total_low', 'total_mid', 'total_high']].sum()
ct = (0.10, 0.10, 0.15)
L.append(dict(line_no=11, budget_line='Contingency for flood damage', item='Contingency', quantity=1, unit='share of subtotal', unit_low=ct[0], unit_mid=ct[1], unit_high=ct[2],
              total_low=round(sub.total_low * ct[0]), total_mid=round(sub.total_mid * ct[1]), total_high=round(sub.total_high * ct[2]),
              basis='10 / 10 / 15% of subtotal (flood damage, price swings: birr fell ~26% against USD in a year)', source='Own choice; currency context Addis Fortune Apr 2026', url='https://addisfortune.news/petrified-labour-cries-over-burdensome-living-costs', confidence='low'))
d = pd.DataFrame(L); d['derived'] = 'yes (estimate)'
d.to_csv(R + 'data/budget_estimate.csv', index=False, encoding='utf-8-sig'); assump.to_csv(R + 'data/budget_assumptions.csv', index=False, encoding='utf-8-sig')
s = d.groupby(['line_no', 'budget_line'])[['total_low', 'total_mid', 'total_high']].sum().reset_index()
tot = s[['total_low', 'total_mid', 'total_high']].sum()
s.to_csv(R + 'data/budget_summary.csv', index=False, encoding='utf-8-sig')
pd.set_option('display.width', 200); print(s.to_string()); print('TOTAL', tot.to_dict())
print('per household (mid):', round(tot.total_mid / A['hh_total']), ' per person:', round(tot.total_mid / (A['hh_total'] * A['hh_size'])))
