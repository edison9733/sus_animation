"""Economy+sanitation: values read by hand from reports/papers downloaded in the 2026-11-16 run
(raw/econ_san/docs/*.txt, raw/econ_san/epmc/*.txt). Each tuple:
(theme, indicator, value, unit, year, geography, admin_level, disaggregation, source_key, derived, note)
source_key -> SOURCES below (source name, source_type, url). Nothing here is estimated; the note says where the value sits."""

U = 'https://data.unhcr.org/en/documents/download/'
E = 'https://europepmc.org/article/PMC/'
SOURCES = {
 'npc': ('National Planning Commission (2017) Ethiopia\'s Progress Towards Eradicating Poverty: An Interim Report on 2015/16 Poverty Analysis Study (HICE surveys)', 'official statistics', 'https://datacatalog.ihsn.org//catalog/9245/download/92897'),
 'jica': ('JICA study report annex "D.Table 5.2-1 Projected GDP/CAP(USD)" (openjicareport 11716669_27; report title and base year not verified)', 'donor study (projection, not official statistics)', 'https://openjicareport.jica.go.jp/pdf/11716669_27.pdf'),
 'unicef_brief': ('UNICEF Ethiopia, Situation Analysis of Children and Women: Gambella Region (briefing note)', 'UN agency report', 'https://www.unicef.org/ethiopia/media/2311/file/Gambella%20.pdf'),
 'unicef_sitrep': ('UNICEF Ethiopia Humanitarian Situation Report No. 3 (Mid-Year), January-June 2025', 'UN agency report', 'https://www.unicef.org/media/173276/file/Ethiopia-Humanitarian-SitRep-No.3-%28Mid-Year%29-30-June-2025.pdf'),
 'who_afro': ('WHO Regional Office for Africa news release: WHO ramps up cholera response efforts in Ethiopia\'s Gambella region (2025)', 'UN agency news release', 'https://www.afro.who.int/countries/ethiopia/news/who-ramps-cholera-response-efforts-ethiopias-gambella-region'),
 'u29942': ('UNHCR Sectors Indicators Matrix: Gambella Emergency Response (as of 01-February-2015)', 'UN agency report', U + '29942'),
 'u30058': ('UNHCR Sectors Indicators Matrix: Gambella Emergency Response (as of 01-April-2015)', 'UN agency report', U + '30058'),
 'u62837': ('WASH Sector Working Group Gambella, 2017 achievements slide (UNICEF emergency WASH specialist; UNHCR data portal doc 62837)', 'UN agency report', U + '62837'),
 'u62732': ('UNHCR Ethiopia WASH Fact Sheet December 2017', 'UN agency report', U + '62732'),
 'u63763': ('UNHCR Ethiopia WASH Fact Sheet March 2018', 'UN agency report', U + '63763'),
 'u66629': ('UNHCR Ethiopia WASH Fact Sheet September 2018', 'UN agency report', U + '66629'),
 'u68082': ('UNHCR Ethiopia WASH Fact Sheet December 2018', 'UN agency report', U + '68082'),
 'u76058': ('UNHCR Ethiopia Refugee Response Monitoring (WASH dashboard) 29-Mar-2020', 'UN agency report', U + '76058'),
 'u62670': ('UNHCR Camp Profile Gambella: Nguenyyiel Refugee Camp, December 2017', 'UN agency report', U + '62670'),
 'u70731': ('UNHCR Camp Profile: Nguenyyiel Refugee Camp, July 2019', 'UN agency report', U + '70731'),
 'u71386': ('UNHCR Camp Profile: Okugo Refugee Camp, August 2019', 'UN agency report', U + '71386'),
 'u72231': ('UNHCR Camp Profile: Nguenyyiel Refugee Camp, October 2019', 'UN agency report', U + '72231'),
 'u74535': ('UNHCR Camp Profile: Nguenyyiel Refugee Camp, February 2020', 'UN agency report', U + '74535'),
 'u74540': ('UNHCR Camp Profile: Pugnido Refugee Camp, February 2020', 'UN agency report', U + '74540'),
 'u75366': ('UNHCR Camp Profile: Nguenyyiel Refugee Camp, March 2020', 'UN agency report', U + '75366'),
 'u76452': ('UNHCR Camp Profile: Nguenyyiel Refugee Camp, April 2020', 'UN agency report', U + '76452'),
 'u119362': ('UNHCR Inter-Agency Emergency Response Plan for New South Sudanese Refugees in Gambella (July-December 2025), October 2025 update', 'UN agency report', U + '119362'),
 'u123068': ('UNHCR South Sudan Emergency Response - Ethiopia, WASH Factsheet May 2026', 'UN agency report', U + '123068'),
 'msf2014': ('MSF article: Ethiopia: Refugees attempt to survive in flooded camps (2014)', 'NGO self-report', 'https://www.msf.org/ethiopia-refugees-attempt-survive-flooded-camps'),
 'acpc_itang': ('UNECA African Climate Policy Centre / ClimDev-Africa project report: Impact of Flooding on Human Settlement in Rural Households of Gambella Region in Ethiopia (2014)', 'UN agency research report', 'https://www.climdev-africa.org/sites/default/files/DocumentAttachments/Impact%20of%20Flooding%20on%20Rural%20Households%20of%20Gambella%20Region%20in%20Ethiopia.pdf'),
 'pmc11020702': ('Peer-reviewed: Open Defecation Practice and Its Determinants Among Households Owned Toilet Facilities in Gambela Town, South West Ethiopia. Environ Health Insights 2024. doi:10.1177/11786302241246421', 'peer-reviewed', E + 'PMC11020702'),
 'pmc7618835': ('Peer-reviewed: Prevalence of Trachoma After Three Rounds of Antibiotic Mass Drug Administration in 13 Woredas of Gambella Region, Ethiopia. Ophthalmic Epidemiol 2024. doi:10.1080/09286586.2023.2248624', 'peer-reviewed', E + 'PMC7618835'),
 'pmc10941795': ('Peer-reviewed: Magnitude of Active Trachoma Among Host and Refugee Children in Gambella Regional State, Ethiopia. Clin Ophthalmol 2024. doi:10.2147/opth.s448870', 'peer-reviewed', E + 'PMC10941795'),
 'pmc10898313': ('Peer-reviewed: Assessment of Urogenital Schistosomiasis Knowledge, Attitudes and Practices Among Abobo Communities in Gambella Regional State. 2024', 'peer-reviewed', E + 'PMC10898313'),
 'pmid30772602': ('Peer-reviewed: Mekonnen GK et al. Risk factors for acute childhood diarrhea: a cross-sectional study comparing refugee camps and host communities in Gambella Region, Ethiopia. Travel Med Infect Dis 2019. doi:10.1016/j.tmaid.2019.02.003 (abstract only; full text not open access)', 'peer-reviewed', 'https://europepmc.org/article/MED/30772602'),
 'preprint': ('Preprint (not peer-reviewed): D\'Mello-Guyett L et al. Measuring Access to Sanitation and Sanitation-related Quality of Life among Refugees in Gambella, Ethiopia. Research Square 2026. doi:10.21203/rs.3.rs-9404994/v1 (abstract only)', 'preprint', 'https://doi.org/10.21203/rs.3.rs-9404994/v1'),
 'pmc11244192': ('Peer-reviewed: Retrospective Analysis of Cholera/Acute Watery Diarrhea Outbreaks in Ethiopia From 2001 To 2023. Clin Infect Dis 2024 (PMID 38996039)', 'peer-reviewed', E + 'PMC11244192'),
 'pmc10913215': ('Peer-reviewed: Spatiotemporal distribution of climate-sensitive disease incidences in Ethiopia: a longitudinal retrospective analysis of malaria, meningitis, cholera, dysentery... 2024 (PMID 38439016)', 'peer-reviewed', E + 'PMC10913215'),
}

ECO, SAN, WAT, HEA, POP = 'economy', 'sanitation', 'water', 'health', 'population'
F = []
def add(*a): F.append(a)

# ---------- poverty and consumption (NPC 2017, HICE surveys) ----------
for yr, r, u, t in (('1999/00', '54.6', '38.4', '50.5'), ('2010/11', '32.5', '30.7', '32'), ('2015/16', '26.4', '16.6', '23.0')):
    for d, v in (('rural', r), ('urban', u), ('total', t)):
        add(ECO, 'Poverty headcount index (national poverty line)', v, '% of population', yr, 'Gambella Region', 'region', d, 'npc', 'no', 'Table 13 row "Gamb."; 2004/05 is "-" (region not covered)')
for yr, r, u, t in (('1999/00', '45.4', '36.9', '44.2'), ('2004/05', '39.3', '35.1', '38.7'), ('2010/11', '30.4', '25.7', '29.6'), ('2015/16', '25.6', '14.8', '23.5')):
    for d, v in (('rural', r), ('urban', u), ('total', t)):
        add(ECO, 'Poverty headcount index (national poverty line)', v, '% of population', yr, 'Ethiopia', 'national', d, 'npc', 'no', 'Table 13 row "Total"')
add(ECO, 'Poverty headcount index (national poverty line)', 'NOT FOUND', '% of population', '2004/05', 'Gambella Region', 'region', 'total', 'npc', 'no', 'Table 13 shows "-" for Gambella in 2004/05; UNICEF brief footnote: region not included in 2004/05 poverty analysis')
for d, a, b in (('total', '26', '17.2'), ('rural', '24', '19.4'), ('urban', '30.2', '12.7')):
    add(ECO, 'Food poverty headcount index', a, '% of population', '2010/11', 'Gambella Region', 'region', d, 'npc', 'no', 'Table 14 row "Gambella"')
    add(ECO, 'Food poverty headcount index', b, '% of population', '2015/16', 'Gambella Region', 'region', d, 'npc', 'no', 'Table 14 row "Gambella"')
add(ECO, 'Food poverty headcount index', '36.6', '% of population', '2010/11', 'Ethiopia', 'national', 'total', 'npc', 'no', 'Summary text p.22: "National food poverty incidence declined from 36.6% to 24.8%"')
add(ECO, 'Food poverty headcount index', '24.8', '% of population', '2015/16', 'Ethiopia', 'national', 'total', 'npc', 'no', 'Summary text p.22')
for tab, d, g, n in (('A3', 'rural+urban', ('11592', '6302', '5290', '13854'), ('10257', '5237', '5020', '12391')),
                     ('A4', 'rural', ('9756', '5586', '4170', '11746'), ('8992', '4807', '4186', '10946')),
                     ('A5', 'urban', ('15151', '7690', '7461', '17941'), ('15619', '7063', '8556', '18518'))):
    for geo, lvl, vals in (('Gambella Region', 'region', g), ('Ethiopia', 'national', n)):
        for lab, v in zip(('Consumption expenditure per capita, total', 'Consumption expenditure per capita, food', 'Consumption expenditure per capita, non-food', 'Consumption expenditure per adult equivalent, total'), vals):
            add(ECO, lab, v, 'Birr per year at 2015/16 national average prices', '2015/16', geo, lvl, d, 'npc', 'no', 'Annex Table %s (HICE 2015/16, n=30,255 households); household consumption, not GDP' % tab)
add(ECO, 'Spatial price index, total (national average = 1.00)', '0.92', 'index', '2015/16', 'Gambella Region', 'region', 'total', 'npc', 'no', 'Annex Table A2 row "Gamb." (food 0.98, non-food 0.82)')
add(ECO, 'HICE 2015/16 sample households', '1344', 'households', '2015/16', 'Gambella Region', 'region', 'rural 576 + urban 768', 'npc', 'no', 'Table 5 regional distribution of sample households (4.5% of 30,255)')

# ---------- JICA projected GRDP ----------
yrs = ['2000/01', '2001/02', '2002/03', '2003/04', '2004/05', '2005/06', '2006/07', '2007/08', '2008/09', '2009/10', '2010/11', '2011/12', '2012/13', '2013/14', '2014/15', '2015/16', '2016/17', '2017/18', '2018/19', '2019/20', '2020/21']
gpc = [135, 141, 146, 152, 158, 165, 172, 179, 186, 194, 202, 211, 219, 229, 239, 248, 257, 267, 277, 288, 299]
gtot = [28, 31, 33, 35, 37, 40, 42, 45, 48, 51, 55, 58, 62, 67, 71, 75, 80, 85, 90, 96, 101]
npc_ = [135, 140, 145, 150, 156, 161, 167, 173, 180, 186, 193, 201, 208, 216, 225, 232, 241, 249, 258, 267, 277]
JN = 'PROJECTED (modelled) series from a JICA study table, constant growth-rate projection (6.5%/6.0% national growth assumed); not an official regional account. Read from the PDF page image/text layer, page 2 block "GAMBELLA"'
for y, a, b, c in zip(yrs, gpc, gtot, npc_):
    add(ECO, 'GRDP per capita, projected (JICA study)', str(a), 'USD per person', y, 'Gambella Region', 'region', 'modelled/projected', 'jica', 'no', JN)
    add(ECO, 'GRDP total, projected (JICA study)', str(b), 'million USD (unit inferred: total/pop = per-capita row)', y, 'Gambella Region', 'region', 'modelled/projected', 'jica', 'no', JN)
    add(ECO, 'GDP per capita, projected (JICA study)', str(c), 'USD per person', y, 'Ethiopia', 'national', 'modelled/projected', 'jica', 'no', JN.replace('page 2 block "GAMBELLA"', 'page 1 block "National"'))

