"""gbv15_build.py - build data/gambella_safety_gbv.csv and data/sanitation_violence_literature.csv.
Inputs (all downloaded 2026-11-16 by gbv10_fetch.py / gbv_01_dhs_download.py / gbv12_lit_abstracts.py):
  raw/gbv3/dhs/dhs_et_dv_{national,subnational}.json  (DHS Program API)
  raw/gbv3/web/*.txt (KAP reports, HVACS, UNHCR docs, GPC, Europe PMC full texts), raw/gbv3/pubmed/*
DHS rows are read programmatically; all other values were transcribed by hand from the cited text files
(file + line/table given in 'note'). Run: python -I scripts/gbv15_build.py"""
import json, os, csv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
ACC = "2026-11-16"
COLS = ["theme", "indicator", "value", "unit", "year", "geography", "admin_level", "disaggregation", "measure_type",
        "sample", "source", "source_type", "url", "accessed", "derived", "note"]
rows = []
def add(**k):
    r = {c: "" for c in COLS}; r.update(accessed=ACC, derived="no"); r.update(k); rows.append(r)

# ---------------- DHS (programmatic) ----------------
DV = ["DV_EXSV_W_EVR", "DV_EXSV_W_12M", "DV_ESVO_W_EVR", "DV_ESVO_W_12M", "DV_EXPV_W_EVR", "DV_EXPV_W_12M",
      "DV_SPVL_W_SEX", "DV_SPV1_W_SEX", "DV_SPVL_W_POS", "DV_SPV1_W_POS", "DV_SPVL_W_ANY", "DV_SPV1_W_ANY",
      "DV_STPV_W_HLP", "DV_STPV_W_NTL"]
nat = json.load(open(R("raw", "gbv3", "dhs", "dhs_et_dv_national.json"), encoding="utf-8"))
sub = json.load(open(R("raw", "gbv3", "dhs", "dhs_et_dv_subnational.json"), encoding="utf-8"))
def pick(data, geo_test):
    out = {}
    for r in data:
        if r["IndicatorId"] in DV and r["IsPreferred"] == 1 and geo_test(r):
            out[(r["SurveyId"], r["IndicatorId"])] = r
    return out
g = pick(sub, lambda r: "gamb" in r["CharacteristicLabel"].lower())
n = pick(nat, lambda r: r["CharacteristicCategory"].startswith("Total"))
seen = set()
for geo, lvl, d, bd in (("Gambela Region", "region", g, "subnational"), ("Ethiopia", "national", n, "national")):
    for (s, i), r in sorted(d.items()):
        mt = "prevalence"
        theme = "help_seeking" if i.startswith("DV_STPV") else ("sexual_violence" if "SV" in i or i.endswith("SEX") else "physical_or_partner_violence")
        add(theme=theme, indicator=r["Indicator"] + f" [{i}]", value=r["Value"], unit="% of women 15-49" if not i.startswith("DV_STPV") else "% of women who experienced violence",
            year=r["SurveyYear"], geography=geo, admin_level=lvl, disaggregation="women 15-49; " + (r["ByVariableLabel"] or "all women in DV module"),
            measure_type=mt, sample=f"n={r['DenominatorUnweighted']} unweighted (weighted {r['DenominatorWeighted']}); women selected for DV module",
            source=f"DHS Program API, {s} Ethiopia DHS {r['SurveyYear']}", source_type="official statistics (DHS)",
            url=f"https://api.dhsprogram.com/rest/dhs/data?countryIds=ET&breakdown={bd}&indicatorIds={i}&f=json",
            note=f"Indicator {i}; IsPreferred=1. Self-reported survey prevalence (household survey). Regional sample is small; API gives no CI. "
                 "DHS samples households from the census frame; whether refugee camps are included was not verified in this run - treat as host-population figure.")

# ---------------- UNHCR / IRC WASH KAP (KPC) surveys, Dec 2017 ----------------
KAP = {"Kule": ("149", "264", "kap_report_kule.txt"), "Pugnido": ("150", "269", "kap_report_pugnido.txt"),
       "Pugnido II": ("159", "302", "kap_report_pugnido2.txt"), "Tierkidi": ("152", "274", "kap_report_tierkidi.txt")}
