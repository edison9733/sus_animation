"""fd04_build_events.py - build data/gambella_flood_drought_events.csv

One row per (event, source). Rows that describe the same flood/drought share an event_id; figures from
different sources are NOT merged. Every hand-entered row carries one or more verbatim quotes; the script
refuses to write the CSV unless each quote is found (whitespace-normalised) in the text file made from
the document downloaded by fd01/fd02 (raw/fd_rerun/...). url and accessed date are taken from
raw/fd_rerun/download_log.tsv, not typed by hand.
GDACS and DFO rows are generated from the downloaded JSON.

Run order: fd01_download.py, fd02_download_web.py, fd03_to_text.py, fd04_build_events.py, fd05_build_yearly.py
Run: python -P scripts/fd04_build_events.py
"""
import os, re, csv, json, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, 'raw', 'fd_rerun')
OUT = os.path.join(ROOT, 'data', 'gambella_flood_drought_events.csv')
COLS = ['event_id', 'event_type', 'start_date', 'end_date', 'year', 'woredas_or_places', 'people_affected',
        'people_displaced', 'deaths', 'houses_or_latrines_damaged', 'crop_or_livestock_loss', 'river_or_cause',
        'source', 'source_type', 'url', 'accessed', 'note', 'geography', 'admin_level', 'derived',
        'evidence_quote', 'raw_file']