# ---------- population snippets ----------
add(POP, 'Population, CSA projection quoted by UNICEF', '463000', 'persons', '2019', 'Gambella Region', 'region', 'total', 'unicef_brief', 'no', 'Table 1: "Total population (2019 projection based on the 2007 Census, CSA)" Gambella 463,000; national 98,663,000')
add(POP, 'Urban share of population, quoted by UNICEF', '36', '% of population', '2019', 'Gambella Region', 'region', 'urban', 'unicef_brief', 'no', 'Section 1 text: "64 per cent of the population live in rural areas and 36 per cent live in urban areas"; the same brief says 34 per cent in section 2 (inconsistent inside the source)')
add(POP, 'Population, regional projection quoted in paper', '498671', 'persons', '2020/21 (2013 Ethiopian calendar)', 'Gambella Region', 'region', 'total', 'pmc11020702', 'no', 'Methods: "population of 498 671 according to the 2013 E.C. population projection"')
add(POP, 'Refugees in Gambella (UNHCR portal, quoted by UNICEF)', '308978', 'persons', '2019', 'Gambella Region', 'region', 'refugees, 31 Dec 2019', 'unicef_brief', 'no', 'Section 1 text')
add(POP, 'Estimated households, Gambella town study kebeles', '3102', 'households', '2023', 'Gambella town', 'woreda', '5 kebeles', 'pmc11020702', 'no', 'Methods: town "has 5 kebeles with an estimated 3102 households"')

# ---------- UNHCR camp WASH indicators ----------
m1 = {'Tierkidi': (14, 27), 'Kule': (15, 31), 'Leitchuor': (17, 43), 'Okugo': (26, 6), 'Pugnido': (15, 27), 'Nip Nip': (11, 47),
      'Pagak (entry point)': (34, 18), 'Burbiey (entry point)': (18, 50), 'Pamdong (entry point)': (22, 27), 'All Gambella camps (total/average row)': (19, 31)}
m2 = {'Tierkidi': (17, 27), 'Kule': (16, 19), 'Leitchuor': (17, 44), 'Okugo': (22, 6), 'Pugnido': (15, 31), 'Nip Nip': (10, 47), 'All Gambella camps (total/average row)': (16, 29)}
for key, m, ymd, wn in (('u29942', m1, '2015-02', 'water = average for January 2015; latrines as of 1 February 2015'), ('u30058', m2, '2015-04', 'water = average for March 2015; latrines as of 1 April 2015')):
    for camp, (l, p) in m.items():
        lvl = 'camp' if 'All' not in camp else 'region'
        add(WAT, 'Litres of water per person per day (refugee camp)', str(l), 'litres/person/day', ymd, camp, lvl, 'refugees', key, 'no', 'WASH columns of the matrix; UNHCR standard >15 lpd (emergency); ' + wn)
        add(SAN, 'Persons per latrine (refugee camp)', str(p), 'persons/latrine', ymd, camp, lvl, 'refugees', key, 'no', 'WASH columns of the matrix; standard <50 persons/latrine; ' + wn)
