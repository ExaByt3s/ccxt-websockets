# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.okcoinusd import okcoinusd
import json
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import NotSupported


class okex (okcoinusd):

    def describe(self):
        return self.deep_extend(super(okex, self).describe(), {
            'id': 'okex',
            'name': 'OKEX',
            'countries': ['CN', 'US'],
            'has': {
                'CORS': False,
                'futures': True,
                'fetchTickers': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/32552768-0d6dd3c6-c4a6-11e7-90f8-c043b64756a7.jpg',
                'api': {
                    'web': 'https://www.okex.com/v2',
                    'public': 'https://www.okex.com/api',
                    'private': 'https://www.okex.com/api',
                },
                'www': 'https://www.okex.com',
                'doc': [
                    'https://github.com/okcoin-okex/API-docs-OKEx.com',
                    'https://www.okex.com/docs/en/',
                ],
                'fees': 'https://www.okex.com/pages/products/fees.html',
            },
            'fees': {
                'trading': {
                    'taker': 0.0015,
                    'maker': 0.0010,
                },
                'spot': {
                    'taker': 0.0015,
                    'maker': 0.0010,
                },
                'future': {
                    'taker': 0.0030,
                    'maker': 0.0020,
                },
                'swap': {
                    'taker': 0.0070,
                    'maker': 0.0020,
                },
            },
            'commonCurrencies': {
                # OKEX refers to ERC20 version of Aeternity(AEToken)
                'AE': 'AET',  # https://github.com/ccxt/ccxt/issues/4981
                'FAIR': 'FairGame',
                'HOT': 'Hydro Protocol',
                'HSR': 'HC',
                'MAG': 'Maggie',
                'YOYO': 'YOYOW',
            },
            'wsconf': {
                'conx-tpls': {
                    'default': {
                        'type': 'ws',
                        'baseurl': 'wss://real.okex.com:10441/websocket',
                    },
                },
                'methodmap': {
                    'addChannel': '_websocketOnAddChannel',
                    'removeChannel': '_websocketOnRemoveChannel',
                    '_websocketSendHeartbeat': '_websocketSendHeartbeat',
                },
                'events': {
                    'ob': {
                        'conx-tpl': 'default',
                        'conx-param': {
                            'url': '{baseurl}',
                            'id': '{id}',
                        },
                    },
                },
            },
        })

    def _websocket_on_open(self, contextId, params):
        # : heartbeat
        # self._websocketHeartbeatTicker and clearInterval(self._websocketHeartbeatTicker)
        # self._websocketHeartbeatTicker = setInterval(() => {
        #      self.websocketSendJson({
        #        'event': 'ping',
        #    })
        #  }, 30000)
        heartbeatTimer = self._contextGet(contextId, 'heartbeattimer')
        if heartbeatTimer is not None:
            self._cancelTimer(heartbeatTimer)
        heartbeatTimer = self._setTimer(contextId, 30000, self._websocketMethodMap('_websocketSendHeartbeat'), [contextId])
        self._contextSet(contextId, 'heartbeattimer', heartbeatTimer)

    def _websocket_send_heartbeat(self, contextId):
        self.websocketSendJson(
            {
                'event': 'ping',
            },
            contextId
        )

    def websocket_close(self, conxid='default'):
        super(okex, self).websocketClose(conxid)
        # stop heartbeat ticker
        # self._websocketHeartbeatTicker and clearInterval(self._websocketHeartbeatTicker)
        # self._websocketHeartbeatTicker = null
        heartbeatTimer = self._contextGet(conxid, 'heartbeattimer')
        if heartbeatTimer is not None:
            self._cancelTimer(heartbeatTimer)
        self._contextSet(conxid, 'heartbeattimer', None)

    def _websocket_on_add_channel(self):
        return None

    def _websocket_on_remove_channel(self):
        return None

    def _websocket_on_channel(self, contextId, channel, msg, data):
        # console.log('================',msg)
        if channel.find('ok_sub_spot_') >= 0:
            # spot
            depthIndex = channel.find('_depth')
            if depthIndex > 0:
                # orderbook
                result = self.safe_value(data, 'result', None)
                if result is not None and not result:
                    error = ExchangeError(self.safe_string(data, 'error_msg', 'orderbook error'))
                    self.emit('err', error)
                    return
                channelName = channel.replace('ok_sub_spot_', '')
                parts = channelName.split('_depth')
                pair = parts[0]
                symbol = self._get_symbol_by_pair(pair)
                timestamp = self.safe_value(data, 'timestamp')
                ob = self.parse_order_book(data, timestamp)
                symbolData = self._contextGetSymbolData(
                    contextId,
                    'ob',
                    symbol
                )
                symbolData['ob'] = ob
                self._contextSetSymbolData(contextId, 'ob', symbol, symbolData)
                self.emit(
                    'ob',
                    symbol,
                    self._cloneOrderBook(symbolData['ob'], symbolData['depth'])
                )
        elif channel.find('ok_sub_future') >= 0:
            # future
            depthIndex = channel.find('_depth')
            if depthIndex > 0:
                # orderbook
                pair = channel.substring(
                    len('ok_sub_future'),
                    depthIndex
                )
                symbol = self._get_symbol_by_pair(pair, True)
                timestamp = data.timestamp
                ob = self.parse_order_book(data, timestamp)
                symbolData = self._contextGetSymbolData(
                    contextId,
                    'ob',
                    symbol
                )
                symbolData['ob'] = ob
                self._contextSetSymbolData(contextId, 'ob', symbol, symbolData)
                self.emit(
                    'ob',
                    symbol,
                    self._cloneOrderBook(symbolData['ob'], symbolData['depth'])
                )

    def _websocket_dispatch(self, contextId, msg):
        # _websocketOnMsg [{"binary":0,"channel":"addChannel","data":{"result":true,"channel":"ok_sub_spot_btc_usdt_depth"}}] default
        # _websocketOnMsg [{"binary":0,"channel":"ok_sub_spot_btc_usdt_depth","data":{"asks":[[
        channel = self.safe_string(msg, 'channel')
        if not channel:
            # pong
            return
        resData = self.safe_value(msg, 'data', {})
        if channel in self.wsconf['methodmap']:
            method = self.wsconf['methodmap'][channel]
            getattr(self, method)(channel, msg, resData, contextId)
        else:
            self._websocket_on_channel(contextId, channel, msg, resData)

    def _websocket_on_message(self, contextId, data):
        # print('_websocketOnMsg', data)
        msgs = json.loads(data)
        if isinstance(msgs, list):
            for i in range(0, len(msgs)):
                self._websocket_dispatch(contextId, msgs[i])
        else:
            self._websocket_dispatch(contextId, msgs)

    def _websocket_subscribe(self, contextId, event, symbol, nonce, params={}):
        if event != 'ob':
            raise NotSupported('subscribe ' + event + '(' + symbol + ') not supported for exchange ' + self.id)
        data = self._contextGetSymbolData(contextId, event, symbol)
        data['depth'] = params['depth']
        data['limit'] = params['depth']
        self._contextSetSymbolData(contextId, event, symbol, data)
        sendJson = {
            'event': 'addChannel',
            'channel': self._get_order_book_channel_by_symbol(symbol, params),
        }
        self.websocketSendJson(sendJson)
        nonceStr = str(nonce)
        self.emit(nonceStr, True)

    def _websocket_unsubscribe(self, contextId, event, symbol, nonce, params={}):
        if event != 'ob':
            raise NotSupported('subscribe ' + event + '(' + symbol + ') not supported for exchange ' + self.id)
        sendJson = {
            'event': 'removeChannel',
            'channel': self._get_order_book_channel_by_symbol(symbol, params),
        }
        self.websocketSendJson(sendJson)
        nonceStr = str(nonce)
        self.emit(nonceStr, True)

    def _get_order_book_channel_by_symbol(self, symbol, params={}):
        pair = self._get_pair_by_symbol(symbol)
        # future example:ok_sub_futureusd_btc_depth_self_week_20
        # ok_sub_spot_usdt_btc_depth
        # spot ewxample:ok_sub_spot_btc_usdt_depth_5
        depthParam = self.safe_string(params, 'depth', '')
        # becareful of the underscore
        if depthParam:
            depthParam = '_' + depthParam
        channel = 'ok_sub_spot_' + pair + '_depth' + depthParam
        if self._isFutureSymbol(symbol):
            contract_type = params.contract_type
            if not contract_type:
                raise ExchangeError('parameter contract_type is required for the future.')
            channel = 'ok_sub_future' + pair + '_depth_' + contract_type + depthParam
        return channel

    def _get_pair_by_symbol(self, symbol):
        [currencyBase, currencyQuote] = symbol.split('/')
        currencyBase = currencyBase.lower()
        currencyQuote = currencyQuote.lower()
        pair = currencyBase + '_' + currencyQuote
        if self._isFutureSymbol(symbol):
            pair = currencyQuote + '_' + currencyBase
        return pair

    def _get_symbol_by_pair(self, pair, isFuture=False):
        [currency1, currency2] = pair.split('_')
        currency1 = currency1.upper()
        currency2 = currency2.upper()
        symbol = currency2 + '/' + currency1 if isFuture else currency1 + '/' + currency2
        return symbol

    def _get_current_websocket_orderbook(self, contextId, symbol, limit):
        data = self._contextGetSymbolData(contextId, 'ob', symbol)
        if 'ob' in data and data['ob'] is not None:
            return self._cloneOrderBook(data['ob'], limit)
        return None
