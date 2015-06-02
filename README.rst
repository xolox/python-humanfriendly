humanfriendly: Human friendly input/output in Python
====================================================

.. image:: https://travis-ci.org/xolox/python-humanfriendly.svg?branch=master
   :target: https://travis-ci.org/xolox/python-humanfriendly

.. image:: https://coveralls.io/repos/xolox/python-humanfriendly/badge.png?branch=master
   :target: https://coveralls.io/r/xolox/python-humanfriendly?branch=master

The functions and classes in the `humanfriendly` package can be used to make
text interfaces more user friendly. Some example features:

- Parsing and formatting numbers, file sizes, pathnames and timespans in
  simple, human friendly formats.

- Easy to use timers for long running operations, with human friendly
  formatting of the resulting timespans.

- Prompting the user to select a choice from a list of options by typing the
  option's number or a unique substring of the option.

- Terminal interaction including text styling (ANSI escape sequences), user
  friendly rendering of usage messages and querying the terminal for its
  size.

The `humanfriendly` package is currently tested on Python 2.6, 2.7, 3.4 and
PyPy.

Getting started
---------------

It's very simple to start using the `humanfriendly` package::

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

The latest version of `humanfriendly` is available on PyPI_ and GitHub_. The
documentation is hosted on `Read the Docs`_. For bug reports please create an
issue on GitHub_. If you have questions, suggestions, etc. feel free to send me
an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2015 Peter Odding.

.. External references:
.. _GitHub: https://github.com/xolox/python-humanfriendly
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _peter@peterodding.com: peter@peterodding.com
.. _PyPI: https://pypi.python.org/pypi/humanfriendly
.. _Read the Docs: https://humanfriendly.readthedocs.org