add(WAT, 'Litres of water per person per day, Gambella camps average 2017', '17', 'litres/person/day', '2017', 'Gambella refugee camps', 'region', 'refugees', 'u62837', 'no', 'Slide "2017 Achievements - Water Supply": 20 l/p/d target, 17 l/p/d achieved; average 5 million litres daily')
add(SAN, 'Household latrine coverage, Gambella camps 2017', '30', '% of households', '2017', 'Gambella refugee camps', 'region', 'refugees', 'u62837', 'no', 'Slide "2017 Achievements - Sanitation & Hygiene": 85% RRP target, 30% achieved; chart labels 19/22/21/25/30% for Jan/Mar/Jun/Sep/Dec could not be matched to months from the text layer')
add(SAN, 'Household latrines in Gambella camps', '12187', 'latrines', '2017', 'Gambella refugee camps', 'region', 'refugees', 'u62837', 'no', 'Same slide: "12,187 HH latrines"')
add(SAN, 'Communal latrines in Gambella camps', '1636', 'latrines', '2017', 'Gambella refugee camps', 'region', 'refugees', 'u62837', 'no', 'Same slide: "1636 Communal latrines"')
add(SAN, 'Refugee families served by urine-diversion dry toilets (UDDT)', '354', 'families', '2017-12', 'Gambella refugee camps', 'region', 'refugees', 'u62732', 'no', 'Highlights: "354 families are benefitting from the same innovative sanitation facility in Gambella"')
add(SAN, 'Family latrine coverage, all Ethiopia refugee camps', '32.4', '% of refugee families', '2017-12', 'Ethiopia (26 refugee camps)', 'national', 'refugees', 'u62732', 'no', 'Highlights; "More than 85% of families have access to shared latrines"')
add(WAT, 'Litres of water per person per day, all Ethiopia refugee camps', '18.7', 'litres/person/day', '2017-12', 'Ethiopia (26 refugee camps)', 'national', 'refugees', 'u62732', 'no', 'Highlights; 11 of 26 camps meet 20 lppd')
add(SAN, 'Family latrine coverage, all Ethiopia refugee camps', '30', '% of refugee families', '2018-03', 'Ethiopia (26 refugee camps)', 'national', 'refugees', 'u63763', 'no', 'Highlights: reduction from December 2017 "due to decommissioning of many latrines"')
add(WAT, 'Litres of water per person per day, all Ethiopia refugee camps', '17.5', 'litres/person/day', '2018-03', 'Ethiopia (26 refugee camps)', 'national', 'refugees', 'u63763', 'no', 'Highlights')
add(SAN, 'Household latrines constructed in Gambella camps', '987', 'latrines', '2018-09', 'Gambella refugee camps', 'region', 'refugees', 'u66629', 'no', 'Highlights: "987 household latrines were constructed in camps in the Gambella region"')
add(SAN, 'Families with household latrine, Gambella camps', '34', '% of families', '2018-09', 'Gambella refugee camps', 'region', 'refugees', 'u66629', 'no', 'DOUBT: the PDF text layer is garbled (two overlapping text boxes); it reads that the new latrines "brought the [c]overage of families with household latrines ... to 34%". Check the PDF page visually before quoting')
add(SAN, 'Qualitative: flooding hampered latrine construction in refugee camps', 'reported (no count)', 'text', '2018-09', 'Ethiopia refugee camps (camps not named)', 'national', 'refugees', 'u66629', 'no', '"Some camps were affected by a recent flooding in the area which hampered the ongoing construction of additional latrines"; not Gambella-specific')
add(WAT, 'Litres of water per person per day, all Ethiopia refugee camps', '19', 'litres/person/day', '2018-09', 'Ethiopia (26 refugee camps)', 'national', 'refugees', 'u66629', 'no', 'Header box')
add(SAN, 'Persons per latrine, all Ethiopia refugee camps', '14', 'persons/latrine', '2018-12', 'Ethiopia (26 refugee camps)', 'national', 'refugees', 'u68082', 'no', 'Header box: "average of 14 pers/latrine. Seven camps don\'t meet the minimum standards of maximum of 20 pers/latrine"')
add(WAT, 'Litres of water per person per day, all Ethiopia refugee camps', '17', 'litres/person/day', '2018-12', 'Ethiopia (26 refugee camps)', 'national', 'refugees', 'u68082', 'no', 'Header box')
add(SAN, 'Persons per latrine, all Ethiopia refugee sites', '16', 'persons/latrine', '2020-03', 'Ethiopia (refugee sites)', 'national', 'refugees', 'u76058', 'no', 'Dashboard summary numbers "15 Liters/Person/Day, 16 Persons/Latrine"; the Gambella-only values on the map could not be read reliably from the text layer')
add(WAT, 'Litres of water per person per day, all Ethiopia refugee sites', '15', 'litres/person/day', '2020-03', 'Ethiopia (refugee sites)', 'national', 'refugees', 'u76058', 'no', 'Dashboard summary numbers')
for key, ymd, v, n in (('u62670', '2017-12', '15', 'header "15 lt" and text "Refugees have access to 15 litres of potable water per person per day"'),
                       ('u70731', '2019-07', '10', 'header "10 lt"'), ('u72231', '2019-10', '9.8', 'header "9.8 liters"'),
                       ('u74535', '2020-02', '9.4', 'header "9.4 liters"; body text says January average was 7.4 l/p/d (irregular supply, equipment breakdown)'),
                       ('u75366', '2020-03', '8.5', 'header and text "8.5 liters"'), ('u76452', '2020-04', '10.1', 'header and text "10.1 liters"')):
    add(WAT, 'Litres of water per person per day (refugee camp)', v, 'litres/person/day', ymd, 'Nguenyyiel', 'camp', 'refugees', key, 'no', n)
