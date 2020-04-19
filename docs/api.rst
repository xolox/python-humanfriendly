API documentation
=================

The following API documentation was automatically generated from the source
code of `humanfriendly` |release|:

.. contents::
   :local:

A note about backwards compatibility
------------------------------------

The `humanfriendly` package started out as a single :mod:`humanfriendly`
module. Eventually this module grew to a size that necessitated splitting up
the code into multiple modules (see e.g. :mod:`~humanfriendly.tables`,
:mod:`~humanfriendly.terminal`, :mod:`~humanfriendly.text` and
:mod:`~humanfriendly.usage`). Most of the functionality that remains in the
:mod:`humanfriendly` module will eventually be moved to submodules as well (as
time permits and a logical subdivision of functionality presents itself to me).

While moving functionality around like this my goal is to always preserve
backwards compatibility. For example if a function is moved to a submodule an
import of that function is added in the main module so that backwards
compatibility with previously written import statements is preserved.

If backwards compatibility of documented functionality has to be broken then
the major version number will be bumped. So if you're using the `humanfriendly`
package in your project, make sure to at least pin the major version number in
order to avoid unexpected surprises.

:mod:`humanfriendly`
--------------------

.. automodule:: humanfriendly
   :members:

:mod:`humanfriendly.case`
------------------------

.. automodule:: humanfriendly.case
   :members:

:mod:`humanfriendly.cli`
------------------------

.. automodule:: humanfriendly.cli
   :members:

:mod:`humanfriendly.compat`
---------------------------

.. automodule:: humanfriendly.compat
   :members: coerce_string, is_string, is_unicode, on_windows

:mod:`humanfriendly.decorators`
-------------------------------

.. automodule:: humanfriendly.decorators
   :members:

:mod:`humanfriendly.deprecation`
--------------------------------

.. automodule:: humanfriendly.deprecation
   :members:

:mod:`humanfriendly.prompts`
----------------------------

.. automodule:: humanfriendly.prompts
   :members:

:mod:`humanfriendly.sphinx`
---------------------------

.. automodule:: humanfriendly.sphinx
   :members:

:mod:`humanfriendly.tables`
---------------------------

.. automodule:: humanfriendly.tables
   :members:

:mod:`humanfriendly.terminal`
-----------------------------

.. automodule:: humanfriendly.terminal
   :members:

:mod:`humanfriendly.terminal.html`
----------------------------------

.. automodule:: humanfriendly.terminal.html
   :members:

:mod:`humanfriendly.terminal.spinners`
--------------------------------------

.. automodule:: humanfriendly.terminal.spinners
   :members:

:mod:`humanfriendly.testing`
----------------------------

.. automodule:: humanfriendly.testing
   :members:

:mod:`humanfriendly.text`
-------------------------

.. automodule:: humanfriendly.text
   :members:

:mod:`humanfriendly.usage`
--------------------------

.. automodule:: humanfriendly.usage
   :members:
