"""fd02_download_web.py - documents/news pages fetched in the 2026-11-16 run for the flood/drought event file.
Saves to raw/fd_rerun/web/, logs HTTP status to raw/fd_rerun/download_log.tsv. A 403/202/000 status means NOT ACCESSED.
Run: python -P scripts/fd02_download_web.py ; then pdftotext / html2txt by fd03."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fd01_download import fetch
URLS = [
 ('ocha_bulletin_2021_09_06.pdf', 'https://www.ecoi.net/en/file/local/2060072/060921_humanitarian_bulletin_final.pdf'),
 ('eue_gamb1099.html', 'https://www.africa.upenn.edu/Hornet/gamb1099.html'),
 ('allafrica_202409090289.html', 'https://allafrica.com/stories/202409090289.html'),
 ('albawaba_1581088.html', 'https://www.albawaba.com/news/flooding-displaces-thousands-ethiopia-1581088'),
 ('radarafrica_28888.html', 'https://radarafrica.com/?p=28888'),
 ('mg_2007_07_31.html', 'https://mg.co.za/article/2007-07-31-nearly-12000-ethiopians-left-homeless-by-floods'),
 ('ajol_ejss_274517.pdf', 'https://ajol.info/index.php/ejss/article/view/274517/259163'),
 ('aau_thesis_itang.pdf', 'https://etd.aau.edu.et/bitstreams/777b5bca-1e88-4cc2-a0c8-c1e762cb7e10/download'),
 ('chijournal_C513.html', 'https://www.chijournal.org/C513'),
 ('rw_flash_2020_08_06.html', 'https://reliefweb.int/report/ethiopia/ethiopia-floods-flash-update-6-august-2020'),
 ('as_22187.html', 'https://addisstandard.com/?p=22187'),
 ('as_45776.html', 'https://addisstandard.com/?p=45776'),
 ('agelgl_2023_09.html', 'https://agelgl.blogspot.com/2023/09/floods-displace-thousands-in-gambella.html'),
 ('nbi_bas_baseline.pdf', 'https://nilebasin.org/sites/default/files/2024-08/144_BAS%20Project%20Baseline%20Information.pdf'),
 ('rw_response_situation_update.html', 'https://response.reliefweb.int/ethiopia/situation-update'),
 ('charter_824.html', 'https://disasterscharter.org/activations/flood-large-in-ethiopia-activation-824-'),
 ('unhcr_refworld_48b3b2189.html', 'https://webarchive.archive.unhcr.org/20240420132229mp_/https://www.refworld.org/docid/48b3b2189.html'),
]
URLS += [tuple(l.rstrip('\n').split('\t')) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fd02_extra_urls.tsv'), encoding='utf-8') if l.strip()] if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fd02_extra_urls.tsv')) else []
if __name__ == '__main__':
    for n, u in URLS:
        fetch('web', n, u)
