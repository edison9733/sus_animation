"""Economy+sanitation: HDX COD-PS Ethiopia subnational population tables (source: CSA projections) -> raw/econ_san/hdx/."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import es01_download as d
d.fetch('hdx/cod_ps_eth.json', 'https://data.humdata.org/api/3/action/package_show?id=cod-ps-eth')
meta = json.load(open(os.path.join(d.ROOT, 'hdx', 'cod_ps_eth.json'), encoding='utf-8'))['result']
for r in meta['resources']:
    if r['name'] in ('table_eth_codps_2026.xlsx', 'eth_admpop_2023.xlsx', 'eth_admpop_adm0_2022_v2.csv', 'eth_admpop_adm1_2022_v2.csv',
                     'eth_admpop_adm2_2022_v2.csv', 'eth_admpop_adm3_2022_v2.csv'):
        d.fetch('hdx/' + r['name'], r['url'])