# ---------------------------------------------------------------- download log -> url, accessed
LOG = {}
for line in open(os.path.join(RR, 'download_log.tsv'), encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    if len(p) >= 5:
        LOG[p[1]] = dict(time=p[0], url=p[2], status=p[3], size=p[4])   # last attempt wins


def norm(s):
    s = s.replace(' ', ' ').replace('Â', ' ')
    return re.sub(r'\s+', ' ', s).strip()


_TXT = {}
def text_of(rel):
    if rel not in _TXT:
        p = os.path.join(RR, rel)
        _TXT[rel] = norm(open(p, encoding='utf-8', errors='replace').read())
    return _TXT[rel]


ROWS, PROBLEMS = [], []


def E(event_id, event_type, start, end, year, places, source, source_type, rawfile, quotes, note,
      aff='', disp='', deaths='', houses='', crop='', cause='', geography='Gambella Region, Ethiopia',
      admin_level='region', derived='no'):
    """hand-entered row; rawfile = 'web/<name>.<ext>' as saved by fd02 (text is read from the .txt next to it)"""
    lg = LOG.get(rawfile)
    if not lg:
        PROBLEMS.append('%s: %s not in download log' % (event_id, rawfile)); lg = dict(time='', url='', status='', size='')
    txt = text_of(os.path.splitext(rawfile)[0] + '.txt')
    for q in quotes:
        if norm(q) not in txt:
            PROBLEMS.append('%s: quote not found in %s: %r' % (event_id, rawfile, q))
    if lg['status'] not in ('200',):
        note += ' | HTTP status of the download was %s, but the body contained the quoted text.' % lg['status']
    ROWS.append(dict(event_id=event_id, event_type=event_type, start_date=start, end_date=end, year=year,
                     woredas_or_places=places, people_affected=aff, people_displaced=disp, deaths=deaths,
                     houses_or_latrines_damaged=houses, crop_or_livestock_loss=crop, river_or_cause=cause,
                     source=source, source_type=source_type, url=lg['url'], accessed=lg['time'][:10], note=note,
                     geography=geography, admin_level=admin_level, derived=derived,
                     evidence_quote=' || '.join(norm(q) for q in quotes), raw_file='raw/fd_rerun/' + rawfile))


def G(event_id, event_type, year, source, where, note, rawfile=''):
    """gap row: nothing found / not accessed"""
    lg = LOG.get(rawfile, dict(time='', url='', status='', size=''))
    val = 'NOT ACCESSED' if 'NOT ACCESSED' in note[:14] else 'NOT FOUND'
    ROWS.append(dict(event_id=event_id, event_type=event_type, start_date='', end_date='', year=year,
                     woredas_or_places=val, people_affected=val, people_displaced=val, deaths=val,
                     houses_or_latrines_damaged=val, crop_or_livestock_loss=val, river_or_cause='',
                     source=source, source_type='gap record', url=where, accessed=(lg['time'][:10] or TODAY),
                     note=note + ((' | HTTP status %s' % lg['status']) if lg['status'] else ''),
                     geography='Gambella Region, Ethiopia', admin_level='region', derived='no',
                     evidence_quote='', raw_file=('raw/fd_rerun/' + rawfile) if rawfile else ''))


TODAY = max(v['time'][:10] for v in LOG.values())

PR = 'peer-reviewed article'
UN = 'UN agency report'
RC = 'Red Cross report'
NEWS = 'news'
NGO = 'NGO self-report'
GREY = 'thesis / research report (not peer-reviewed)'

# =========================================================================== FLOODS
E('GAM-FL-1961-01', 'flood', '1961-10', '1961-11', 1961, 'Akobo district (Tiergol village; farmland between Aferwa and mouth of Gilo river)',
  'Ayenew & Shimels (2024) A History of Famine on the Southwestern Ethiopian Border: the case of Akobo (1950-1991). Ethiopian Journal of Social Sciences 10(1)',
  PR, 'web/ajol_ejss_274517.pdf',
  ['the 1961 flood was', 'heavy and continuous rainfall in October', 'houses of soldiers were destroyed and additional eight houses were taken away',
   'there were no registered deaths at that time'],
  'Archive-based history. Water stayed on farmland for more than a month; crops planted in October destroyed; famine followed in 1961/62 (a register listed 258 people suffering from hunger when the famine was first reported). No affected-population total in the source.',
  deaths='0 registered', houses='4 soldiers\' houses destroyed + 8 houses taken away (Tiergol military camp)',
  crop='crops planted in October destroyed (no area given)', cause='Pibor river overflow after heavy rain; also Gilo (Gilawo) river',
  geography='Akobo, Gambella Region', admin_level='woreda')

E('GAM-FL-1988-01', 'flood', '1988', '', 1988, 'western Gambella plain; Itang area; Gambella town (power station, buildings)',
  'Mersha Alemu (2007) Flood hazard, vulnerability and risk assessments: Itang area of Gambella. MSc thesis, Addis Ababa University (citing the Baro-Akobo Basin master plan study)',
  GREY, 'web/aau_thesis_itang.pdf',
  ['the area of 9720 sq. km in the west of the plain was covered with water for', 'destroyed the grain crops on an area of 4.5',
   'the losses came to 2.2 million birrs'],
  'Second-hand: thesis section 3.3.4 summarises the Baro-Akobo Basin study, which was not opened. Month not given. No people figures. Ayenew & Shimels (2024) separately report an acute famine in Akobo in 1988 caused by "drought and flood" (no figures).',
  crop='4,500 ha grain crops destroyed; loss 2.2 million birr; many cattle, sheep and goats died (no count)',
  houses='houses, hotels, administrative buildings flooded (no count); hydro power station flooded, supply cut one month',
  cause='Baro river and tributaries; 9,720 km2 under water for one month')

E('GAM-FL-1989-01', 'flood', '1989', '', 1989, 'Itang town',
  'Alemseged Tamiru, Negash Wagesho & Ermias Alemu (2014) Impact of flooding on human settlement in rural households of Gambella Region. UNECA-ACPC / Arba Minch University project report',
  GREY, 'web/uneca_itang.pdf', ['The 1989 flood is identified as the biggest'],
  'From participatory mapping with Itang residents (2012): 1989 called the biggest flood in 40 years, covering nearly all of Itang town. No figures. Community recall, not a measured record.',
  cause='Baro river', geography='Itang Special Woreda, Gambella Region', admin_level='woreda')

E('GAM-FL-1996-01', 'flood', '1996-06-06', '1996-09', 1996, 'Gog, Jor, Akobo, Jikawo, Itang, Lare, Dimma, Gambella weredas (35 villages by 24 June)',
  'UNDP Emergencies Unit for Ethiopia (J. Ahrens): Gambella Floods Report - Air Survey, 2 August 1996 (quotes DPPC memoranda of 24 June and 11 July 1996)',
  UN, 'web/eue_gambel96aug.html',
  ['flooding 35 villages and corn fields on both sides of the rivers', 'reportedly 16 people had been killed while a total number of 23,000',
   '8,000 people were affected, while in Gog Jinjer 17,000 were affected by', 'floods; 7,500 people were affected in Dimma',
   'While in Itang (5,000) and Lare (2,000) displaced people were'],
  'people_affected 23,000 and deaths 16 = DPPC memo of 24 June 1996 (17,125 of them "highly affected"). DPPC Gambella report of 11 July: Jikawo about 8,000, Gog Jinjer 17,000, Dimma 7,500 affected (4 more deaths reported in Dimma) - not added to the 23,000 here because overlap is unknown. people_displaced = Itang 5,000 + Lare 2,000 being accommodated on 2 Aug (sum is mine).',
  aff='23000', disp='7000', deaths='16', crop='corn fields flooded; loss of livestock and property reported (no count)',
  cause='Gilo, Akobo and Baro rivers overflow after rain from 6 June 1996', derived='yes (people_displaced = 5,000 + 2,000)')

E('GAM-FL-1996-01', 'flood', '1996-06', '1996-09', 1996, 'Itang, Jikawo (52 villages), Akobo, Gog (7 of 10 kebeles), Jor (11 of 11 kebeles), Dimma, Gambella weredas',
  'UNDP Emergencies Unit for Ethiopia: Gambella People\'s Regional State - Flood Assessment mission 22-27 September 1996 (table source: Gambella Regional Bureau of DPPC)',
  UN, 'web/eue_Gambel96oct.html',
  ['Total: 89,968', '52 villages were affected by floods', 'of 15,000 people were affected along the Gilo river', 'affected by the worst floods in five years',
   'people out of their homes'],
  'people_affected 89,968 = total relief BENEFICIARIES in the DPPC table (rounded, cumulative July to mid-September 1996: Gambella 2,000; Itang 22,868; Jikawo 10,000 est.; Akobo 30,000 est.; Gog+Jor 17,125; Dimma 7,975; Abobo and Godere not affected). It is a relief count used here as the affected figure. The latest flood in Itang forced about 2,000 people out of their homes. Akobo: all maize and sorghum destroyed; Gog+Jor: nearly all maize and sorghum destroyed.',
  aff='89968', disp='2000', crop='all crops (maize, sorghum) destroyed in Akobo; nearly all in Gog and Jor; all local production destroyed in Itang (no area given)',
  cause='Baro, Gilo, Akobo rivers; peaks early July and mid-September')

E('GAM-FL-1997-01', 'flood', '1997', '', 1997, 'Gambella Region (Baro river plain)',
  'UNDP-EUE: Food shortages and seasonal floods - major recurrent threats to Gambella Region. Assessment mission report 16-21 October 1999',
  UN, 'web/eue_gamb1099.html', ['widespread floods in 1997 which displaced many thousands', 'The 1997 inundation of the Baro River took a long time to recede'],
  'Retrospective mention only: "displaced many thousands", no number. Late recession delayed riverbank planting and gave a very poor harvest in 1998.',
  disp='', crop='crops destroyed; riverbank planting of Oct 1997 delayed (no figures)', cause='Baro river')

E('GAM-FL-1999-01', 'flood', '1999-07', '1999-10', 1999, 'Gambella, Itang and Jikawo weredas (Itang town offices and houses)',
  'UNDP-EUE: Food shortages and seasonal floods - major recurrent threats to Gambella Region. Assessment mission report 16-21 October 1999',
  UN, 'web/eue_gamb1099.html',
  ['displaced and made homeless 57,500 people in Gambella, Itang and Jikawo weredas', 'directly affecting an estimated 57,500 people',
   'Three more weredas were affected by floods in July and October this year'],
  'Figure is from local authorities (Regional DPP Bureau). The source uses the same 57,500 for "directly affected" and for "displaced and made homeless". Floods in July and again October 1999; not receded by 21 October. The report also says 163,263 people in 111 peasant associations are considered vulnerable to seasonal flooding.',
  aff='57500', disp='57500', houses='residential areas inundated; Itang town offices and houses "totally drenched" (no count)',
  crop='crops and belongings lost (no figures)', cause='Baro river overflow after heavy rain in the western highlands')

E('GAM-FL-2006-01', 'flood', '2006', '', 2006, 'Gambella Region ("most parts")',
  'Wakuma Abaya, Mandere & Ewald (2009) Floods and health in Gambella region, Ethiopia. Global Health Action 2:2019. doi:10.3402/gha.v2i0.2019',
  PR, 'web/abaya2009_pmc.html',
  ['the 2006 flood in the Gambella region caused damage to 1,650 ha of maize crops', 'There was also a 20% reduction in production'],
  'Paper cites its ref. 29 for the crop figures; no people figures for Gambella. Paper also states that the Baro, Akobo, Gilo, Alwero, Jikow, Gnandera and Koikoye rivers overflowed every year in the seven years before 2006/07 except 2002 (citing the 2006 flash appeal).',
  crop='1,650 ha maize damaged; 20% reduction in production (waterlogging)', cause='river overflow')

E('GAM-FL-2006-01', 'flood', '2006', '', 2006, 'Gambella Region ("most parts")',
  'IFRC Emergency Appeal MDRET004 Ethiopia: Floods, 14 September 2007 (background section)', RC, 'web/ifrc_MDRET004EA_2007.pdf',
  ['most parts of Gambella regions are some'],
  'Mention only: the 2006 flooding in "most parts of Gambella" is given as an example of river flooding. No figures.', cause='river flooding')

E('GAM-FL-2007-01', 'flood', '2007-07-29', '2007-10', 2007, 'Gambella Region (western Ethiopia)',
  'Mail & Guardian, 31 July 2007: "Nearly 12 000 Ethiopians left homeless by floods" (quotes Ojulu Bach, head of disaster prevention programme, Gambela region)',
  NEWS, 'web/mg_2007_07_31.html',
  ['people have been displaced and one killed from the flood that resulted from Sunday', 'head of disaster prevention programme in the Gambela region'],
  'Early count two days after the flash flood of Sunday 29 July 2007: 11,886 displaced, 1 dead (the number is printed as "11 886" with a non-breaking space; quote check covers the rest of the sentence). Official said numbers could rise.',
  disp='11886', deaths='1', cause='flash flood after heavy rainfall on 29 July 2007')

E('GAM-FL-2007-01', 'flood', '2007-07', '2007-09', 2007, 'Gambella Region',
  'IFRC Emergency Appeal MDRET004 Ethiopia: Floods, 14 September 2007 (information from ERCS Gambella regional branch)', RC, 'web/ifrc_MDRET004EA_2007.pdf',
  ['more than 40,000 people have been affected by the floods in the area, with over 8,000'],
  '"more than 40,000 affected, over 8,000 displaced" (lower bounds). GLIDE FL-2007-000145-ETH.',
  aff='40000', disp='8000', cause='kiremt rains; river floods')

E('GAM-FL-2007-01', 'flood', '2007-07', '2007-09-20', 2007, 'Gambella, Lare and Itang woredas',
  'IFRC Operations Update no. 1, MDRET004 Ethiopia: Floods, 28 September 2007 (Table 1, source Ethiopian Red Cross Society)', RC, 'web/ifrc_MDRET00401_2007.pdf',
  ['Gambella Gambella, Lare and Itang', 'Flood affected populations in 5 regions as at 20 September 2007'],
  'Table 1: 20,000 affected people in Gambella, Lare and Itang as at 20 September 2007; 36,090 is the TOTAL of the five regions (2,700 + 1,300 + 3,170 + 400 + 20,000 + 2,520 + 6,000). Corrected by the independent check 2026-11-16: pdftotext -layout shifts the number column by one line, so the first build read the table total as the Gambella value; PyMuPDF table extraction gives the row "Gambella | Gambella, Lare and Itang | 20,000". Same update repeats the early-September figure (more than 40,000 affected, over 8,000 displaced).',
  aff='20000', cause='kiremt rains; river floods')

E('GAM-FL-2007-01', 'flood', '2007', '', 2007, 'Itang Special Woreda (household survey)',
  'Alemseged Tamiru, Negash Wagesho & Ermias Alemu (2014) Impact of flooding on human settlement in rural households of Gambella Region. UNECA-ACPC / Arba Minch University project report',
  GREY, 'web/uneca_itang.pdf',
  ['The 2007 flood was one of the major events', 'As a result 38 percent of the surveyed houses were severely damaged', 'standing crops as reported by 77 percent of the surveyed households'],
  'Household survey in Itang (carried out 2012) about the 2007 flood. Percentages are shares of SURVEYED households, not counts: 38% of surveyed houses severely damaged; 77% reported damage to standing crops; grain reserves of nearly half destroyed; three of four cattle keepers reported severe damage. Recall data five years after the event.',
  houses='38% of surveyed houses severely damaged', crop='77% of surveyed households: standing crops damaged; many goats drowned (no count)',
  cause='Baro river overflow plus flash floods from Oromia highlands; unusually long duration', geography='Itang Special Woreda, Gambella Region', admin_level='woreda')

E('GAM-FL-2008-01', 'flood', '2008-08', '2008-08-25', 2008, 'Gambella Region (Gilo river mentioned)',
  'Mail & Guardian / Reuters, 25 August 2008: "Thousands displaced by floods in Ethiopia" (quotes Akway Ojulu, head of emergency assistance in Gambella)',
  NEWS, 'web/mg_2008_08_25.html',
  ['forcing 18 000 people to be displaced', 'About 3 000 hectares of farm land with maize, sorghum and cotton have been destroyed', 'deaths of three people including one child'],
  'Regional official quoted by Reuters. A UNHCR/Refworld copy of an IRIN article on the same flood (Lare and Itang woredas) could not be opened (browser check).',
  disp='18000', deaths='3', crop='about 3,000 ha maize, sorghum and cotton destroyed', cause='flash floods after nearly a week of heavy rain; major rivers burst banks')

E('GAM-FL-2008-01', 'flood', '2008', '', 2008, 'Itang Special Woreda',
  'Alemseged Tamiru, Negash Wagesho & Ermias Alemu (2014) Impact of flooding on human settlement in rural households of Gambella Region. UNECA-ACPC / Arba Minch University project report',
  GREY, 'web/uneca_itang.pdf', ['the most recent major flood which occurred in 2008'],
  'Mention only (2008 named as a major flood by Itang elders and in participatory mapping, with 1989 and 2012). No figures. The report writes "2008 E.C. and 2012 E.C." in one sentence; elsewhere the years are used as Gregorian, so the calendar is not fully certain.',
  cause='Baro river', geography='Itang Special Woreda, Gambella Region', admin_level='woreda')

E('GAM-FL-2012-01', 'flood', '2012', '2012-10', 2012, 'Itang Special Woreda (Pill kebele entirely inundated; parts of Itang town)',
  'Alemseged Tamiru, Negash Wagesho & Ermias Alemu (2014) Impact of flooding on human settlement in rural households of Gambella Region. UNECA-ACPC / Arba Minch University project report',
  GREY, 'web/uneca_itang.pdf', ['that the 2012 flood stayed beyond the end of September', 'Pill Kebele was entirely inundated up to shoulder'],
  'Field observation by the research team during the household survey (October 2012). No people or damage counts.',
  cause='Baro river flood plus flash floods', geography='Itang Special Woreda, Gambella Region', admin_level='woreda')

E('GAM-FL-2014-01', 'flood', '2014-08', '2014-09', 2014, 'Leitchuor (Lietchuor) refugee camp; Nip Nip camp; Pagak and Pamdong transit sites; MSF hospital at Itang (near Kule and Tierkidi camps)',
  'Medecins Sans Frontieres press release, 4 September 2014: "Refugees attempt to survive in flooded camps"', NGO, 'web/msf_2014_flooded_camps.html',
  ['which shelters some 40,000 people from South Sudan, has become a lake dotted with islands', 'the latrines, which were hastily built, have overflowed, with some collapsing',
   'Heavy rains and flooding have also caused serious damage in Pagak and Pamdong transit camps'],
  'people_affected = camp population given by MSF ("some 40,000"; photo caption says around 36,000). LATRINES: hastily built latrines overflowed, some collapsed completely. Tukuls flooded; shelters blown down in the storm of 24 August 2014; MSF 120-bed hospital in Itang flooded after a dyke collapsed. MSF notes Kule and Tierkidi sites are not prone to flooding. The same text was issued by MSF-USA on 5 Sept 2014 (not listed separately).',
  aff='40000', houses='latrines overflowed, some collapsed (no count); newly built tukuls completely flooded; shelters blown down (no count)',
  cause='rainy-season rain pooling on flat black cotton soil; storm of 24 August 2014', geography='refugee camps, Gambella Region', admin_level='refugee camp')

E('GAM-FL-2014-01', 'flood', '2014-08', '2014-09', 2014, 'Leitchuor refugee camp',
  'Al Jazeera, 5 September 2014: "Ethiopia refugee camp submerged by floods" (reports the MSF statement)', NEWS, 'web/aljazeera_2014_09_05.html',
  ['has been made uninhabitable by flooding'],
  'News report of the MSF statement; camp "home to almost 40,000 refugees". Not an independent figure.',
  cause='heavy rains and storms', geography='refugee camps, Gambella Region', admin_level='refugee camp')

E('GAM-FL-2014-01', 'flood', '2014-08', '', 2014, 'Leitchuor and Nip Nip refugee camps',
  'UNHCR news release, Gambella, 11 May 2015: relocation of South Sudanese refugees from flood-prone Leitchuor and Nip Nip camps to Jewi camp',
  UN, 'web/unhcr_news_9642.html',
  ['became flooded last August together with Nip Nip camp', 'It will accommodate about 48,000 refugees from Leitchuor camp'],
  'Consequence of the August 2014 flooding: about 48,000 refugees from Leitchuor to be relocated to Jewi camp (capacity about 50,000) from 8 May 2015; nearly 3,000 from Nip Nip relocated (some to Pugnido in March 2015). 48,000 is a relocation figure, not entered as people_affected.',
  cause='camps sited on floodplain', geography='refugee camps, Gambella Region', admin_level='refugee camp')

E('GAM-FL-2014-01', 'flood', '2014', '2015-02-01', 2014, 'Leitchuor and Nip Nip refugee camps',
  'UNHCR Sectors Indicators Matrix: Gambella Emergency Response (as of 01 February 2015)', UN, 'web/unhcr_29942.pdf',
  ['Due to flooding in Leitchuor and Nip Nip camps, only a minimum of the transitional shelters'],
  'Shelter note in the matrix: because of flooding only a minimum of the transitional shelters built in the two camps are habitable; most households self-settled on higher ground in the host community. No count.',
  houses='most transitional shelters in Leitchuor and Nip Nip not habitable (no count)', geography='refugee camps, Gambella Region', admin_level='refugee camp')

E('GAM-FL-2014-01', 'flood', '2014', '', 2014, 'Leitchuor and Nip Nip refugee camps',
  'Norwegian Refugee Council, 23 July 2015: "Flood affected refugees in need of urgent assistance"', NGO, 'web/nrc_2015_07.html',
  ['The refugees were affected by a flood that occurred last year'],
  'NRC: 48,000 refugees from Leitchuor and Nip Nip relocated to Jewi camp in mid-May 2015 after the 2014 flood (the NRC page prints "48.000"). Relocation figure, not entered as people_affected.',
  geography='refugee camps, Gambella Region', admin_level='refugee camp')

E('GAM-FL-2017-01', 'flood', '2017-05', '2017-07', 2017, 'parts of Gambella Region (no woreda named)',
  'OCHA Ethiopia Weekly Humanitarian Bulletin, 10 July 2017', UN, 'web/ocha_bulletin_2017_07_10.pdf',
  ['have already been reported in parts of Amhara, Gambella and Oromia regions since May'],
  'Mention only: flood incidences reported in parts of Gambella since May 2017. No figures.', cause='heavy rains')

E('GAM-FL-2017-01', 'flood', '2017-05', '2017-06', 2017, 'Gambella Region (no woreda named)',
  'Gambella Community Development Council (GCDC) website, 11 June 2017, reposting a UNICEF Ethiopia humanitarian situation report', NEWS, 'web/gambcomm_111.html',
  ['Floods have been reported following heavy rains in Amhara, Gambella, Oromia, SNNP and Somali regions'],
  'Diaspora community website reposting UNICEF text; the UNICEF original was not opened. Mention only, no figures.', cause='heavy rains')

E('GAM-FL-2019-01', 'flood', '2019-10-02', '2019-10-03', 2019, 'Gambella town (five kebeles along the Baro river bed)',
  'OCHA Ethiopia Humanitarian Bulletin, 23 September - 06 October 2019', UN, 'web/ocha_bulletin_2019_sep23_oct06.pdf',
  ['at least 353 households (1,405', 'people) were displaced across five kebeles, and their houses were fully flooded', 'The flood was reportedly more severe compared to previous years'],
  'Assessment of 3 October 2019 by the Gambella Region Disaster Prevention, Preparedness and Food Security Agency with partners. The GCDC website reposted the same text on 9 Oct 2019 (not listed separately).',
  disp='1405', houses='houses of 353 households fully flooded', cause='Baro (Openo) river overflow after heavy rain on 2 October 2019',
  geography='Gambella town, Gambella Region', admin_level='town')

E('GAM-FL-2020-01', 'flood', '2020-06', '2020-09', 2020, 'Gambella Region',
  'IFRC DREF Emergency Plan of Action MDRET023 Ethiopia: Floods, September 2020 (Table 1, figures from NDRMC)', RC, 'web/ifrc_MDRET023_2020.pdf',
  ['Gambella 31,865 18,819', 'Flood affected and displaced people by Regions from June to September 2020'],
  'Table 1 "Flood affected and displaced people by Regions from June to September 2020": Gambella 31,865 affected, 18,819 displaced (national total 1,017,854 affected, 292,863 displaced).',
  aff='31865', disp='18819', cause='heavy and prolonged kiremt rains')

E('GAM-FL-2020-01', 'flood', '2020-07', '2020-08-10', 2020, 'Gambella Region (listed with five other regions)',
  'OCHA Ethiopia Humanitarian Bulletin, 27 July - 10 August 2020', UN, 'web/ocha_bulletin_2020_07_27_08_10.pdf',
  ['Amhara, Oromia, Gambella, SNNP and Somali regions, of whom 53,158 people were'],
  'Gambella is listed among six affected regions; the 124,219 affected / 53,158 displaced (as of 10 August 2020) are six-region totals, so no Gambella figure is entered. Web search snippets (not opened: OCHA flash update of 6 Aug 2020 on ReliefWeb, Addis Standard archive) give 11,749 displaced in Jor, Akobo and Wantowa woredas in mid-August 2020.',
  cause='above-normal rainfall, second dekad of July 2020')

E('GAM-FL-2020-01', 'flood', '2020-07', '2020-08-10', 2020, 'Nuer zone',
  'The Watchers (watchers.news), 10 August 2020: "Severe floods displace at least 32 000 people in Ethiopia" (cites UN OCHA)', NEWS, 'web/watchers_2020_08_10.html',
  ['In Nuer, around 9 000 have been displaced', 'all major rivers in Gambella are at full capacity'],
  'News site summarising OCHA; "around 9 000" displaced in Nuer zone, extensive crop damage.',
  disp='9000', crop='extensive crop damage (no figure)', cause='rivers at full capacity', geography='Nuer Zone, Gambella Region', admin_level='zone')

E('GAM-FL-2021-01', 'flood', '2021-04', '2021-07', 2021, 'Lare woreda',
  'OCHA Ethiopia Humanitarian Bulletin, 6 September 2021 (citing NDRMC)', UN, 'web/ocha_bulletin_2021_09_06.pdf',
  ['and Lare Woreda of Gambella Region', 'Oromia, Somali and SNNP Regions left some 616,714 individuals affected, 214,124 others'],
  'Lare woreda is named among the most affected areas of the April-July 2021 floods. Figures in the bulletin (616,714 affected, 214,124 displaced, 28 dead) are for seven regions together; no Gambella figure.',
  cause='belg / early kiremt rains', geography='Lare woreda, Gambella Region', admin_level='woreda')

E('GAM-FL-2021-01', 'flood', '2021-04', '2021-07', 2021, 'Gambella Region',
  'Gambella Community Development Council (GCDC) website, 26 October 2022, text credited "AS" (Addis Standard) quoting UN data', NEWS, 'web/gambcomm_289.html',
  ['between April-July 2021, which had displaced some 11,749 residents'],
  'DOUBT: second-hand figure in a 2022 news article. Web search snippets (not opened) attribute the same number, 11,749 displaced (Jor, Akobo, Wantowa), to OCHA reporting of August 2020, so the year may be wrong in one of the two.',
  disp='11749', cause='river and flash flooding')

E('GAM-FL-2022-01', 'flood', '2022-08', '2022-10', 2022, '12 woredas and Gambella town',
  'Gambella Community Development Council (GCDC) website, 26 October 2022, text credited "AS" (Addis Standard) quoting UN (OCHA) data', NEWS, 'web/gambcomm_289.html',
  ['at least 185,200 people (37,040 households) were internally displaced and an additional 79,631 people (15,927 households) were affected',
   '72 percent of cropland was damaged', 'Of 917 water schemes in 10 affected woredas, 270 are not functional', 'At least 77 health facilities',
   'more than 74,000 civilians had been displaced'],
  'News relay of the OCHA flood update of 24 October 2022 (ReliefWeb original not accessible). people_affected = the "additional" 79,631 who were affected but not displaced; 185,200 + 79,631 = 264,831, which equals the EM-DAT total_affected of the Ethiopia flood of Aug-Oct 2022 (my comparison). Earlier (August 2022) the regional DRM head gave more than 74,000 displaced in eight districts. 270 of 917 water schemes not functional; 77 health facilities and 135 schools affected (56,006 children). No latrine count.',
  aff='79631', disp='185200', houses='no house or latrine count; 270 of 917 water schemes non-functional in 10 woredas; 77 health facilities; 135 schools',
  crop='72% of cropland damaged (mostly maize); on average 8% of livestock died (mostly poultry)', cause='Akobo, Alwero, Baro (Openo), Gilo rivers and tributaries; heavy rain early August to October')

E('GAM-FL-2022-01', 'flood', '2022-08', '2022-10', 2022, '12 woredas',
  'UNICEF Ethiopia Humanitarian Situation Report No. 10, October 2022', UN, 'web/unicef_sitrep10_oct2022.pdf',
  ['heavy rains from early August to October caused flooding across 12 woredas displacing an estimated', '250 water schemes in 10 flood-affected woredas',
   'at least 135 schools were damaged by the floods'],
  '"an estimated 180,000 people" displaced (the number is on the next line of the PDF text). 250 water schemes non-functional in 10 woredas; over 70 health facilities affected; at least 135 schools damaged (over 56,000 children). 72% of cropland damaged, 8% of livestock died.',
  disp='180000', houses='no house or latrine count; 250 water schemes non-functional; over 70 health facilities; 135 schools',
  crop='72% of cropland damaged (mostly maize); on average 8% of livestock died', cause='heavy rains early August to October 2022')

E('GAM-FL-2022-01', 'flood', '2022-08', '2022-09', 2022, '11 woredas',
  'Protection Cluster Ethiopia, Monthly Protection Overview, September 2022', UN, 'web/ecoi_protection_sep2022.pdf',
  ['Over 187,000 individuals are reportedly affected and newly displaced by flood in 11 woredas of Gambella region'],
  '"Over 187,000 ... affected and newly displaced" - one combined figure, entered under people_affected only. Displaced people sheltering in schools and health centres.',
  aff='187000', cause='flood')

E('GAM-FL-2022-01', 'flood', '2022-07', '', 2022, 'Itang Special Woreda (schools); expected: Itang, Abol, Lare, Makuey, Jikawo, Jor, Gambella town',
  'UNICEF Ethiopia Humanitarian Situation Report No. 7, July 2022', UN, 'web/unicef_sitrep7_jul2022.pdf',
  ['three alternative basic education and 10 formal primary schools have been affected by floods'],
  'Start of the 2022 season: by July, 13 schools in Itang woreda already affected by floods; flooding and evacuation expected in six woredas and Gambella town (regional Disaster Risk Prevention and Food Security Agency forecast).',
  houses='13 schools affected in Itang (3 alternative basic education + 10 primary)', cause='heavy rain up- and downstream on the Baro river')

E('GAM-FL-2023-01', 'flood', '2023-06', '', 2023, 'Gambella Region',
  'International Charter Space and Major Disasters, activation 824 "Flooding in Ethiopia" (activated 20 June 2023; UNITAR/UNOSAT flood assessment product dated 28 June 2023)',
  'UN / satellite mapping activation', 'web/charter_824.html',
  ['Floods are affecting the Gambella region in Ethiopia', 'Date of Charter Activation 2023-06-20'],
  'Activation page only; no impact figures. Shows that flooding in Gambella was already being mapped in June 2023, before the September 2023 peak. May be the same season as GAM-FL-2023-02.',
  cause='Akobo, Alwero, Baro (Openo), Gilo rivers')

E('GAM-FL-2023-02', 'flood', '2023-09', '2023-09', 2023, 'nine districts incl. Gambella city (kebeles 01, 02, 04, 05); all five Nuer zone districts',
  'Addis Standard via allAfrica, 19 September 2023: "Floods displace thousands in Gambella, regional govt calls for relief" (regional communication bureau)',
  NEWS, 'web/allafrica_202309200126.html',
  ['have impacted nine districts across the region', 'the overflowing of the Baro, Alwero, Gilona and Akobo rivers'],
  'Only the headline and first two paragraphs are public on allAfrica (rest is subscription content); "thousands" displaced, no number. addisstandard.com itself returned HTTP 403.',
  cause='overflow of Baro, Alwero, Gilo and Akobo rivers after heavy rain in the highlands')

E('GAM-FL-2023-02', 'flood', '2023-06', '2023-12', 2023, 'Agnewak (Anywaa) and Nuer zones, Itang Special Woreda, parts of Gambela town',
  'Ethiopian Red Cross Society Emergency Operations Center: Flood situation as of December 2023', RC, 'web/ercs_flood_dec2023.pdf',
  ['Gambela Flood 10,434 52,345'],
  'Table "Flood affected areas": Gambela 10,434 households, 52,345 people affected by floods following the kiremt rain (national 107,321 households / 641,782 people). Cumulative for the 2023 season, so it may include the June 2023 flooding.',
  aff='52345', cause='kiremt rains; floods and overflow of lakes (national description)')

E('GAM-FL-2024-01', 'flood', '2024-08', '2024-08-12', 2024, 'four districts of Gambella Region',
  'Radar Africa, 12 August 2024: "Flooding displaces thousands in western Ethiopia" (cites Fana Broadcasting Corporation and the regional communication bureau)',
  NEWS, 'web/radarafrica_28888.html', ['has displaced around 16,000 people', 'affected four districts in the Gambella region'],
  'News relay of state media; homes and fields damaged (no count).', disp='16000', houses='homes damaged (no count)', crop='agricultural fields damaged (no count)',
  cause='intense rainfall')

E('GAM-FL-2024-01', 'flood', '2024-07', '2024-09-20', 2024, 'Gog, Lare, Jor and Wanthoa (Wanthwa) woredas, Anywaa and Nuer zones',
  'IFRC Operation Update #1, Emergency Appeal MDRET036 Ethiopia: Floods and Landslides, issued 3 October 2024 (covers 31 July - 20 September 2024)', RC, 'web/ifrc_MDRET036eu1.pdf',
  ['flood-induced displacements of 21,060 people due to heavy rains in Gog, Lare, Jor and Wanthwa woredas'],
  '21,060 people displaced by flooding in four woredas (no exact date in the update).', disp='21060', cause='heavy kiremt rains')

E('GAM-FL-2024-02', 'flood', '2024-09', '2024-09-09', 2024, 'Jikawo woreda',
  'Ground News page (article summary credited to allAfrica / Addis Standard): "Heavy rains displace over 20,000 in Gambella region as Baro river overflows"',
  NEWS, 'web/groundnews_2024.html', ['has caused the Baro River to overflow, displacing over 20,000 people'],
  'Aggregator summary of an Addis Standard article (original returned HTTP 403). Kept as a separate event from GAM-FL-2024-01 because woreda (Jikawo) and month (September) differ; it could be the same season counted twice. Significant damage to homes, crops and plantations (no counts).',
  disp='20000', houses='significant damage to homes (no count)', crop='crops and plantations damaged (no count)', cause='Baro river overflow after heavy rainfall in Jikawo',
  geography='Jikawo woreda, Gambella Region', admin_level='woreda')

E('GAM-FL-2024-02', 'flood', '2024-09', '2024-09-09', 2024, 'Jikawo woreda',
  'Prensa Latina, 9 September 2024: "Heavy rains continue to affect Ethiopia" (quotes the head of the regional Disaster Risk Management Office)', NEWS, 'web/plenglish_242225.html',
  ['More than 20 thousand people displaced'],
  'News agency; "more than 20 thousand" displaced in Jikawo district.', disp='20000', cause='heavy rains; Baro river overflow',
  geography='Jikawo woreda, Gambella Region', admin_level='woreda')

E('GAM-FL-2025-01', 'flood', '2025-07-24', '2025-07-25', 2025, 'Gambella city (Newland area; kebeles 01 and 05 per search snippet)',
  'Addis Standard via allAfrica, 25 July 2025: "Over 50 homes damaged by flash floods in Gambella city following heavy overnight rainfall"', NEWS, 'web/allafrica_202507250436.html',
  ['More than 50 homes have been damaged in Gambella city'],
  'Residents\' account; only the first paragraphs are public on allAfrica. No injuries reported; several residents evacuated.',
  houses='more than 50 homes damaged', cause='flash flood after heavy overnight rain', geography='Gambella city, Gambella Region', admin_level='town')

E('GAM-FL-2025-02', 'flood', '2025-09', '2025-09', 2025, 'Lare, Jikawo and Wanthoa woredas, Nuer zone',
  'Protection Cluster Ethiopia, Monthly Protection Overview, September 2025', UN, 'web/gpc_ethiopia_sep2025.pdf',
  ['Total of 7,082 HHs, comprising 35,410 individuals displaced across three woredas (Lare, Jikawo, Wanthoa) of Nuer Zone', 'damaged 4,958 hectares of crops'],
  '7,082 households / 35,410 people displaced by seasonal flooding. One health centre and 8 health posts affected; 10 primary and 9 secondary schools damaged. Household items lost. Flood assessment mission to Nuer and Anywaa zones on 8-10 September 2025.',
  disp='35410', houses='no house or latrine count; 1 health centre, 8 health posts affected; 19 schools damaged',
  crop='4,958 ha crops damaged (maize, sorghum, vegetables)', cause='seasonal flooding', geography='Nuer Zone, Gambella Region', admin_level='zone')

E('GAM-FL-2025-02', 'flood', '2025-10', '', 2025, 'Matar (refugee arrivals site)',
  'UNHCR Ethiopia, document 119362 (South Sudan emergency response plan / update for Gambella, 2025)', UN, 'web/unhcr_119362.pdf',
  ['refugees continue to shelter in the flooded grounds of a'],
  'Photo caption dated 4 October 2025: new South Sudanese arrivals in Matar sheltering in the flooded grounds of a school while awaiting relocation to Luakdong. No count. The plan describes the terrain as flood-prone and budgets dykes and drainage for the new site.',
  cause='seasonal flooding / waterlogging', geography='Matar, Gambella Region', admin_level='refugee site')

E('GAM-FL-2025-02', 'flood', '2025-06', '2025-09', 2025, 'low-lying parts of Gambella (Baro-Akobo basin)',
  'FEWS NET / USGS East Africa Seasonal Monitor, November 2025', 'early-warning bulletin', 'web/fews_seasonal_monitor_2025_11.pdf',
  ['the Baro-Akobo Basin led to extended inundation'],
  'Remote-sensing based seasonal summary: rising water levels along the Baro-Akobo basin led to extended inundation in low-lying parts of Gambella during the 2025 kiremt season. No impact figures.',
  cause='rising water levels along the Baro-Akobo basin')

# =========================================================================== DROUGHTS / RAIN FAILURE
E('GAM-DR-1982-01', 'drought', '1982-06', '1982-08', 1982, 'Akobo district',
  'Ayenew & Shimels (2024) A History of Famine on the Southwestern Ethiopian Border: the case of Akobo (1950-1991). Ethiopian Journal of Social Sciences 10(1)',
  PR, 'web/ajol_ejss_274517.pdf',
  ['Famine also occurred in Akobo in 1982', 'it rained only on July 15', 'The maize planted in the district in'],
  'Archive-based. Delay and shortage of rain: very little rain in June 1982, rain only on 15 July; maize withered, first cropping season (June-August) failed, acute food shortage. No number of people.',
  crop='maize withered; June-August season unproductive (no area)', cause='delay and shortage of rain', geography='Akobo, Gambella Region', admin_level='woreda')

E('GAM-DR-1990-01', 'drought', '1990-06', '', 1990, 'Akobo district',
  'Ayenew & Shimels (2024) A History of Famine on the Southwestern Ethiopian Border: the case of Akobo (1950-1991). Ethiopian Journal of Social Sciences 10(1)',
  PR, 'web/ajol_ejss_274517.pdf',
  ['In the famine of 1990 alone between 15,000 and 20, 000 people in Akobo had been', 'after the early days of June 1990, there was acute shortage of rain in Akobo'],
  'people_affected is a RANGE in the source (15,000 to 20,000 affected by the 1990 famine in Akobo); it is not used in yearly sums. The paper attributes the 1988 and 1990 famines to "multiple factors such as drought and flood". Nearly all victims migrated to neighbouring sub-provinces.',
  aff='15000-20000', crop='planted crops shrivelled; state farm also damaged (no area)', cause='acute shortage of rain after early June 1990',
  geography='Akobo, Gambella Region', admin_level='woreda')

E('GAM-DR-1999-01', 'drought', '1999', '', 1999, 'Jor, Akobo and Dimma weredas',
  'UNDP-EUE: Food shortages and seasonal floods - major recurrent threats to Gambella Region. Assessment mission report 16-21 October 1999',
  UN, 'web/eue_gamb1099.html',
  ['food insecurity reportedly affecting an estimated 30,400 people from 3 weredas (Jor, Akobo and Dimma)', 'poor rains earlier in the year'],
  'Rain failure / food insecurity rather than a declared drought: poor rains early in 1999, meher rains started on time but broke off, forcing replanting. 30,400 people food insecure in three weredas (regional DPP Bureau; the three weredas could not be visited). Together with the 57,500 flood-affected the source gives 87,900 people needing help.',
  aff='30400', crop='replanting needed; reduced harvest prospects (no figures)', cause='poor and interrupted rains in 1999')

E('GAM-DR-2002-01', 'drought', '2002-06', '2002-12', 2002, 'Gambella Region',
  'FAO/WFP Crop and Food Supply Assessment Mission to Ethiopia, Special Report, 30 December 2002 (section 4.10 Gambella; Table 11)', UN, 'web/fao_y8300e_2002.html',
  ['This year the Kiremt rains were late and floods low', '13 600 tonnes or 40 percent below last year', 'Gambella 58 400 7 235 760 22 8 017'],
  'Kiremt rains late and river floods low in 2002: cereal and pulse area about 20% below 2001, harvest 13,600 t, 40% below 2001. people_affected = 58,400 people in Gambella requiring emergency food assistance in 2003 (Table 11, DPPC-led assessment; part of the 11.3 million in need nationally). A WFP/UNDP-EUE/DPPC mid-season assessment of Gambella (25 Aug - 1 Sep 2002) exists on ReliefWeb but could not be opened.',
  aff='58400', crop='cereal and pulse area -20%; harvest 13,600 t = 40% below previous year', cause='late kiremt rains; low river floods (less recession farming)')

E('GAM-DR-2016-01', 'drought', '2016', '2018', 2016, 'Gambella Region',
  'UNICEF Ethiopia (2019/2020) Situation Analysis of Children and Women: Gambella Region (citing UNOCHA HRD relief food beneficiary analysis 2013-2018)',
  UN, 'web/unicef_gambella_brief.pdf',
  ['of 28,966 people were relief food beneficiaries', 'a severe El Ni'],
  'Indirect evidence only. The brief says that between 2016 and 2018 people in Gambella were food insecure and "a minimum of 28,966 people were relief food beneficiaries", in a period when El Nino- and Indian Ocean Dipole-induced droughts hit the Horn of Africa. It does not say the drought hit Gambella itself, so 28,966 is NOT entered as people_affected. The OCHA HRD documents were not opened (tralac copy returned HTTP 403).',
  cause='El Nino 2015/16 and Indian Ocean Dipole droughts in the Horn of Africa (regional context)')

# =========================================================================== rows generated from JSON
def gdacs_rows():
    import glob
    from shapely.geometry import shape, Point
    adm1 = shape(json.load(open(os.path.join(ROOT, 'data', 'gambella_adm1.geojson'), encoding='utf-8'))['features'][0]['geometry'])
    lst = json.load(open(os.path.join(RR, 'gdacs', 'eth_fl_dr.json'), encoding='utf-8'))['features']
    eid_map = {1102824: 'GAM-FL-2024-01', 1102257: 'GAM-FL-2023-02', 1101733: 'GAM-FL-2022-01', 3146: 'GAM-FL-2007-01', 3367: 'GAM-FL-2008-01',
               1017730: 'GAM-DR-2025-01', 1100570: 'GAM-FL-2020-01', 1100243: 'GAM-FL-2019-01'}
    for x in lst:
        pr = x['properties']
        if 'Ethiopia' not in (pr.get('country') or ''): continue
        f = os.path.join(RR, 'gdacs', '%s_%s.json' % (pr['eventtype'], pr['eventid']))
        if not os.path.exists(f) or os.path.getsize(f) == 0: continue
        d = json.load(open(f, encoding='utf-8'))['properties']
        lon, lat = x['geometry']['coordinates'][:2]
        inside = adm1.contains(Point(lon, lat))
        sendai = [s for s in (d.get('sendai') or []) if 'gambel' in ((s.get('region') or '') + (s.get('description') or '')).lower()]
        if not (inside or sendai): continue
        eid = eid_map.get(pr['eventid'])
        if eid is None:
            PROBLEMS.append('GDACS event %s matched Gambella but has no event_id mapping' % pr['eventid']); continue
        aff = disp = deaths = houses = crop = ''
        for s in sendai:
            if s['sendainame'] == 'affected': aff = s['sendaivalue']
            elif s['sendainame'] == 'displaced': disp = s['sendaivalue']
            elif s['sendainame'] == 'death': deaths = s['sendaivalue']
            elif s['sendainame'] == 'agriculture': crop = norm(s['description']) + ' (no count; GDACS text, region field "%s")' % s['region']
            else: houses = norm(s['description']) + ' (no count; GDACS "%s" record, region field "%s")' % (s['sendainame'], s['region'])
        lg = LOG['gdacs/%s_%s.json' % (pr['eventtype'], pr['eventid'])]
        fl = pr['eventtype'] == 'FL'
        note = ('GDACS %s event %s, alert %s. Centroid %.3fE %.3fN is %s the Gambella ADM1 polygon (point-in-polygon test, mine). ' %
                (pr['eventtype'], pr['eventid'], d.get('alertlevel'), lon, lat, 'inside' if inside else 'OUTSIDE'))
        if sendai:
            descs = []
            for s in sendai:
                dsc = norm(s['description']).rstrip('\u201d').strip()
                if dsc not in descs: descs.append(dsc)
            note += 'Impact fields (GDACS "sendai" records, region Gambella; onset %s): ' % sendai[0]['onset_date'][:10] + ' / '.join(descs) + ' Values are the GDACS fields as given (its "affected" field can be the non-displaced part of a total quoted in the description). GDACS does not link its original source.'
        elif fl:
            note += 'No impact figures in GDACS; older GDACS flood records copy the Dartmouth Flood Observatory archive (same id). Whole-country event, matched to Gambella by centroid only.'
        else:
            note += ('Remote-sensing agricultural drought alert covering %s; %s. No people figures. Matched to Gambella by centroid only.' %
                     (d.get('country'), (d.get('severitydata') or {}).get('severitytext')))
        ROWS.append(dict(event_id=eid, event_type='flood' if fl else 'drought', start_date=d['fromdate'][:10], end_date=d['todate'][:10],
                         year=int(d['fromdate'][:4]), woredas_or_places='Gambella Region' if sendai else 'centroid in Gambella Region',
                         people_affected=aff, people_displaced=disp, deaths=deaths, houses_or_latrines_damaged=houses, crop_or_livestock_loss=crop,
                         river_or_cause='' if fl else 'agricultural drought (GDACS/GDO indicator)',
                         source='GDACS (Global Disaster Alert and Coordination System) API, event %s %s' % (pr['eventtype'], pr['eventid']),
                         source_type='alert database (UN/EC)', url=lg['url'], accessed=lg['time'][:10], note=note,
                         geography='Gambella Region, Ethiopia' if sendai else 'Ethiopia / multi-country (centroid in Gambella)',
                         admin_level='region' if sendai else 'country', derived='yes (matched to Gambella by centroid test)' if not sendai else 'no',
                         evidence_quote=norm(d.get('htmldescription') or ''), raw_file='raw/fd_rerun/gdacs/%s_%s.json' % (pr['eventtype'], pr['eventid'])))


def dfo_rows():
    from shapely.geometry import shape, Point
    adm1 = shape(json.load(open(os.path.join(ROOT, 'data', 'gambella_adm1.geojson'), encoding='utf-8'))['features'][0]['geometry'])
    j = json.load(open(os.path.join(RR, 'dfo', 'dfo_bbox_gambella.json'), encoding='utf-8'))
    lg = LOG['dfo/dfo_bbox_gambella.json']
    eid_map = {1430: 'GAM-FL-1998-01', 3146: 'GAM-FL-2007-01', 3367: 'GAM-FL-2008-01'}
    day = lambda t: (datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=t)).strftime('%Y-%m-%d')
    for x in j['features']:
        a = x['attributes']
        if 'thiopia' not in a['COUNTRY']: continue
        pt = Point(a['LONG'], a['LAT']); inside = adm1.contains(pt)
        dist_km = 0.0 if inside else adm1.distance(pt) * 111.0
        if not inside and a['ID'] not in eid_map: continue           # other Ethiopia polygons touching the bbox, centroid outside: not used
        eid = eid_map.get(a['ID'])
        if eid is None:
            PROBLEMS.append('DFO %s centroid inside Gambella but no mapping' % a['ID']); continue
        note = ('DFO archive ID %s; main cause "%s"; severity class %s; validation "%s"; GLIDE "%s". The archive has no place-name field: ' %
                (a['ID'], a['MAINCAUSE'], a['SEVERITY'], a['VALIDATION'], str(a['GLIDENUMBE']).strip()))
        if inside:
            note += 'flood polygon centroid %.2fE %.2fN lies inside the Gambella ADM1 polygon (test is mine), but the polygon area is %.0f km2, so dead/displaced may cover a wider area than Gambella.' % (a['LONG'], a['LAT'], a['AREA'])
        else:
            note += ('centroid %.2fE %.2fN lies about %.0f km OUTSIDE the Gambella ADM1 polygon (degree distance x 111, mine); matched to this event because country = Ethiopia and dates, dead and displaced equal the Reuters report of 25 Aug 2008.' % (a['LONG'], a['LAT'], dist_km))
        ROWS.append(dict(event_id=eid, event_type='flood', start_date=day(a['BEGAN']), end_date=day(a['ENDED']), year=int(day(a['BEGAN'])[:4]),
                         woredas_or_places='not named (polygon centroid %.2fE %.2fN)' % (a['LONG'], a['LAT']), people_affected='',
                         people_displaced=a['DISPLACED'], deaths=a['DEAD'], houses_or_latrines_damaged='', crop_or_livestock_loss='',
                         river_or_cause=a['MAINCAUSE'],
                         source='Dartmouth Flood Observatory, Global Active Archive of Large Flood Events (ArcGIS feature service copy "Global_Archive_of_large_flood_events", records to Oct 2021), ID %s' % a['ID'],
                         source_type='flood archive compiled from news reports', url=lg['url'], accessed=lg['time'][:10], note=note,
                         geography='Ethiopia (flood polygon; centroid %s Gambella)' % ('inside' if inside else 'near'), admin_level='flood polygon',
                         derived='yes (matched to Gambella by centroid / date match)', evidence_quote='', raw_file='raw/fd_rerun/dfo/dfo_bbox_gambella.json'))