def kap(camp, ind, val, mt, note, unit="% of surveyed population/households", theme="latrine_safety"):
    sid, did, f = KAP[camp]
    add(theme=theme, indicator=ind, value=val, unit=unit, year=2017, geography=f"{camp} refugee camp", admin_level="camp",
        disaggregation="all respondents (household survey)", measure_type=mt,
        sample="384 households planned (single-proportion formula, p=50%, d=5%)" + ("; 383 informants" if camp == "Kule" else "; 385 informants" if camp == "Pugnido II" else ""),
        source=f"IRC/UNHCR WASH KAP (KPC) survey report, {camp} camp, Dec 2017 (UNHCR Microdata Library catalog {sid})",
        source_type="NGO/UN survey report", url=f"https://microdata.unhcr.org/index.php/catalog/{sid}/download/{did}",
        note=f"raw/gbv3/web/{f} section 4.4. " + note)
kap("Kule", "Adults who sometimes defecate in the bush at night", 8, "prevalence", "Text: 'night time defecation experience 8 % of adults defecate some times in the bush over night'.", theme="open_defecation_night")
kap("Pugnido", "Adults who sometimes defecate in the bush at night", 12, "prevalence", "Text: '12 % of adults defecate some times in the bush over night'.", theme="open_defecation_night")
kap("Pugnido II", "Adults who defecate in the bush at night", 10, "prevalence", "Main reason given in report: 'darkness to use latrine overnight'.", theme="open_defecation_night")
kap("Tierkidi", "Adults who practise open defecation in the bush at night", 7, "prevalence", "Text: 'Overnight 7% of adults practice open defecation in the bush by considering latrine is not safe'.", theme="open_defecation_night")
kap("Kule", "Latrines that do not give privacy", 27, "perception", "Main reason: lock not working; 68% 'don't know whether have privacy or not' (as printed).")
kap("Pugnido", "Latrines that do not give privacy", 69, "perception", "Main reasons as printed: 'too close to house, not sex segregated'.")
kap("Pugnido II", "Respondents satisfied with latrine privacy", 83, "perception", "As printed.")
kap("Pugnido II", "Respondents who feel safe when using latrine", 71, "perception", "As printed; the report says 'the remaining 13% not feel safe' although 71+13 is not 100 - remainder unexplained.")
kap("Pugnido II", "Respondents who do not feel safe when using latrine", 13, "perception", "Main reason as printed: 'latrine is not sex segregated'. See doubt on 71% row.")
kap("Tierkidi", "Respondents not satisfied with latrine privacy", 85, "perception", "Reasons as printed: '25% not sex segregated 25%lock missed and also 50% infrastructure poor' (shares of reasons).")
kap("Tierkidi", "Reason for privacy dissatisfaction: latrine not sex-segregated", 25, "perception", "% of reasons among dissatisfied respondents, as printed.", unit="% of reasons given")
kap("Tierkidi", "Reason for privacy dissatisfaction: lock missing", 25, "perception", "% of reasons among dissatisfied respondents, as printed.", unit="% of reasons given")
kap("Kule", "Adults who practise open defecation (daytime/general)", 6, "prevalence", "93% used household latrine, 1% communal latrine.", theme="open_defecation")
kap("Pugnido", "Adults who practise open defecation (daytime/general)", 5, "prevalence", "84% HH latrine, 8% shared others' latrine, 2% communal.", theme="open_defecation")
kap("Pugnido II", "Adults who practise open defecation (daytime/general)", 3, "prevalence", "97% used HH latrine.", theme="open_defecation")
kap("Tierkidi", "Adults who practise open defecation (daytime/general)", 5, "prevalence", "92% HH latrine, 3% communal.", theme="open_defecation")

# ---------------- HVACS 2024 (refugee camps Ethiopia) ----------------
HV = dict(source="RRS, UNHCR & Baobab RPC (2025) Ethiopia Humanitarian Violence Against Children and Youth Survey (HVACS) 2024 summary report",
          source_type="survey report (UN/government/research consortium)",
          url="https://cdn.togetherforgirls.org/assets/files/Ethiopia-Humanitarian-Violence-Against-Children-and-Youth-Survey-summary-report.pdf",
          year=2024, measure_type="prevalence")
HVG = "Ethiopia refugee camps (20 camps; Gambela office camps: Jewi, Kule, Nguenyyiel, Okugo, Pinyudo-1, Tierkidi)"
HVS = "1,937 females (941 aged 18-24; 996 aged 13-17) and 1,536 males (682; 854); weighted"
def hv(ind, val, dis, note, unit="%", geo=HVG, lvl="national", mt="prevalence", theme="sexual_violence_children"):
    add(theme=theme, indicator=ind, value=val, unit=unit, geography=geo, admin_level=lvl, disaggregation=dis, sample=HVS,
        note="raw/gbv3/web/hvacs_summary_report.txt " + note, **{k: v for k, v in HV.items() if k != "measure_type"}, measure_type=mt)