add(WAT, 'Litres of water per person per day (refugee camp)', '20', 'litres/person/day', '2019-08', 'Okugo', 'camp', 'refugees', 'u71386', 'no', 'header "20 liters" and WASH text')
add(SAN, 'Household latrine coverage (refugee camp)', '24', '% of occupied houses', '2019-08', 'Okugo', 'camp', 'refugees', 'u71386', 'no', '"Joint latrine inventory ... August 2019 ... household latrine coverage based on occupied houses stood at 24%. About 578 latrines are needed"')
add(SAN, 'Household latrines needed to close gap (refugee camp)', '578', 'latrines', '2019-08', 'Okugo', 'camp', 'refugees', 'u71386', 'no', 'same sentence')
add(WAT, 'Litres of water per person per day (refugee camp)', '20.2', 'litres/person/day', '2020-02', 'Pugnido', 'camp', 'refugees', 'u74540', 'no', 'WASH text "average access rate of 20.2 liters per person per day"; header box shows 20.1')
add(WAT, 'Litres of water per person per day (refugee site)', '15.52', 'litres/person/day', '2025-10', 'Luakdong', 'camp', 'new South Sudanese refugees', 'u119362', 'no', 'October 2025 update, status as of 5 October 2025')
add(SAN, 'Persons per latrine (refugee site)', '52', 'persons/latrine', '2025-10', 'Luakdong', 'camp', 'new South Sudanese refugees', 'u119362', 'no', '"Currently latrines are shared by 52 people per latrine in Luakdong"')
add(SAN, 'Planned family latrines (emergency response plan)', '10000', 'latrines (planned)', '2025', 'Gambella new-arrival sites', 'region', 'plan, not achievement', 'u119362', 'no', 'WASH plan: "10,000 family latrines to be constructed through community participation"; also 400 communal latrines planned')
add(WAT, 'Litres of water per person per day (refugee site)', '6.00', 'litres/person/day', '2026-05', 'Luakdong', 'camp', 'new South Sudanese refugees', 'u123068', 'no', 'Key figures, "average of previous weeks"; fuel shortages cited')
add(SAN, 'Persons per latrine (refugee site)', '64', 'persons/latrine', '2026-05', 'Luakdong', 'camp', 'new South Sudanese refugees', 'u123068', 'no', 'Key figures, "average of previous weeks"')
add(SAN, 'Household and communal latrines constructed and functional', '690', 'latrines', '2026-05', 'Luakdong and Tormorok response area', 'camp', 'new South Sudanese refugees', 'u123068', 'no', 'Achievements list; also 105 latrine pits excavated, 50 superstructures')

# ---------- peer-reviewed / studies ----------
T = 'Table 2 "Latrine condition and utilization among households in Gambella Town, 2023" (n=561 latrine-owning households, June-July 2023)'
for lab, v in (('Open defecation practised despite owning a latrine', '47.2'), ('Latrine utilisation among latrine-owning households', '52.8'), ('Latrines with superstructure', '80.2'),
               ('Latrines with door', '60.2'), ('Latrines with squat hole', '37.8'), ('Latrines judged hygienic', '41.0'), ('Latrines cleaned daily', '38.9'), ('Latrine owned for 3 years or more', '91.4')):
    add(SAN, lab, v, '% of latrine-owning households', '2023', 'Gambella town', 'woreda', 'urban, latrine owners only', 'pmc11020702', 'no', T + ('; OD 95% CI 43.2-51.4' if lab.startswith('Open') else ''))
for eu, n, w, l, h in (('Agnuak zone EU: Jor, Gog, Dimma', 777, 39, 3, 6), ('Agnuak zone EU: Gambella, Abobo', 775, 43, 1, '<1'), ('Nuer zone and Itang EU: Lare, Itang', 774, 41, 3, 0),
                       ('Majang zone EU: Mengeshi, Godere', 779, 51, 6, 6), ('Nuer zone EU: Wanthuwa, Makoy, Jikawo, Akobo', 775, 46, 1, '<1'), ('Gambella Region, 13 woredas (total)', 3880, 44, 3, 3)):
    lvl = 'region' if 'total' in eu else 'woreda'
    nn = 'Table 4, trachoma impact surveys February-March 2019, %d households surveyed; evaluation unit = group of woredas' % n
    add(SAN, 'Households with an improved latrine', str(l), '% of households', '2019', eu, lvl, 'rural/host community survey', 'pmc7618835', 'no', nn + ('; 110/3,880' if lvl == 'region' else ''))
    add(WAT, 'Households with improved drinking water source within 30-minute return journey', str(w), '% of households', '2019', eu, lvl, 'rural/host community survey', 'pmc7618835', 'no', nn)
    add('hygiene', 'Households with a latrine with a handwashing station', str(h), '% of households', '2019', eu, lvl, 'rural/host community survey', 'pmc7618835', 'no', nn)
