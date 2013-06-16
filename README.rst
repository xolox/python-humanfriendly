humanfriendly: Human friendly input/output in Python
====================================================

The functions in the ``humanfriendly`` module can be used to make text
interfaces more user friendly by parsing and formatting file sizes and
timestamps in a simple, human readable format.

Usage
-----

It's very simple to start using the ``humanfriendly`` module::

   import humanfriendly
   num_bytes = humanfriendly.parse_size(raw_input("Enter a readable file size: "))
   print "You entered:", humanfriendly.format_size(num_bytes)

Contact
-------

The latest version of ``humanfriendly`` is available on PyPi_ and GitHub_. For
bug reports please create an issue on GitHub_. If you have questions,
suggestions, etc. feel free to send me an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2013 Peter Odding.

.. External references:
.. _GitHub: https://github.com/xolox/python-humanfriendly
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _peter@peterodding.com: peter@peterodding.com
.. _PyPi: https://pypi.python.org/pypi/humanfriendly