hv("Experienced sexual violence before age 18", 13.9, "females 18-24", "Key findings p.8.")
hv("Experienced sexual violence before age 18", 2.2, "males 18-24", "Key findings p.8.")
hv("Experienced sexual violence in past 12 months", 4.4, "females 13-17", "Figure 2 shows 4.4; text says 'Four percent'; factsheet 4.4%.")
hv("Experienced sexual violence in past 12 months", 3.8, "males 13-17", "p.9.")
hv("Experienced physical violence before age 18", 24.4, "females 18-24", "Figure 1 / factsheet.", theme="physical_violence_children")
hv("Experienced any violence (sexual, physical or emotional) before age 18", 31.9, "females 18-24", "Figure 3 overall / factsheet 31.9%; text rounds to 32%.", theme="any_violence_children")
hv("Experienced any violence (sexual, physical or emotional) before age 18", 26.4, "males 18-24", "Figure 3 overall / factsheet.", theme="any_violence_children")
hv("Experienced any violence (sexual, physical or emotional) before age 18", 28.4, "females 18-24", "Figure 3 (by region). Value read from chart labels in extracted PDF text (two 28.4 labels under 'Gambela'); text says 'Gambella, where both genders reported similar levels'. Check against PDF figure.", geo="Gambela RRS regional office camps (Jewi, Kule, Nguenyyiel, Okugo, Pinyudo-1, Tierkidi)", lvl="region", theme="any_violence_children")
hv("Experienced any violence (sexual, physical or emotional) before age 18", 28.4, "males 18-24", "Figure 3; see doubt on female row.", geo="Gambela RRS regional office camps (Jewi, Kule, Nguenyyiel, Okugo, Pinyudo-1, Tierkidi)", lvl="region", theme="any_violence_children")
hv("First incident of childhood sexual violence occurred in respondent's home", 39.1, "females 18-24 who experienced SV", "p.14 / Figure 9.", unit="% of survivors", theme="location_of_violence")
hv("First incident of childhood sexual violence occurred after arriving in the refugee camp", 32.3, "females 18-24 who experienced SV", "p.14.", unit="% of survivors", theme="location_of_violence")
hv("Most recent sexual violence occurred outside (roads/streets, markets/shops, schools, lakes/rivers or other bodies of water, fields/other natural areas)", 30.5, "females 13-17 who experienced SV in past 12 months", "p.14 / Figure 10. Category combines several outdoor locations; toilets/latrines are not a separate category in the summary report.", unit="% of survivors", theme="location_of_violence")
hv("Most recent sexual violence occurred in the evening", 43.2, "females 13-17 who experienced SV in past 12 months", "p.14.", unit="% of survivors", theme="location_of_violence")
for ind, v in (("Told someone about sexual violence", 50), ("Knew of a place to seek help", 28), ("Sought help", 24), ("Received help", 19)):
    add(theme="help_seeking", indicator=ind, value=v, unit="% of survivors", year=2024, geography=HVG, admin_level="national",
        disaggregation="females 18-24 who experienced sexual violence (any incident)", measure_type="prevalence", sample=HVS,
        source="Baobab RPC (2025) Violence against children and youth in refugee settings in Ethiopia: Factsheet", source_type="survey factsheet (research consortium)",
        url="https://cdn.togetherforgirls.org/assets/files/Violence-against-children-and-youth-in-refugee-settings-in-Ethiop.pdf",
        note="raw/gbv3/web/hvacs_factsheet_tfg.txt, 'Child survivors need additional support' panel. Shows how few incidents reach services (under-reporting).")

# ---------------- Peer-reviewed Gambella studies ----------------
def pr(theme, ind, val, year, geo, lvl, dis, sample, src, url, note, unit="%"):
    add(theme=theme, indicator=ind, value=val, unit=unit, year=year, geography=geo, admin_level=lvl, disaggregation=dis,
        measure_type="prevalence", sample=sample, source=src, source_type="peer-reviewed", url=url, note=note)
