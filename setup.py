#!/usr/bin/env python
"""Setup/install script for kstock.

This file is part of: kstock
https://github.com/kpwf/kstock
"""
__author__ = 'Kevin (penniesfromkevin at gmail)'
__copyright__ = 'Copyright (c) 2014, Kevin'
__license__ = 'MIT license'

import os
from distutils.core import setup

from kstock import __version__


this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, 'README.rst')) as fhandle:
    LONG_DESCRIPTION = '\n%s' % fhandle.read()

setup(
    name='kstock',
    version=__version__,
    py_modules=['kstock'],
    author='Kevin',
    author_email='penniesfromkevin _at_ gmail.com',
    description='Get stock quote data from Google Finance and Yahoo Finance',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/kpwf/kstock',
    download_url='https://github.com/kpwf/kstock',
    keywords='stocks stockmarket market finance google yahoo quotes'.split(),
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Investment',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        ],
    )