gdacs_rows()
dfo_rows()

# =========================================================================== GAP ROWS
G('GAP-FL-2026', 'flood', 2026, 'searched: GDACS API (Ethiopia floods to 2026-11-16), IFRC GO events, UNICEF Ethiopia mid-year sitrep 30 June 2026, web search (2 queries)',
  'https://www.unicef.org/media/183381/file/Ethiopia-Humanitarian-Situation-Report-No.3(Mid-Year),30-June-2026.pdf.pdf',
  'NOT FOUND: no Gambella flood record for 2026 in the sources opened. GDACS lists one 2026 Ethiopia flood (9-11 March 2026, centroid 37.26E 6.17N, outside Gambella). Absence of a record is not absence of a flood; the 2026 kiremt season may simply not be reported yet.',
  'web/unicef_sitrep_2026_midyear.pdf')
G('GAP-DR-GAMBELLA', 'drought', '', 'searched: EM-DAT via OWID, IFRC GO drought events (16) and appeals, GDACS drought alerts, OCHA bulletins 2017-2021, UNICEF sitreps 2022-2026, web search (3 queries)',
  'https://goadmin.ifrc.org/api/v2/event/?countries__in=65&dtype=20&limit=200',
  'NOT FOUND: no source opened gives a Gambella-specific drought impact figure (people affected, livestock or crop loss) after 2002. None of the 16 IFRC GO drought events for Ethiopia mentions Gambella. Drought rows in this file are rain-failure / food-insecurity episodes (1982, 1990, 1999, 2002), one indirect reference (2016-2018) and one GDACS remote-sensing alert (2025).',
  'ifrc/event_c65_dtype20.json')
G('GAP-EMDAT-LOCATION', 'flood/drought', '', 'EM-DAT event table via Our World in Data (meadow/emdat/2026-10-21)',
  'https://catalog.ourworldindata.org/meadow/emdat/2026-10-21/natural_disasters/natural_disasters.parquet',
  'NOT FOUND: the OWID copy of EM-DAT has no location / admin-unit text and no DisNo; columns are country, dates, type, subtype, deaths, affected, homeless, injured, damages. Gambella events cannot be identified in it. Only the Ethiopia national series is used (ethiopia_flood_drought_yearly.csv).',
  'emdat/natural_disasters.parquet')
G('GAP-RELIEFWEB', 'flood/drought', '', 'ReliefWeb / OCHA (reliefweb.int reports, disaster pages FL-2022-000356-ETH etc., API v1 and v2)',
  'https://api.reliefweb.int/v2/reports',
  'NOT ACCESSED: reliefweb.int pages returned HTTP 202 with an empty body (bot check) to curl and HTTP 403 to the fetch tool; API v1 is decommissioned (HTTP 410) and API v2 answers "You are not using an approved appname" (HTTP 403). Not bypassed. Missed because of this: OCHA Ethiopia flash update 6 Aug 2020, OCHA Gambella flood update 24 Oct 2022, OCHA situation report 1 Nov 2022, OCHA map "Flood affected areas - Gambella region", WFP/UNDP-EUE/DPPC 2002 mid-season assessment of Gambella, UNICEF flash update May 2025. OCHA bulletins were read from ecoi.net copies instead.',
  'reliefweb/rw_api_v2_gambella_flood.json')
G('GAP-EDRMC', 'flood/drought', '', 'Ethiopia Disaster Risk Management Commission (EDRMC / NDRMC) flood alerts and contingency plans',
  'https://edrmc.gov.et/',
  'NOT ACCESSED: edrmc.gov.et and ndrmc.gov.et did not respond (connection failed, HTTP 000) on 2026-11-15 and 2026-11-16. NDRMC figures appear only as quoted by IFRC (2020) and OCHA (2021).')
G('GAP-NEWS-BLOCKED', 'flood', '', 'Addis Standard (addisstandard.com ?p=29184, 29256, 30163, 37878, 12994, 22187, 45776), The New Humanitarian / IRIN (nodes 227422, 227728, 2008/08/27, 2006/08/24), FloodList, IOM DTM, Lutheran World Federation Ethiopia',
  'https://addisstandard.com/?p=29184',
  'NOT ACCESSED: these sites returned HTTP 403 (bot protection); not bypassed. Leads seen only in search snippets and therefore not entered as figures: Addis Standard Aug 2022 "4,139 households displaced in four districts (2,040 Itang, 1,000 Lare)"; IRIN Aug 2008 (Lare and Itang woredas); IRIN "floods killed two and displaced more than 6,000" (undated); LWF 2014 "latrines and sanitation facilities have collapsed" in flooded camps.')