OK = ("Shifera N et al. (2025) BMJ Open 15:e086405 - Hidden GBV in Okugu Refugee Camp", "https://doi.org/10.1136/bmjopen-2024-086405")
oks = "n=416 reproductive-age women analysed (422 participated); facility-based, Mar-May 2023"
okn = "raw/gbv3/web/epmc_PMC12056619.txt Tables 2-3. Recall period not stated in the abstract/tables read. GBV definition in this paper also counts dowry/bride price and multiple partners (operational definition), so 64.4% is not comparable with DHS."
pr("gbv_any", "Gender-based violence (any form, study definition)", 64.4, 2023, "Okugo (Okugu) refugee camp", "camp", "women 15-49", oks, *OK, okn + " 95% CI 59-69.")
pr("physical_violence", "Physical violence", 51.9, 2023, "Okugo (Okugu) refugee camp", "camp", "women 15-49", oks, *OK, okn)
pr("sexual_violence", "Sexual violence (any)", 34.9, 2023, "Okugo (Okugu) refugee camp", "camp", "women 15-49", oks, *OK, okn + " 145/416.")
pr("sexual_violence", "Forced sex", 11.3, 2023, "Okugo (Okugu) refugee camp", "camp", "women 15-49", oks, *OK, okn + " 47/416.")
pr("sexual_violence", "Attempted unwanted sex", 22.6, 2023, "Okugo (Okugu) refugee camp", "camp", "women 15-49", oks, *OK, okn + " 94/416.")
pr("sexual_violence", "Unwelcome touch", 15.6, 2023, "Okugo (Okugu) refugee camp", "camp", "women 15-49", oks, *OK, okn + " 65/416.")
PY = ("Hadush F, Tsegaye D, Legass SA, Abebe E, Zenu S (2023) BMC Public Health - IPV among South Sudanese refugee women in Pinyudo camp", "https://doi.org/10.1186/s12889-023-16343-x")
pys = "n=406 married refugee women; community-based, Mar-Jun 2021"
pyn = "raw/gbv3/web/epmc_PMC10367380.txt results. IPV includes physical, sexual, emotional violence and controlling behaviour by husband in past 12 months."
pr("partner_violence", "Intimate partner violence, past 12 months", 48.3, 2021, "Pugnido (Pinyudo) refugee camp", "camp", "married women", pys, *PY, pyn + " 95% CI 43.6-53.2; 196/406.")
pr("sexual_violence", "Sexual IPV, past 12 months", 35.5, 2021, "Pugnido (Pinyudo) refugee camp", "camp", "married women", pys, *PY, pyn + " 144/406.")
pr("partner_violence", "Physical IPV, past 12 months", 40.4, 2021, "Pugnido (Pinyudo) refugee camp", "camp", "married women", pys, *PY, pyn + " 164/406.")
GT = ("Gedefa AG et al. (2024) Front Public Health 12:1412788 - IPV in Gambella town", "https://doi.org/10.3389/fpubh.2024.1412788")
gts = "n=396 partnered women 15-49; community-based, 2021"
gtn = "raw/gbv3/web/epmc_PMC11163098.txt Table 2. Host community (Gambella town, 5 kebeles), not a camp."
pr("partner_violence", "Intimate partner violence, lifetime", 58.8, 2021, "Gambella town", "woreda", "partnered women 15-49", gts, *GT, gtn + " 95% CI 54.0-63.6.")
pr("partner_violence", "Intimate partner violence, last 12 months", 51.8, 2021, "Gambella town", "woreda", "partnered women 15-49", gts, *GT, gtn + " 95% CI 46.7-56.8; 205/396.")
pr("sexual_violence", "Sexual IPV, last 12 months", 38.9, 2021, "Gambella town", "woreda", "partnered women 15-49", gts, *GT, gtn + " 154/396.")
pr("sexual_violence", "Female elementary-school students who were subjected to rape", 34.8, 2022, "Kule refugee camp", "camp", "female elementary students",
   "n=210 (211 sampled); institution-based, May 2022", "Kong BS, Gezimu W, Demeke A, Duguma A (2023) Int J Reprod Med 2023:5559246 - Rape among female students, Kule camp",
   "https://doi.org/10.1155/2023/5559246", "raw/gbv3/web/epmc_PMC10256440.txt abstract: '73 (34.8%) were subjected to rape'. Recall period not given in the abstract; small sample.")

# ---------------- UNHCR / GPC reports: reported cases and qualitative risk statements ----------------
def un(theme, ind, val, unit, year, geo, lvl, mt, src, stype, url, note, dis="", sample=""):
    add(theme=theme, indicator=ind, value=val, unit=unit, year=year, geography=geo, admin_level=lvl, disaggregation=dis,
        measure_type=mt, sample=sample, source=src, source_type=stype, url=url, note=note)