N2 = 'Table of household characteristics, Itang district survey 1 Nov-5 Dec 2021 (host n=474, refugee n=248)'
add(SAN, 'Latrine availability', '32.3', '% of households', '2021', 'Itang special woreda (host community)', 'woreda', 'host community', 'pmc10941795', 'no', N2 + '; 153/474')
add(SAN, 'Latrine availability', '85.5', '% of households', '2021', 'Itang special woreda (refugee camps)', 'camp', 'refugees', 'pmc10941795', 'no', N2 + '; 212/248')
add(SAN, 'Latrine utilisation among households with a latrine', '97.4', '% of households with latrine', '2021', 'Itang special woreda (host community)', 'woreda', 'host community', 'pmc10941795', 'no', N2 + '; 148 yes / 4 no')
add(SAN, 'Latrine utilisation among households with a latrine', '99.5', '% of households with latrine', '2021', 'Itang special woreda (refugee camps)', 'camp', 'refugees', 'pmc10941795', 'no', N2 + '; 212 yes / 1 no')
add(SAN, 'Respondents with access to a toilet', '93.3', '% of respondents', '2022', 'Abobo woreda', 'woreda', 'community survey', 'pmc10898313', 'no', 'Text: "376 participants (93.3%) had access to toilets, with 290 (77.1%) having toilets in their own homes and 86 (22.9%) using public toilets"; n=403, August 2022; the practices table gives 92.3% for the same 376')
add(SAN, 'Respondents defecating in river/dam/bush/open field', '7.7', '% of respondents', '2022', 'Abobo woreda', 'woreda', 'community survey', 'pmc10898313', 'no', 'Risky practices table: 31 of 403')
add(SAN, 'Households with no access to latrine', '95.7', '% of surveyed households', '2012', 'Itang special woreda', 'woreda', 'rural flood-affected kebeles', 'acpc_itang', 'no', 'Table 6 "Access to electricity, safe drinking water and latrine"; household survey of 431 households, Sep-Nov 2012; text: "Access to electricity and pit latrines is nearly inexistent"')
add(WAT, 'Households using surface water for drinking during flood', '40.7', '% of surveyed households', '2012', 'Itang special woreda', 'woreda', 'rural flood-affected kebeles', 'acpc_itang', 'no', 'Table 6; dry season 38.1% surface water, 60.9% borehole')
add(HEA, 'Two-week diarrhoea prevalence, children under five', '38', '% of children', '2016', 'Gambella refugee camps', 'camp', 'refugees', 'pmid30772602', 'no', 'Abstract: n=1,667 under-fives in total; OR 1.37 (95% CI 1.04-1.8) refugee vs host; data collection Sep-Dec 2016 per companion paper PMC6249824')
add(HEA, 'Two-week diarrhoea prevalence, children under five', '33', '% of children', '2016', 'Gambella host communities', 'region', 'host community', 'pmid30772602', 'no', 'Abstract; in host communities diarrhoea was more likely where households "consumed surface water or did not have a latrine"')
add(SAN, 'Refugee respondents with access to a sanitation facility', '40', '% of respondents', 'NOT STATED in abstract (preprint posted 2026-04)', 'Two refugee settlements, Gambella', 'camp', 'refugees', 'preprint', 'no', 'Abstract: 764 respondents, 307 (40%) with access; of users 36% pit latrine, 64% UDDT')
add(SAN, 'Refugee respondents practising open defecation', '60', '% of respondents', 'NOT STATED in abstract (preprint posted 2026-04)', 'Two refugee settlements, Gambella', 'camp', 'refugees', 'preprint', 'no', 'Abstract: 457 of 764')

