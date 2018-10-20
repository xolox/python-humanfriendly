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

The :mod:`humanfriendly` module
-------------------------------

.. automodule:: humanfriendly
   :members:

The :mod:`humanfriendly.cli` module
-----------------------------------

.. automodule:: humanfriendly.cli
   :members:

The :mod:`humanfriendly.compat` module
--------------------------------------

.. automodule:: humanfriendly.compat
   :members:

The :mod:`humanfriendly.decorators` module
------------------------------------------

.. automodule:: humanfriendly.decorators
   :members:

The :mod:`humanfriendly.prompts` module
---------------------------------------

.. automodule:: humanfriendly.prompts
   :members:

The :mod:`humanfriendly.sphinx` module
--------------------------------------

.. automodule:: humanfriendly.sphinx
   :members:

The :mod:`humanfriendly.tables` module
--------------------------------------

.. automodule:: humanfriendly.tables
   :members:

The :mod:`humanfriendly.terminal` module
----------------------------------------

.. automodule:: humanfriendly.terminal
   :members:

The :mod:`humanfriendly.testing` module
---------------------------------------

.. automodule:: humanfriendly.testing
   :members:

The :mod:`humanfriendly.text` module
------------------------------------

.. automodule:: humanfriendly.text
   :members:

The :mod:`humanfriendly.usage` module
-------------------------------------

.. automodule:: humanfriendly.usage
   :members:
