"""
Generate IP-ASN rules

Author: https://github.com/RS0485
Version: 1.0

This script is used to generate IP-ASN rules for Quantumult X and Stash
The ASN infomation is from https://bgp.he.net/
"""

import os
import datetime
import requests
from bs4 import BeautifulSoup

class ASN:
    def __init__(self, asn, name, adjacencies_v4, routes_v4, adjacencies_v6, routes_v6):
        self.asn = asn
        self.name = name
        self.adjacencies_v4 = adjacencies_v4
        self.routes_v4 = routes_v4
        self.adjacencies_v6 = adjacencies_v6
        self.routes_v6 = routes_v6

def parse_asn_table(html):
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', id='asns')

    asns = []
    for tr in table.select('tbody tr'):
        cells = tr.find_all('td')
        asn = cells[0].a.text[2:]
        name = cells[1].text.strip()
        if not name:
            # 如果名称为空，则跳过这一行
            continue
        adjacencies_v4 = int(cells[2].text.replace(',', ''))
        routes_v4 = int(cells[3].text.replace(',', ''))
        adjacencies_v6 = int(cells[4].text.replace(',', ''))
        routes_v6 = int(cells[5].text.replace(',', ''))
        asns.append(ASN(asn, name, adjacencies_v4, routes_v4, adjacencies_v6, routes_v6))
    return asns

def write_in_quan_format(asns, country_or_region, file_name):
    with open(file_name, 'w') as f:
        # 写入文件头
        now = datetime.datetime.now()
        header = f"# name: {country_or_region} ASNs\n" \
                 f"# desc: {country_or_region} IP-ASN rules for Quantumult X\n" \
                 f"# author: https://github.com/RS0485/\n" \
                 f"# total: {len(asns)}\n" \
                 f"# updated: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f.write(header)

        for asn in asns:
            line = f"IP-ASN,{asn.asn},{country_or_region}"
            f.write(line + '\n')

def write_in_stash_format(asns, country_or_region, file_name):
    with open(file_name, 'w') as f:
        # 写入文件头
        now = datetime.datetime.now()
        header = f"name: {country_or_region} ASNs\n" \
                 f"desc: {country_or_region} IP-ASN rules for Stash\n" \
                 f"author: https://github.com/RS0485/\n" \
                 f"total: {len(asns)}\n" \
                 f"updated: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n" \
                 f"rules:\n"
        f.write(header)

        for asn in asns:
            line = f"  - IP-ASN,{asn.asn},{country_or_region}"
            f.write(line + '\n')

def gen_asn_rules(country_or_region, dir):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    html = requests.get(f"https://bgp.he.net/country/{country_or_region}",headers=headers)

    asns = parse_asn_table(html.text)

    # 按照 adjacencies_v4 字段降序排序，数量越多优先级越高
    asns.sort(key=lambda x: x.adjacencies_v4, reverse=True)

    write_in_quan_format(asns, country_or_region, f"{dir}/{country_or_region}-ASNs.list")
    write_in_stash_format(asns, country_or_region, f"{dir}/{country_or_region}-ASNs.stoverride")


country_or_regions = ["CN", "HK", "US"]

os.mkdir("./generated")
for country_or_region in country_or_regions:
    gen_asn_rules(country_or_region, "./generated")

