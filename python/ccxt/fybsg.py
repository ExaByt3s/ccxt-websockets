# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.fybse import fybse


class fybsg (fybse):

    def describe(self):
        return self.deep_extend(super(fybsg, self).describe(), {
            'id': 'fybsg',
            'name': 'FYB-SG',
            'countries': ['SG'],  # Singapore
            'has': {
                'CORS': False,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766513-3364d56a-5edb-11e7-9e6b-d5898bb89c81.jpg',
                'api': 'https://www.fybsg.com/api/SGD',
                'www': 'https://www.fybsg.com',
                'doc': 'https://fyb.docs.apiary.io',
            },
            'markets': {
                'BTC/SGD': {'id': 'SGD', 'symbol': 'BTC/SGD', 'base': 'BTC', 'quote': 'SGD'},
            },
        })
