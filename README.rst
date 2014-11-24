kstock
======

**Python module - Retrieve stock data from Google Finance and Yahoo Finance**

This started as a modification of ystockquote by Corey Goldberg, but
became a full re-write.  Test methodology has been retained for now,
but that will also change in the future.

 * Created by: Kevin (2014)
 * License: MIT
 * Dev Home: `https://github.com/kpwf/kstock <https://github.com/kpwf/kstock>`_

----

~~~~~~~~~~~~
Requirements
~~~~~~~~~~~~

  * Python 2.7
  * May work on Python 3.3 (not tested)

~~~~~~~
Install
~~~~~~~

Clone the development repo (requires `git <http://git-scm.com/>`_) to install::

    $ git clone git://github.com/kpwf/kstock.git
    $ cd kstock
    $ python setup.py install

To run unit tests::

    $ python -m unittest discover

~~~~~~~~~~~~~
Example Usage
~~~~~~~~~~~~~

.. code:: python

    >>> import kstock
    >>> print(kstock.get_all('GOOG', 'google'))
    >>> print(kstock.get_all('GOOG', 'yahoo'))
    >>>

.. code:: bash

    $ ./sample_point_creator.py -f ticker_symbols.txt
    $