E = "UNHCR Briefing note 'Access to energy: safeguarding refugee women and girls' (Gambella, 2018)"
un("reported_gbv", "Rape and physical assault as share of reported SGBV cases", 61, "% of reported SGBV cases", 2017, "Gambella refugee camps", "region", "reported_cases",
   E, "UN agency report", "https://data.unhcr.org/en/documents/download/64744", "raw/gbv3/web/unhcr_64744.txt 'The challenge'. Linked in text to firewood collection in remote locations. Share of reported cases only; report says SGBV is under-reported. Absolute counts NOT given.")
un("reported_gbv", "Rape and physical assault as share of reported SGBV cases", 74, "% of reported SGBV cases", 2018, "Gambella refugee camps", "region", "reported_cases",
   E, "UN agency report", "https://data.unhcr.org/en/documents/download/64744", "raw/gbv3/web/unhcr_64744.txt; first quarter of 2018 only.")
un("lighting", "Alternative energy provision for lighting (solar lanterns, lamps, street lights)", 32, "% (base not stated)", 2018, "Gambella refugee camps", "region", "reported_cases",
   E, "UN agency report", "https://data.unhcr.org/en/documents/download/64744", "raw/gbv3/web/unhcr_64744.txt: 'limited alternative energy provision for lighting (solar lanterns, lamps, street lights at only 32%)'. Denominator unclear (households? needs?). measure_type set to reported_cases only because it is an operational figure - treat as coverage claim, not survey.")
un("reported_gbv", "New GBV incidents reported by refugees (countrywide)", 15, "incidents", 2024, "Ethiopia (all refugee operations)", "national", "reported_cases",
   "UNHCR Ethiopia Operational Update, March 2024", "UN agency report", "https://data.unhcr.org/en/documents/download/108108", "raw/gbv3/web/unhcr_108108.txt GBV box: 'Refugees countrywide have reported 15 new gender-based violence (GBV) incidents including physical abuse, sexual abuse, and rape'. Reporting period presumably March 2024 (not stated precisely). Not Gambella-specific. Reported incidents are a tiny fraction of prevalence.")
un("gbv_services", "GBV case management (cases handled)", 25, "cases", 2026, "Gambella - South Sudan emergency response (new arrivals, Level 1 registered since 22 July 2025)", "region", "reported_cases",
   "UNHCR South Sudan Emergency Response - Ethiopia, Protection and Education Factsheet, May 2026", "UN agency report", "https://data.unhcr.org/en/documents/download/123066", "raw/gbv3/web/unhcr_123066.txt Achievements: '25 GBV Case Management'. Service output count, not incidence; period not stated (likely cumulative/month).")
un("sanitation_context", "Persons per latrine", 64, "persons per latrine", 2026, "Luakdong (new-arrival site, Gambella)", "camp", "reported_cases",
   "UNHCR South Sudan Emergency Response - Ethiopia, WASH Factsheet, May 2026", "UN agency report", "https://data.unhcr.org/en/documents/download/123068", "raw/gbv3/web/unhcr_123068.txt: '64 Persons Per Latrine in Luakdong *' (*average of previous weeks). Gambella factsheet (doc 123069) also gives '1:64 latrine per people, below emergency standards'. Operational monitoring figure.")
un("sanitation_context", "Latrine attendants", 0, "persons", 2026, "Gambella - South Sudan emergency response", "region", "reported_cases",
   "UNHCR South Sudan Emergency Response - Ethiopia, WASH Factsheet, May 2026", "UN agency report", "https://data.unhcr.org/en/documents/download/123068", "raw/gbv3/web/unhcr_123068.txt Achievements list.")
un("sanitation_context", "Refugee families with a household toilet (all Gambella camps)", 37, "% of families", 2019, "Gambella refugee camps (7 camps)", "region", "reported_cases",
   "UNHCR Gambella Region Situational Update, 31 Oct 2019", "UN agency report", "https://data.unhcr.org/en/documents/download/73666", "raw/gbv3/web/unhcr_73666.txt p.2: 'household toilets benefit only 37% of families', others use communal latrines or open defecation. Same doc p.1: 'Rape and domestic violence are among the highest reported SGBV cases', with under-reporting due to stigma.")
un("sanitation_context", "Refugee families with access to a household toilet", 28, "% of families", 2020, "Gambella refugee camps", "region", "reported_cases",
   "UNHCR Refugees and asylum seekers from South Sudan in Gambella Region, Situational Update, 30 June 2020", "UN agency report", "https://data.unhcr.org/en/documents/download/78202", "raw/gbv3/web/unhcr_78202.txt: 'Only 28% of refugee families have access to a household toilet, whereas most refugees utilize communal latrines or engage in open defecation'.")
