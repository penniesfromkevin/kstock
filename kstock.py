"""Retrieve stock quote data from Google Finance and Yahoo! Finance.

Tested on: Python 2.7
"""
__author__ = 'Kevin (penniesfromkevin at gmail)'
__copyright__ = 'Copyright (c) 2014, Kevin'
__version__ = '0.1.0'
__license__ = 'MIT license'

import csv
import json
import logging

try:
    # py3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
except ImportError:
    # py2
    from urllib2 import Request, urlopen, HTTPError

APIS = ('google', 'yahoo')
DEFAULT_API = APIS[0]

G_QUOTE_URL = 'http://finance.google.com/finance/info'
G_TAGS = {
    'change': 'c',  # '-7.86'
    'change_fix': 'c_fix',  # '-0.07'
    'ccol': 'ccol',  # 'chg' 'chr'
    'change_percent': 'cp',  # '-2.38'
    'change_percent_fix': 'cp_fix',  # '3.06'
    'dividend_per_share': 'div',  # '1.10'
    'stock_exchange': 'e',  # 'INDEXNASDAQ' 'NASDAQ' 'NYSE'
    'after_hours_change': 'ec',  # '+0.01'
    'after_hours_change_fix': 'ec_fix',  # '-0.77'
    'eccol': 'eccol',  # 'chb' 'chg' 'chr'
    'after_hours_change_percent': 'ecp',  # '-0.26'
    'after_hours_change_percent_fix': 'ecp_fix',  # '0.98'
    'after_hours_price': 'el',  # '96.84'
    'after_hours_price_cur': 'el_cur',  # '11.48'
    'after_hours_price_fix': 'el_fix',  # '96.84'
    'after_hours_trade_date': 'elt',  # 'Nov 21, 7:21PM EST'
    'id': 'id',  # '10792264'
    'last_trade_price': 'l',  # '96.81'
    'last_trade_price_fix': 'l_fix',  # '96.81'
    'last_trade_date': 'lt',  # 'Nov 21, 4:02PM EST'
    'last_trade_date_iso': 'lt_dts',  # '2014-11-21T17:15:59Z'
    'last_trade_time': 'ltt',  # '5:15PM EST'
    'pcls_fix': 'pcls_fix',  # '95.82'
    's': 's',  # '2'
    'company_name': 't',  # 'ZEN'
    'dividend_yield': 'yld',  # '2.85'
    }

Y_QUOTE_URL = 'http://finance.yahoo.com/d/quotes.csv'
Y_TAGS = {
    '1_year_target': 't8',
    '200_sma': 'm4',
    '50_sma': 'm3',
    '52_week_high': 'k',
    '52_week_low': 'j',
    '52_week_range': 'w',
    'after_hours_change': 'c8',
    'annualized_gain': 'g3',
    'ask_realtime': 'b2',
    'ask_size': 'a5',
    'average_daily_volume': 'a2',
    'bid_realtime': 'b3',
    'bid_size': 'b6',
    'book_value': 'b4',
    'change': 'c1',
    'change_200_sma': 'm5',
    'change_50_sma': 'm7',
    'change_from_52_week_high': 'k4',
    'change_from_52_week_low': 'j5',
    'change_percent': 'p2',
    'change_percent_change': 'c',
    'change_percent_realtime': 'k2',
    'change_realtime': 'c6',
    'commission': 'c3',
    'company_name': 'n',
    'dividend_pay_date': 'r1',
    'dividend_per_share': 'd',
    'dividend_yield': 'y',
    'ebitda': 'j4',
    'eps': 'e',
    'eps_estimate_current_year': 'e7',
    'eps_estimate_next_quarter': 'e9',
    'eps_estimate_next_year': 'e8',
    'ex_dividend_date': 'q',
    'float_shares': 'f6',
    'high_limit': 'l2',
    'holdings_gain': 'g4',
    'holdings_gain_percent': 'g1',
    'holdings_gain_percent_realtime': 'g5',
    'holdings_gain_realtime': 'g6',
    'holdings_value': 'v1',
    'holdings_value_realtime': 'v7',
    'last_trade_date': 'd1',
    'last_trade_price': 'l1',
    'last_trade_realtime_time': 'k1',
    'last_trade_size': 'k3',
    'last_trade_time': 't1',
    'last_trade_time_plus': 'l',
    'low_limit': 'l3',
    'market_cap': 'j1',
    'market_cap_realtime': 'j3',
    'more_info': 'v',
    'notes': 'n4',
    'order_book_realtime': 'i5',
    'pe': 'r',
    'pe_realtime': 'r2',
    'peg': 'r5',
    'percent_change_200_sma': 'm6',
    'percent_change_50_sma': 'm8',
    'percent_change_from_52_week_high': 'k5',
    'percent_change_from_52_week_low': 'j6',
    'previous_close': 'p',
    'price_book': 'p6',
    'price_eps_estimate_current_year': 'r6',
    'price_eps_estimate_next_year': 'r7',
    'price_paid': 'p1',
    'price_sales': 'p5',
    'revenue': 's6',
    'shares_outstanding': 'j2',
    'shares_owned': 's1',
    'short_ratio': 's7',
    'stock_exchange': 'x',
    'ticker_trend': 't7',
    'today_open': 'o',
    'todays_high': 'h',
    'todays_low': 'g',
    'todays_range': 'm',
    'todays_range_realtime': 'm2',
    'todays_value_change': 'w1',
    'todays_value_change_realtime': 'w4',
    'trade_date': 'd2',
    'trade_links': 't6',
    'volume': 'v',
    }

