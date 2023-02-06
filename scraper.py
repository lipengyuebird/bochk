# venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2/2/2023 10:03 pm
# @Author  : Perye (Pengyu LI)
# @File    : scraper.py
# @Software: PyCharm

from typing import Dict

import dateutil
import requests
from lxml import etree
from dateutil import parser

import util.currencies
from extensions import cache


@cache.memoize(timeout=300)
def scrape_exchange_rate_hkd() -> Dict:
    html = etree.HTML(requests.get(
        'https://www.bochk.com/whk/rates/exchangeRatesForCurrency/exchangeRatesForCurrency-input.action?lang=en'
    ).text)

    last_updated = dateutil.parser.parse(
        html.xpath('//*[@id="form-div"]/form/div/table[2]/tr[1]/td/b/text()')[0].split(': ')[1].strip()).isoformat()

    result = {}

    for i in range(3, 30):
        row = html.xpath(f'//*[@id="form-div"]/form/div/table[1]/tr[{i}]/td/text()')
        print(row)
        if not row:
            break
        result[row[0].strip()] = {
            'banknotes_bank_buy': float(row[2].strip()),
            'banknotes_bank_sell': float(row[1].strip()),
            'telegraphic_transfer_bank_buy': None,
            'telegraphic_transfer_bank_sell': None,
            'last_updated': last_updated
        }

    return result


def clear_cache(base_currency: str):
    assert base_currency.upper() in util.currencies.allowed_currencies
    cache.delete_memoized(eval('scrape_exchange_rate_' + base_currency.lower()))