QUAL = [
 ("water_firewood_risk", "Women and girls face harassment, physical attacks and rape where they collect firewood/water (Pagak reception centre)", 2020, "Pagak reception centre, Gambella", "camp",
  "UNHCR Gambella Situational Update, 30 June 2020", "https://data.unhcr.org/en/documents/download/78202", "raw/gbv3/web/unhcr_78202.txt SGBV section."),
 ("lighting", "Lack of lighting around camps enhances SGBV risk at night when accessing services; street lighting proposed for water points and communal latrines", 2018, "Ethiopia refugee camps incl. Gambella", "national",
  "UNHCR Session 2 group discussion note: Joint review of proposed solutions (SGBV and energy)", "https://data.unhcr.org/fr/documents/download/63874", "raw/gbv3/web/unhcr_63874.txt lines 8-14, 73-79. Year not printed in extracted text (cites UNDP 2018 and the 2017-2019 SGBV strategy)."),
 ("water_firewood_risk", "Women moving long distances on foot to fetch water at heightened risk of GBV; basic GBV services not yet provided (flood-displaced IDPs)", 2025, "Lare, Jikawo and Wanthoa woredas (Nuer Zone)", "woreda",
  "Global Protection Cluster Ethiopia, Monthly Protection Overview, September 2025", "https://globalprotectioncluster.org/sites/default/files/2025-10/ethiopia_monthly_protection_overview_september_2025.pdf", "raw/gbv3/web/gpc_protection_sep2025.txt 'GBV Core Services' row for Gambella. Same report WASH rows: 'Latrines not gender-segregated and lack privacy and lighting' and 'Open defecation is commonly practiced' - table layout makes attribution between Amhara (Jarri IDP sites) and Gambella rows ambiguous in the extracted text; verify in PDF."),
 ("gbv_services", "Limited protection partners and budget delays disrupting referral of GBV survivors to the One-Stop Center", 2025, "Gambella (conflict/drought affected areas)", "region",
  "Global Protection Cluster Ethiopia, Monthly Protection Overview, May 2025", "https://globalprotectioncluster.org/sites/default/files/2025-06/monthly_protection_overview_may_2025.pdf", "raw/gbv3/web/gpc_protection_may2025.txt GBV core services row; table layout merges regions - verify in PDF."),
 ("water_firewood_risk", "FGDs: women and girls exposed to higher risk of sexual, physical and psychological violence at firewood collection sites; in Gambella unmet basic needs (clothes, shoes, food) raise exploitation risk for adolescent girls", 2021, "Ethiopia refugee operations incl. Gambella", "national",
  "UNHCR Ethiopia Participatory Assessment Report 2021", "https://data.unhcr.org/en/documents/download/96333", "raw/gbv3/web/unhcr_96333.txt section 4.1 (qualitative FGDs)."),
]
for th, ind, yr, geo, lvl, src, url, note in QUAL:
    un(th, ind, "qualitative", "", yr, geo, lvl, "perception", src, "UN agency / cluster report (qualitative)", url, note)

