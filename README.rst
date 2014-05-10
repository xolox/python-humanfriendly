humanfriendly: Human friendly input/output in Python
====================================================

.. image:: https://travis-ci.org/xolox/python-humanfriendly.svg?branch=master
   :target: https://travis-ci.org/xolox/python-humanfriendly

.. image:: https://coveralls.io/repos/xolox/python-humanfriendly/badge.png?branch=master
   :target: https://coveralls.io/r/xolox/python-humanfriendly?branch=master

The functions in the ``humanfriendly`` package can be used to make text
interfaces more user friendly by parsing and formatting file sizes and
timestamps in simple, human readable formats. It's currently tested on Python
2.6, 2.7 and 3.4.

Getting started
---------------

It's very simple to start using the ``humanfriendly`` package::

   >>> import humanfriendly
   >>> user_input = raw_input("Enter a readable file size: ")
   Enter a readable file size: 16G
   >>> num_bytes = humanfriendly.parse_size(user_input)
   >>> print num_bytes
   17179869184
   >>> print "You entered:", humanfriendly.format_size(num_bytes)
   You entered: 16 GB

Contact
-------

The latest version of ``humanfriendly`` is available on PyPI_ and GitHub_. The
documentation is hosted on `Read the Docs`_. For bug reports please create an
issue on GitHub_. If you have questions, suggestions, etc. feel free to send me
an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2013 Peter Odding.

.. External references:
.. _GitHub: https://github.com/xolox/python-humanfriendly
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _peter@peterodding.com: peter@peterodding.com
.. _PyPI: https://pypi.python.org/pypi/humanfriendly
.. _Read the Docs: https://humanfriendly.readthedocs.org