LOGGER = logging.getLogger()


def _request(url):
    """Makes the URL info request.

    Args:
        url: URL that returns data.

    Returns:
        Response string.
    """
    LOGGER.debug('_request URL: %s', url)
    try:
        request = Request(url)
        response = urlopen(request)
        content = response.read().decode().strip()
    except HTTPError as err:
        LOGGER.error('_request: HTTPError')
        content = ''
    LOGGER.debug('_request content: %s', content)
    return content


def _request_y_symbols(symbols, tag_string):
    """Makes the Yahoo! Finance info request.

    Args:
        symbols: Stock symbol or, confusingly, list of stock symbols.
        tag_string: Tag or, confusingly, tag combination.
            Examples:
                'p1'   # single tag
                'np1v' # tag combination

    Returns:
        Dictionary with symbols as keys and list of tag values as
        values.
        {
            symbol1: [value1, .., valueN],
            ..
            symbolM: [value1, .., valueN],
            }
    """
    if isinstance(symbols, str):
        symbols = [symbols]
    symbols = conform_symbols(symbols, 'yahoo')
    symbol_string = '+'.join(symbols)
    url = '%s?s=%s&f=%s' % (Y_QUOTE_URL, symbol_string, tag_string)
    content = _request(url)
    csv_reader = csv.reader(content.splitlines(), delimiter=',')
    content = [row for row in csv_reader]
    return_dict = {}
    if content:
        for index, symbol in enumerate(symbols):
            return_dict[symbol] = content[index]
    return return_dict


def _y_get_all(symbols):
    """Get all Yahoo! quote data for the given ticker symbols.

    Args:
        symbols: Stock symbol or, confusingly, list of stock symbols.

    Returns:
        Dictionary of symbols with dictionary of tag values requested.
        See _y_get_tags().
    """
    tags = Y_TAGS.keys()
    symbol_data = _y_get_tags(symbols, tags)
    return symbol_data


def _y_get_tag(symbols, tag_string):
    """Get Yahoo! tag values for multiple symbols.

    Args:
        symbols: Stock symbol or, confusingly, list of stock symbols.
        tag_string: Tag name, tag, or, confusingly, tag combination.
        Examples:
            'trade_date' # tag name
            'd2'         # tag
            'nd1d2'      # tag combination

    Returns:
        Dictionary of symbols with list of tag values requested.
        {
            symbol1: [value1, .., valueN],
            ..
            symbolN: [value1, .., valueN],
            }
    """
    if tag_string in Y_TAGS:
        tag_string = Y_TAGS[tag_string]
    return_dict = _request_y_symbols(symbols, tag_string)
    return return_dict


def _y_get_tags(symbols, tags):
    """Get multiple Yahoo! tag values for multiple symbols.

    This is similar to _y_get_tag(), but a little more versatile with
    cleaner output (dictionary).

    Args:
        symbols: Stock symbol or, confusingly, list of stock symbols.
        tags: Tag name, tag, or, confusingly, list of tag names or tags.
            NOTE: Tag combination strings are no longer allowed.
        Examples:
            'trade_date' # tag name
            'd2'         # tag
            ['trade_date', 'd2'] # list of tag names and/or tags

    Returns:
        Dictionary of symbols with dictionary of tag values requested.
        {
            symbol1: {
                key1: value1,
                ..
                keyN: valueN,
                },
            ..
            symbolM: {
                key1: value1,
                ..
                keyN: valueN,
                },
            }
    """
    if isinstance(symbols, str):
        symbols = [symbols]
    if isinstance(tags, str):
        tags = [tags]
    tag_parts = []
    tag_names = []
    for tag in tags:
        if tag in Y_TAGS:
            # tag is actually a tag name; get the tag from value
            tag_names.append(tag)
            tag_parts.append(Y_TAGS[tag])
        elif tag in Y_TAGS.values():
            # tag is really a tag; get the name from key
            for tag_name, tag_abbr in Y_TAGS.items():
                if tag == tag_abbr:
                    tag_names.append(tag_name)
                    tag_parts.append(tag_abbr)
                    break
        else:
            # Unknown tag; pass tag with "unknown" as name
            tag_names.append('unknown')
            tag_parts.append(tag)
    tag_string = ''.join(tag_parts)
    symbol_data = _request_y_symbols(symbols, tag_string)
    symbol_dict = {}
    for symbol in symbols:
        symbol_new = symbol.strip('^.')
        symbol_dict[symbol_new] = {}
        for tag_index, tag_name in enumerate(tag_names):
            symbol_dict[symbol_new][tag_name] = symbol_data[symbol][tag_index]
    return symbol_dict


def _g_get_all(symbols):
    """Get all Google quote data for the given ticker symbols.

    Args:
        symbols: Stock symbol or, confusingly, list of stock symbols.

    Returns:
        Dictionary of symbols with dictionary of tag values requested.
    """
    if isinstance(symbols, str):
        symbols = [symbols]
    symbols = conform_symbols(symbols, 'google')
    symbol_string = ','.join(symbols)
    url = '%s?client=ig&q=%s' % (G_QUOTE_URL, symbol_string)
    content = _request(url)
    if content.startswith('//'):
        content = content[2:].strip()
    content = json.loads(content)

    # Reverse the dictionary
    g_tag_fixed = {}
    for tag_name, tag_value in G_TAGS.items():
        g_tag_fixed[tag_value] = tag_name

    symbol_dict = {}
    for symbol_data in content:
        symbol = symbol_data['t'].strip('^.')
        symbol_dict[symbol] = {}
        for tag_name, tag_value in symbol_data.items():
            if tag_name in g_tag_fixed:
                symbol_dict[symbol][g_tag_fixed[tag_name]] = tag_value
    LOGGER.debug('_g_get_all: %s', repr(symbol_dict))
    return symbol_dict


def conform_symbols(symbols, fapi=DEFAULT_API):
    """Conform symbol names to the fapi ('google' or 'yahoo').

    Args:
        symbols: List of ticker symbols.
        fapi: Financial data API; currently 'google' or 'yahoo'.

    Returns:
        List of symbols conformed to the fapi.
    """
    fapi = fapi.lower()[0]
    final_symbols = []
    for symbol in symbols:
        parts = symbol.split(':')
        if len(parts) > 1:
            exchange = parts[0]
            symbol = parts[1]
        else:
            exchange = ''
            symbol = parts[0]
        if fapi == 'g':
            symbol = symbol.replace('^', '.')
            if exchange:
                symbol = '%s:%s' % (exchange, symbol)
        else:
            symbol = symbol.replace('.', '^')
        symbol = symbol.upper()
        final_symbols.append(symbol)
    return final_symbols


def get_all(symbols, fapi=DEFAULT_API):
    """Get all available quote data for the given ticker symbols.

    Args:
        symbols: Stock symbol or, confusingly, list of stock symbols.
        fapi: Financial data API; currently 'google' or 'yahoo'.

    Returns:
        Dictionary of symbols with dictionary of tag values requested.
    """
    fapi = fapi.lower()[0]
    if fapi == 'g':
        symbol_dict = _g_get_all(symbols)
    else:
        symbol_dict = _y_get_all(symbols)
    return symbol_dict


def parse_symbol_file(filepath, fapi=None):
    """Read in stock symbol list from a text file.

    Args:
        filepath: Path to file containing stock symbols, one per line.
        fapi: If this is supplied, the symbols read will be conformed
            to a financial API; currently 'google' or 'yahoo'.

    Returns:
        List of stock symbols; list may be empty if file could not be
        parsed.
    """
    try:
        with open(filepath, 'r') as file_handle:
            symbols = [line.strip() for line in list(file_handle)
                       if '#' not in line]
        if fapi:
            symbols = conform_symbols(symbols, fapi)
    except IOError:
        symbols = []
    return symbols