# ---------------- NOT FOUND / NOT ACCESSED ----------------
NF = [
 ("latrine_safety", "Results of Gambella camp safety audits (share of women/girls feeling unsafe at latrines; latrines with working locks; lighting; sex segregation)", "NOT FOUND", "Gambella refugee camps", "camp",
  "UNHCR SGBV fact sheets (docs 62730, 63873, 64984, 66622) mention a quarterly Safety Audit in Tierkidi (June 2018) but give no results; no audit report found on data.unhcr.org via the documents opened.", "https://data.unhcr.org/en/documents/download/64984"),
 ("latrine_safety", "SanQoL-5 'How often do you feel unsafe using the toilet?' (Nguenyyiel & Tierkidi, Mar-Apr 2024, LSHTM/Oxfam)", "NOT ACCESSED", "Nguenyyiel and Tierkidi refugee camps", "camp",
  "Dataset restricted ('Request a copy' / data sharing agreement). Only the codebook and questionnaire are open; codebook confirms variables safety_toilet_end, lockinside, lockoutside, useatnight. No results publication found in this run.", "https://datacompass.lshtm.ac.uk/id/eprint/5151/"),
 ("latrine_safety", "UNHCR WASH KAP 2017 microdata frequencies for latrine-safety variables (s2e* series)", "NOT ACCESSED", "Kule, Pugnido, Pugnido II, Tierkidi", "camp",
  "Microdata are licensed (account + request). Public variable pages show 'Valid: 0' and no frequencies; only the PDF reports were used.", "https://microdata.unhcr.org/index.php/catalog/149/data-dictionary"),
 ("reported_gbv", "GBVIMS reported SGBV incident counts by Gambella camp and year", "NOT FOUND", "Gambella refugee camps", "camp",
  "Not in UNHCR factsheets/situational updates opened (64744, 73666, 78202, 108108, 123066, 123069) nor GPC overviews (May, Sep 2025). GBVIMS data are not published at camp level.", "https://data.unhcr.org/en/country/eth"),
 ("sexual_violence_children", "Ethiopia VACS 2022 estimate for Gambella Region", "NOT FOUND", "Gambela Region", "region",
  "Factsheet: Gambella was sampled but separate estimates only for Oromia, Somali, SNNP and Addis Ababa (females). National headline percentages are graphics, not extractable text.", "https://cdn.togetherforgirls.org/assets/files/Ethiopia-VACS-2022-factsheet.pdf"),
 ("sexual_violence_children", "HVACS 2024 full report appendix tables (camp/region detail, location incl. latrines)", "NOT ACCESSED", "Ethiopia refugee camps", "national",
  "Population Council Knowledge Commons PDF returned HTTP 403 (bot check) - not bypassed. Summary report and factsheet used instead.", "https://knowledgecommons.popcouncil.org/cgi/viewcontent.cgi?article=1055&context=hubs_humanitarian"),
 ("latrine_safety", "Peer-reviewed study measuring sanitation-related violence or latrine safety in Gambella camps", "NOT FOUND", "Gambella Region", "region",
  "PubMed searches (raw/gbv3/pubmed/pubmed_*.json, lit_search.json) and Semantic Scholar search (s2_gambella.json) returned no Gambella study on sanitation-related violence.", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"),
]
for th, ind, val, geo, lvl, note, url in NF:
    add(theme=th, indicator=ind, value=val, geography=geo, admin_level=lvl, measure_type="", source="see note", source_type="", url=url, note=note)

def write(path, cols, data):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(data)
os.makedirs(R("data"), exist_ok=True)
write(R("data", "gambella_safety_gbv.csv"), COLS, rows)

# ---------------- literature table ----------------
LC = ["authors", "year", "journal", "country", "design", "n", "finding_verbatim_or_close", "effect_size", "doi_or_url", "source_opened", "note"]
lit = [
 dict(authors="Jadhav A, Weitzman A, Smith-Greenaway E", year=2016, journal="BMC Public Health 16:1139", country="India", design="Cross-sectional, NFHS-3 (2005-06), logistic regression",
      n="75,619 women", finding_verbatim_or_close="Net of their socioeconomic status, women who use open defecation are twice as likely to face NPSV as women with a household toilet.",
      effect_size="Open air vs household toilet, past-year NPSV: OR 2.14 (1.28-3.56) bivariate; 2.15 (1.11-4.15) demographics-adjusted; 2.25 (1.13-4.50) full model. Pit vs toilet: 0.59 (0.20-1.70), n.s.",
      doi_or_url="https://doi.org/10.1186/s12889-016-3797-z", source_opened="Europe PMC full text PMC5100257, Table 2", note="Falsification test: open defecation not associated with intimate partner sexual violence."),
 dict(authors="Winter SC, Barchi F", year=2016, journal="International Journal of Environmental Health Research 26(3):291-305 (online 2015)", country="Kenya", design="Cross-sectional, Kenya DHS 2008",
      n="NOT FOUND (not in abstract)", finding_verbatim_or_close="women who primarily practice open defecation (OD), particularly in disorganized communities, had higher odds of experiencing recent non-partner violence.",
      effect_size="NOT ACCESSED (full text paywalled; abstract gives no odds ratio)", doi_or_url="https://doi.org/10.1080/09603123.2015.1111309", source_opened="PubMed abstract PMID 26593879; Crossref metadata", note="Outcome is non-partner violence (physical and/or sexual)."),
 dict(authors="Sommer M, Ferron S, Cavill S, House S", year=2015, journal="Environment and Urbanization 27(1):105-116 (online 30 Dec 2014)", country="Global (review)", design="Review of evidence and practice",
      n="not applicable", finding_verbatim_or_close="Findings indicate the need for more systematic, reliable, and ethically conducted monitoring and learning on this topic to build a more solid evidence base",
      effect_size="none (review)", doi_or_url="https://doi.org/10.1177/0956247814564528", source_opened="Crossref abstract (publisher page HTTP 403, not bypassed)", note="Stresses lack of valid documentation and sensitivity of the topic."),
 dict(authors="Kayser GL, Chokhandre P, Rao N, Singh A, McDougal L, Raj A", year=2021, journal="SSM - Population Health 13:100738", country="India", design="Cross-sectional, NFHS-4 (2015-16), multivariable logistic regression",
      n="74,698 women 15-49", finding_verbatim_or_close="In rural India, those who lack private household sanitation, compared to those with a household toilet, have significantly greater odds of NMSV (AOR = 2.45; p < 0.05).",
      effect_size="Rural: AOR 2.45 (p<0.05); total sample: no significant association; urban: n.s. Past-year NMSV prevalence 0.45%.", doi_or_url="https://doi.org/10.1016/j.ssmph.2021.100738", source_opened="Europe PMC full text PMC7903128 (abstract)", note="46.2% of households lacked private sanitation (37.3% open defecation, 8.9% shared)."),
 dict(authors="Gibbs A, Reddy T, Khanyile D, Cawood C", year=2021, journal="Global Public Health 16(4):590-596", country="South Africa", design="Population-based cross-sectional survey, poor communities in 4 districts",
      n="10,635 women 18-24", finding_verbatim_or_close="those reporting a shared toilet were more likely to report past year experience of non-partner rape ... compared to those with their own toilet indoors.",
      effect_size="Shared toilet vs own indoor toilet: aOR 1.45 (95% CI 1.17-1.80); past-year non-partner rape prevalence 5.7%", doi_or_url="https://doi.org/10.1080/17441692.2020.1813787", source_opened="PubMed abstract PMID 32896218", note=""),
 dict(authors="Barchi F, Winter SC", year=2020, journal="Violence Against Women 26(10):1101-1119", country="20 sub-Saharan African countries", design="Multicountry cross-sectional, DHS",
      n="138,097 women", finding_verbatim_or_close="The results suggest that sanitation and water access are associated with risk of NPV in a number of countries in the region, particularly in urban settings.",
      effect_size="Not in abstract (country-specific models); 12-month NPV prevalence 2.3-11.3% across countries", doi_or_url="https://doi.org/10.1177/1077801219853370", source_opened="PubMed abstract PMID 31230569", note="Ethiopia inclusion not checked (full text not opened)."),
 dict(authors="Chi H, Puno-Balagosa A, Jain A, Subramanian SV, Kim R", year=2026, journal="Social Science & Medicine 393:119005", country="31 LMICs", design="Three-level logistic regression, DHS 2013-2021",
      n="259,208 women 15-49", finding_verbatim_or_close="women who used shared toilet facilities (AOR = 1.16, 95 % CI = 1.01-1.34) and who had no facilities (AOR = 1.40, 95 % CI = 1.17-1.68) had greater risk for NPSV.",
      effect_size="Shared toilet AOR 1.16 (1.01-1.34); no facility AOR 1.40 (1.17-1.68); public water source AOR 1.27 (1.06-1.52); open water source AOR 1.37 (1.02-1.84). Past-year NPSV 0.5%.",
      doi_or_url="https://doi.org/10.1016/j.socscimed.2026.119005", source_opened="PubMed abstract PMID 41605000", note="Country list (whether Ethiopia is included) not checked."),
 dict(authors="Bandyopadhyay S, Sarkar S, Sensarma R", year=2023, journal="Scientific Reports 13", country="India", design="Cross-sectional, NFHS-4 (2015-16); logistic regression, IPWRA, PSM",
      n="NOT FOUND in text read", finding_verbatim_or_close="We find that NPV decreases with access to drinking water, while IPV decreases with provision of toilets.",
      effect_size="IPWRA ATET on NPV: drinking water -0.005, toilet -0.004 (toilet not statistically significant); PSM: -0.005 and -0.010", doi_or_url="https://doi.org/10.1038/s41598-023-37879-3", source_opened="Europe PMC full text PMC10382593", note="Article number not recorded - use DOI."),
 dict(authors="Winter SC, Johnson L, Dzombo MN", year=2023, journal="Frontiers in Public Health 11:1191101", country="Kenya (Nairobi informal settlement)", design="Probability-sample cross-sectional survey; chi-square and multivariate logistic regression",
      n="550 women", finding_verbatim_or_close="individual-level and technological factors may be critical factors in actual experiences of violence.",
      effect_size="Not in abstract", doi_or_url="https://doi.org/10.3389/fpubh.2023.1191101", source_opened="PubMed abstract PMID 37841717", note="Outcome: past-year sanitation-related violence (experienced, observed, heard)."),
]
write(R("data", "sanitation_violence_literature.csv"), LC, lit)
print(len(rows), "rows safety/gbv;", len(lit), "literature rows")
