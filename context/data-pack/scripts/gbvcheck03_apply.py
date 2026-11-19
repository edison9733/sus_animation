"""gbvcheck03_apply.py - independent checker (2026-11-16). Applies certain fixes and a 'verified' column to
data/gambella_safety_gbv.csv and data/sanitation_violence_literature.csv, based on sources re-downloaded by
scripts/gbvcheck01_redownload.sh into raw/gbvcheck/ (DHS rows were compared programmatically by gbvcheck02_dhs.py).
Idempotent. To rebuild: python -I scripts/gbv15_build.py ; python -I scripts/gbvcheck03_apply.py"""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)
CHK = " [check 2026-11-16: "

def load(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f); return rd.fieldnames, list(rd)
def save(p, cols, rows):
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
def mark(r, v, why):
    r["verified"] = v
    if CHK not in r["note"]:
        r["note"] = r["note"] + CHK + why + "]"

# ---------------- safety / GBV ----------------
p = R("data", "gambella_safety_gbv.csv")
cols, rows = load(p)
if "verified" not in cols: cols.append("verified")
for r in rows:
    s, url, ind, val = r["source"], r["url"], r["indicator"], r["value"]
    if s.startswith("DHS Program API"):
        if "[DV_STPV" in ind:  # fix: base is women who experienced violence, not all women in DV module (DHS indicator definition)
            r["disaggregation"] = "women 15-49 who ever experienced physical or sexual violence"
        mark(r, "yes", "value and denominators match fresh DHS API download raw/gbvcheck/dhs_*.json (IsPreferred=1)")
    elif "WASH KAP" in s:
        mark(r, "yes", "re-downloaded report (same file hash); figure found in section 4.4 text")
    elif "HVACS" in s or "Factsheet" in s:
        if "Gambela RRS" in r["geography"]:
            mark(r, "yes", "re-downloaded PDF p.19 Figure 3 shows two 28.4 labels for Gambela and text says both genders similar; read from chart labels, PDF not rendered")
        else:
            mark(r, "yes", "re-downloaded PDF (same hash); value found in text or figure labels")
    elif r["source_type"] == "peer-reviewed":
        mark(r, "yes", "fresh Europe PMC full text; value, n and study period match")
    elif "63874" in url:
        mark(r, "no", "statement confirmed in re-downloaded PDF, but the year 2018 is not printed in the document - year is the collector's inference")
    elif "monthly_protection_overview_may_2025" in url:
        mark(r, "no", "re-downloaded PDF: GBV core services table lists Amhara, Gambella, South Ethiopia, Oromia in one block; the referral/One-Stop Center text sits next to 'Gambella' but mentions Debre Birhan Hospital (Amhara) and areas of West Guji/Guji/Borana (Oromia) - attribution to Gambella cannot be confirmed")
    elif "september_2025" in url:
        mark(r, "yes", "re-downloaded PDF: GBV row for Gambella (Lare, Jikawo, Wanthoa) confirmed; WASH-row ambiguity noted by collector is real")
    elif val in ("NOT FOUND", "NOT ACCESSED"):
        if "64984" in url:
            mark(r, "yes", "re-downloaded 64984: safety audit in Tierkidi mentioned, no results given")
        elif "lshtm" in url:
            mark(r, "yes", "LSHTM page re-opened: data file 'Restricted ... Data Sharing Agreement'; the open xlsx is the study instrument, not data")
        elif "VACS-2022" in url:
            mark(r, "yes", "re-downloaded factsheet: separate estimates only for Oromia, Somali, SNNP, Addis Ababa")
        elif "popcouncil" in url:
            mark(r, "yes", "re-tried 2026-11-16: HTTP 403 again (not bypassed)")
        else:
            mark(r, "not_checked", "absence/access claim not independently re-tested")
    elif "data.unhcr.org" in url:
        mark(r, "yes", "re-downloaded UNHCR document (same hash); figure/statement found in text")
    else:
        mark(r, "not_checked", "not re-opened by checker")
save(p, cols, rows)

# ---------------- literature ----------------
p = R("data", "sanitation_violence_literature.csv")
cols, lit = load(p)
if "verified" not in cols: cols.append("verified")
for r in lit:
    if r["doi_or_url"].endswith("s41598-023-37879-3"):
        r["journal"] = "Scientific Reports 13:12278"
        r["n"] = "76,580 women (NPV models); 59,093 (IPV models)"
        r["effect_size"] = ("IPWRA ATET on NPV: drinking water -0.005 (95% CI -0.009 to -0.001), toilet -0.004 (-0.011 to 0.003, n.s.); "
                            "PSM: drinking water -0.006 (-0.010 to -0.002), toilet -0.010 (-0.025 to 0.005, n.s.). Table 14; percentage-point reductions as stated by the authors")
        r["note"] = "Fixed by checker 2026-11-16: PSM drinking-water value was given as -0.005 (Table 14 shows -0.006); n and article number taken from Table 14 / JATS metadata."
    r["verified"] = "yes"
    if CHK not in r["note"]:
        r["note"] = (r["note"] + CHK + "re-opened source (fresh Europe PMC / PubMed efetch / Crossref); quote and effect sizes match]").strip()
save(p, cols, lit)
from collections import Counter
print(Counter(r["verified"] for r in rows), Counter(r["verified"] for r in lit))