# ---------- cholera / AWD ----------
add(HEA, 'Cholera/AWD cases reported', '211', 'cases', '2020', 'Gambella Region', 'region', 'all ages', 'pmc11244192', 'no', 'Table 4 row "Gambela": 0 cases in 2015-2019 and 2021-2023, 211 in 2020; 4 deaths (CFR 1.9%)')
add(HEA, 'Cholera/AWD deaths reported', '4', 'deaths', '2020', 'Gambella Region', 'region', 'all ages', 'pmc11244192', 'no', 'Table 4 row "Gambela": "4 (1.9)"')
add(HEA, 'Cholera/AWD incidence rate', '44.14', 'cases per 100,000 population', '2020', 'Gambella Region', 'region', 'all ages', 'pmc11244192', 'no', 'Table 3 row "Gambela"; 0.00 in every other year 2015-2023')
for y in ('2015', '2016', '2017', '2018', '2019', '2021', '2022', '2023'):
    add(HEA, 'Cholera/AWD cases reported', '0', 'cases', y, 'Gambella Region', 'region', 'all ages', 'pmc11244192', 'no', 'Table 4 row "Gambela" (national surveillance line list analysed by the authors); text: "In 2023, the cholera outbreak involved all regions, except Addis Ababa and Gambela"')
add(HEA, 'Cholera case fatality rate, cumulative 2015-2023', '1.89', '%', '2015-2023', 'Gambella Region', 'region', 'all ages', 'pmc11244192', 'no', 'Abstract and Table 3/4; national 2015-2023 cases 99,945')
for mth, v in (('October', '2'), ('November', '67'), ('December', '25')):
    add(HEA, 'Cholera/AWD cases by calendar month, summed over 2010-2022', v, 'cases', '2010-2022 (%s)' % mth, 'Gambella Region', 'region', 'month total across years', 'pmc10913215', 'no', 'Table 3 "Monthly regional Cholera/AWD disease incidence in Ethiopia from 2010 to 2022", row Gambella: Jan-Sep 0, Oct 2, Nov 67, Dec 25 (sum 94; differs from 211 in PMC11244192 - different data extract)')
add(HEA, 'Cholera cases reported', '2194', 'cases', '2025 (January-May)', 'Gambella Region', 'region', 'all ages', 'unicef_sitrep', 'no', 'Text: "Between January and May 2025, a total of 4,373 cholera cases and 42 deaths ... Amhara (2,179 cases, 10 deaths) and Gambella (2,194 cases, 32 deaths)"; source of figures: PHEOC/EPHI as cited by UNICEF')
add(HEA, 'Cholera deaths reported', '32', 'deaths', '2025 (January-May)', 'Gambella Region', 'region', 'all ages', 'unicef_sitrep', 'no', 'same sentence')
add(HEA, 'Woredas with active cholera outbreak', '5', 'woredas', '2025 (end of May)', 'Gambella Region', 'region', '', 'unicef_sitrep', 'no', '"outbreak currently active in 23 woredas - 18 in Amhara and 5 in Gambella"')
add(HEA, 'Cholera cases (lower bound in news release)', '1200', 'cases ("more than")', '2025 (February-March)', 'Gambella Region', 'region', 'all ages', 'who_afro', 'no', '"infected more than 1,200 people. The outbreak, first detected in Akobo Woreda on February 11, has since spread to eight woredas and four refugee camps"')
add(HEA, 'Woredas affected by cholera outbreak', '8', 'woredas (plus 4 refugee camps)', '2025 (February-March)', 'Gambella Region', 'region', '', 'who_afro', 'no', 'same sentence')
add(HEA, 'People given WASH non-food items (cholera and flood response)', '31000', 'persons ("over")', '2025 (January-June)', 'Gambella Region', 'region', 'incl. South Sudanese refugees', 'unicef_sitrep', 'no', 'WASH section of the sitrep')

# ---------- latrine collapse / flooding ----------
add(SAN, 'Qualitative: latrines overflowed and some collapsed after rainstorm', 'reported (no count)', 'text', '2014-08-24', 'Leitchuor', 'camp', 'refugees', 'msf2014', 'no', '"inside the camp, the latrines, which were hastily built, have overflowed, with some collapsing completely" (rainstorm of 24 August 2014)')
add(SAN, 'Number of pit latrines collapsed or flooded', 'NOT FOUND', 'latrines', '', 'Gambella Region', 'region', '', 'msf2014', 'no', 'No source opened in this run gives a count of collapsed/flooded latrines for Gambella. Looked in: MSF 2014 article, UNHCR WASH fact sheets 2017-2018, UNHCR camp profiles 2017-2020, UNHCR ERP Oct 2025 and WASH factsheet May 2026, UNICEF sitrep mid-2025, IFRC/OCHA flood documents saved by the flood task (raw/ifrc, raw/web), web search 2026-11-16')