G('GAP-DFO-ORIGINAL', 'flood', '', 'Dartmouth Flood Observatory original archive files (FloodArchive.xlsx, MasterListrev.htm)',
  'https://floodobservatory.colorado.edu/temp/FloodArchive.xlsx',
  'NOT ACCESSED: the original file URLs return a 236-byte error page (HTTP 404). An ArcGIS-hosted copy of the archive was used instead; its latest record begins 2021-10-06 (5,131 records), so DFO gives nothing for 2022-2026. DFO record 455 (27 Aug - 1 Sep 1990, 50,300 displaced, centroid 35.20E 7.00N) and 696 (Sept 1992) lie just outside Gambella and were left out.',
  'dfo/dfo_maxdate.json')
G('GAP-UNHCR-CAMPS', 'flood', '', 'UNHCR Gambella documents opened: data.unhcr.org 119362, 29942, news 9642 (plus the camp profiles 62617-76452, 94526, 122411 read in the earlier run)',
  'https://data.unhcr.org/en/documents/download/119362',
  'NOT FOUND: no flood damage report with figures for Kule, Tierkidi, Nguenyyiel, Jewi, Pugnido, Pugnido 2 or Okugo camps. What was found concerns Leitchuor and Nip Nip (flooded August 2014, closed, refugees moved to Jewi in May 2015), Pagak and Pamdong transit sites (2014) and Matar (2025). Camp profiles mention flood-prone terrain and road/drainage needs without event data. UNHCR East Africa Floods Appeal 2024 (unhcr.org) and data.unhcr.org search did not load.',
  'web/unhcr_119362.pdf')

# =========================================================================== write
if PROBLEMS:
    print('PROBLEMS - CSV NOT WRITTEN'); [print('  ', p) for p in PROBLEMS]; sys.exit(1)

def sk(r):
    gap = r['event_id'].startswith('GAP')
    return (gap, str(r['year']) if r['year'] != '' else '9999', r['event_id'], r['source_type'], r['source'])
ROWS.sort(key=sk)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
    for r in ROWS: w.writerow(r)
ev = sorted({r['event_id'] for r in ROWS if not r['event_id'].startswith('GAP')})
print('wrote', OUT, len(ROWS), 'rows;', len(ev), 'events;', sum(1 for r in ROWS if r['event_id'].startswith('GAP')), 'gap rows; quotes checked OK')
