#!/usr/bin/env python
"""Sample test point creator.
"""
__author__ = 'Kevin (penniesfromkevin at gmail)'
__copyright__ = 'Copyright (c) 2014, Kevin.'
__version__ = '0.1.1'

import logging
import socket
import sys
import time

from argparse import ArgumentParser

import kstock


DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 2878
DEFAULT_DELAY = 10 #seconds
DEFAULT_COUNT = -1
DEFAULT_ERRORS = 10

LOG_LEVELS = ('CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG')
DEFAULT_LOG_LEVEL = LOG_LEVELS[3]
LOGGER = logging.getLogger()


def parse_args():
    """Parse user arguments and return as parser object.

    Returns:
        Parser object with arguments as attributes.
    """
    parser = ArgumentParser(description='Create kstock test points.')
    parser.add_argument('-a', '--api', default=kstock.DEFAULT_API,
            choices=kstock.APIS, help='Financial Data API to query.')

    parser.add_argument('-f', '--filepath',
            help='Optional path to file containing stock ticker symbols.')
    parser.add_argument('-t', '--tickers',
            help='Comma-separated string of stock ticker symbols.')

    parser.add_argument('-d', '--delay', default=DEFAULT_DELAY, type=int,
            help='Delay between queries, in seconds.')
    parser.add_argument('-e', '--error_max', default=DEFAULT_ERRORS, type=int,
            help='Maximum number of socket errors allowed before quitting.')
    parser.add_argument('-c', '--count', default=DEFAULT_COUNT, type=int,
            help='Number of iterations; negative for infinite.')

    parser.add_argument('-x', '--transmit', action='store_true',
            help='Send points to host for real.')
    parser.add_argument('-s', '--host', default=DEFAULT_HOST,
            help='Host IP of machine running agent.')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int,
            help='Host port receiving data.')

    parser.add_argument('-L', '--loglevel', choices=LOG_LEVELS,
            default=DEFAULT_LOG_LEVEL, help='Set the logging level.')
    args = parser.parse_args()
    return args


def transmit_line(host, port, line):
    """Transmit data line to metrics agent.

    Args:
        host: Host IP.
        port: Host port.
        line: Metric line to send, in Graphite format.
    """
    sock = socket.socket()
    sock.connect((host, port))
    sock.sendall('%s\n' % line)
    sock.close()


def main():
    """Main script.
    """
    if ARGS.tickers:
        symbols = ARGS.tickers.split(',')
    else:
        symbols = []
    if ARGS.filepath:
        symbols += kstock.parse_symbol_file(ARGS.filepath)
    if not symbols:
        LOGGER.error('No ticker symbols specified.')
        errors = ARGS.error_max
    else:
        symbols = kstock.conform_symbols(symbols, ARGS.api)
        errors = 0
    count = ARGS.count
    while count != 0 and errors < ARGS.error_max:
        quotes = kstock.get_all(symbols, ARGS.api)
        if quotes:
            for symbol in quotes:
                LOGGER.debug(quotes[symbol])
                for param in ('last_trade_price', 'after_hours_price'):
                    if param in quotes[symbol]:
                        price = quotes[symbol][param].strip()
                        symbol = symbol.strip('^.')
                        line = "stock.%s %s host='%s'" % (param, price, symbol)
                        LOGGER.info(line)
                        if ARGS.transmit:
                            transmit_line(ARGS.host, ARGS.port, line)
            if count > 0:
                count -= 1
            LOGGER.info('---- %d left to go ----', count)
        else:
            errors += 1
            LOGGER.error('---- Errors: %d (%d) ----', errors, ARGS.error_max)

        if errors >= ARGS.error_max:
            LOGGER.info('Exiting due to maximum errors.')
        else:
            time.sleep(ARGS.delay)

    return errors


if __name__ == '__main__':
    ARGS = parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=getattr(logging, ARGS.loglevel))
    sys.exit(main())
