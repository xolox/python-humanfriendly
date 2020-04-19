Changelog
=========

The purpose of this document is to list all of the notable changes to this
project. The format was inspired by (but doesn't strictly adhere to) `Keep a
Changelog`_. This project adheres to `semantic versioning`_.

.. contents::
   :local:

.. _Keep a Changelog: http://keepachangelog.com/
.. _semantic versioning: http://semver.org/

`Release 8.2`_ (2020-04-19)
---------------------------

Added a simple case insensitive dictionary implementation, for details refer to
the new :mod:`humanfriendly.case` module.

.. _Release 8.2: https://github.com/xolox/python-humanfriendly/compare/8.1...8.2

`Release 8.1`_ (2020-03-06)
---------------------------

**Enhancements:**

- Make it possible to opt out of the output capturing that
  :func:`humanfriendly.testing.run_cli()` sets up by default.

- Improve feature parity between :class:`humanfriendly.testing.CaptureOutput`
  and my :pypi:`capturer` package to the point where most of the
  :pypi:`humanfriendly` test suite can now run without :pypi:`capturer`.

**Internal changes:**

- Refactored the test suite to import all names separately instead of referring
  to identifiers via their modules (my preferences have changed since this code
  was written a long time ago).

.. _Release 8.1: https://github.com/xolox/python-humanfriendly/compare/8.0...8.1

`Release 8.0`_ (2020-03-02)
---------------------------

This release is backwards incompatible in several ways, see the notes below.

**Enhancements:**

- Adopt :func:`functools.wraps()` to make decorator functions more robust.

- Make the :class:`~humanfriendly.terminal.spinners.Spinner` class more
  customizable. The interval at which spinners are updated and the characters
  used to draw the animation of spinners can now be customized by callers.
  This was triggered by `executor issue #2`_.

  .. note:: The text cursor hiding behavior of spinners has been removed
            because it was found to be problematic (sometimes the text cursor
            would be hidden but not made visible again, which is disorienting
            to say the least).

- Improve test skipping based on exception types.

  The :class:`humanfriendly.testing.TestCase` class was originally created to
  enable skipping of tests that raise specific exception types on Python 2.6.
  This involved patching test methods, which had the unfortunate side effect
  of generating confusing :pypi:`pytest` output on test failures.

  Since then :pypi:`unittest2` was integrated which provided real
  skipping of tests however removing the old test skipping support
  from the :mod:`humanfriendly.testing` module would have resulted
  in a backwards incompatible change, so I never bothered. I've now
  decided to bite the bullet and get this over with:

  1. I've implemented an alternative (finer grained) strategy based on a
     decorator function that applies to individual test methods, for
     details see :func:`humanfriendly.testing.skip_on_raise()`.

  2. I've removed the test method wrapping from the
     :class:`humanfriendly.testing.TestCase` class.

  .. note:: This change is backwards incompatible, in fact it breaks the
            test suites of two other projects of mine (:pypi:`executor` and
            :pypi:`vcs-repo-mgr`) because they depend on the old test method
            wrapping approach. Both test suites will need to be migrated to
            the :func:`~humanfriendly.testing.skip_on_raise()` decorator.

**Internal changes:**

- The "deprecated imports" feature provided by :mod:`humanfriendly.deprecation`
  has been adopted to clean up the maze of (almost but not quite) cyclic import
  dependencies between modules.

- HTML to ANSI functionality has been extracted to a new
  :mod:`humanfriendly.terminal.html` module.

- Support for spinners has been extracted to a new
  :mod:`humanfriendly.terminal.spinners` module.

- The use of positional arguments to initialize
  :class:`~humanfriendly.terminal.spinners.Spinner` objects has been deprecated
  using the new :func:`humanfriendly.deprecation.deprecated_args()` decorator
  function.

.. _Release 8.0: https://github.com/xolox/python-humanfriendly/compare/7.3...8.0
.. _executor issue #2: https://github.com/xolox/python-executor/issues/2

`Release 7.3`_ (2020-03-02)
---------------------------

**Enhancements:**

Added the :func:`humanfriendly.deprecation.deprecated_args()` decorator function
which makes it easy to switch from positional arguments to keyword arguments
without dropping backwards compatibility.

.. note:: I'm still working on the humanfriendly 8.0 release which was going to
          break backwards compatibility in several ways if it wasn't for the
          tools provided by the new :mod:`humanfriendly.deprecation` module.

.. _Release 7.3: https://github.com/xolox/python-humanfriendly/compare/7.2...7.3

`Release 7.2`_ (2020-03-01)
---------------------------

**Enhancements:**

Support for backwards compatible aliases that emit deprecation warnings
(:mod:`humanfriendly.deprecation`).

.. note:: I'm currently working on several large refactorings that involve
          moving things around between modules and dreaded having to extend the
          existing maze of (almost but not quite) cyclic import dependencies
          between modules. This new functionality will be adopted to untangle
          the existing maze in the upcoming humanfriendly 8.0 release, which
          bumps the major version number due to this very large change in how
          backwards compatibility is implemented. It is my hope that this new
          functionality will prove to be robust enough to unburden me from the
          less elegant aspects of preserving backwards compatibility 😁.

**Documentation:**

Get rid of broken references and noise in the online documentation once and for all:

- :pypi:`Sphinx` was emitting a screen full of warnings about unknown
  references. These were bothering me because testing the integration between
  Sphinx and :mod:`humanfriendly.deprecation` involved lots of broken
  references as well.

- Additionally the :mod:`humanfriendly.compat` module introduced a lot of noise
  into the generated documentation because imported classes and their members
  were being included in the documentation, this is now also fixed.

- Finally I decided to start using ``sphinx-build -nW`` to complain loudly when
  even just one broken reference is found. This should encourage the discipline
  to never introduce broken references again!

**Tests:**

Fixed :mod:`unittest` deprecation warnings in the test suite.

.. _Release 7.2: https://github.com/xolox/python-humanfriendly/compare/7.1.1...7.2

`Release 7.1.1`_ (2020-02-18)
-----------------------------

Fix Python 3 incompatibility (``distutils.spawn``).

Much to my dismay this morning I ran into the following traceback on a Python
3.6 installation that is based on native Ubuntu (Debian) packages::

  Traceback (most recent call last):
    File "...", line 1, in <module>
      from coloredlogs.syslog import enable_system_logging
    File ".../coloredlogs/__init__.py", line 138, in <module>
      from humanfriendly import coerce_boolean
    File ".../humanfriendly/__init__.py", line 25, in <module>
      from humanfriendly.tables import format_pretty_table as format_table
    File ".../humanfriendly/tables.py", line 32, in <module>
      from humanfriendly.terminal import (
    File ".../humanfriendly/terminal.py", line 26, in <module>
      import distutils.spawn
  ModuleNotFoundError: No module named 'distutils.spawn'

To enable local development and testing against lots of Python releases I use
deadsnakes_ to install Python 2.7, 3.4, 3.5, 3.6, 3.7 and 3.8 at the same time.
Before committing 335a69bae5_ I did check the availability of the
``distutils.spawn`` module against my locally installed interpreters:

.. code-block:: console

   $ ls -l /usr/lib/python*/distutils/spawn.py
   -rw-r--r-- 1 root root 8.5K Nov  7 11:07 /usr/lib/python2.7/distutils/spawn.py
   -rw-r--r-- 1 root root 7.4K Mar 29  2019 /usr/lib/python3.4/distutils/spawn.py
   -rw-r--r-- 1 root root 7.3K Nov 24 02:35 /usr/lib/python3.5/distutils/spawn.py
   -rw-r--r-- 1 root root 7.3K Oct 28 17:30 /usr/lib/python3.6/distutils/spawn.py
   -rw-r--r-- 1 root root 7.7K Oct 28 17:30 /usr/lib/python3.7/distutils/spawn.py
   -rw-r--r-- 1 root root 7.7K Oct 28 17:30 /usr/lib/python3.8/distutils/spawn.py

I took this to mean it would be available on all these versions. Furthermore
the tests on Travis CI passed as well. I think this is because deadsnakes_ as
well as Travis CI are closer to upstream (the official Python releases) whereas
Debian and Ubuntu make significant customizations...

In any case this new commit should fix the issue by using
:func:`shutil.which()` on Python 3 instead.

.. _Release 7.1.1: https://github.com/xolox/python-humanfriendly/compare/7.1...7.1.1
.. _deadsnakes: https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa
.. _335a69bae5: https://github.com/xolox/python-humanfriendly/commit/335a69bae5

`Release 7.1`_ (2020-02-16)
---------------------------

**Enhancements:**

- Enable Windows native support for ANSI escape sequences. This was brought to
  my attention in `coloredlogs issue #71`_ and `coloredlogs pull request #72`_.
  My experiences with ANSI escape sequences started out as part of the
  :pypi:`coloredlogs` package but eventually I moved the support for ANSI
  escape sequences to the :pypi:`humanfriendly` package. This explains how it
  now makes sense to integrate the Windows native ANSI escape sequence support
  in :pypi:`humanfriendly` as well.

**Bug fixes:**

- Accept pluralized disk size units (`#26`_). I'm not claiming this is a full
  solution to the problem, far from it. It does lessen the pain a bit (IMHO).

- Make sure the selected pager is available before trying to run it. While
  testing :pypi:`humanfriendly` on Windows 10 I noticed that ``humanfriendly
  --help`` resulted in nothing but a traceback, because :man:`less` wasn't
  available. That's not human friendly at all 😕 (even if it is Windows 😈).

.. _Release 7.1: https://github.com/xolox/python-humanfriendly/compare/7.0...7.1
.. _coloredlogs issue #71: https://github.com/xolox/python-coloredlogs/issues/71
.. _coloredlogs pull request #72: https://github.com/xolox/python-coloredlogs/pull/72
.. _#26: https://github.com/xolox/python-humanfriendly/issues/26

`Release 7.0`_ (2020-02-16)
---------------------------

After an unplanned but extended hiatus from the development and maintenance of
my open source projects I'm now finally starting to pick up some momentum, so
I'm trying to make the best of it:

- Merge pull request `#24`_: Fix bug in :func:`~humanfriendly.parse_length()` that rounded floats.
- Merge pull request `#32`_: Update hyperlinks in readme.
- Merge pull request `#33`_: Drop support for Python 2.6 and 3.0-3.4
- Merge pull request `#35`_: SVG badge in readme.
- Merge pull request `#36`_: Add support for nanoseconds and microseconds time units
- Fixed :func:`~humanfriendly.tables.format_rst_table()` omission from
  ``humanfriendly.tables.__all__``.
- Start testing on Python 3.8 and 3.9-dev.

.. _Release 7.0: https://github.com/xolox/python-humanfriendly/compare/6.1...7.0
.. _#24: https://github.com/xolox/python-humanfriendly/pull/24
.. _#32: https://github.com/xolox/python-humanfriendly/pull/32
.. _#33: https://github.com/xolox/python-humanfriendly/pull/33
.. _#35: https://github.com/xolox/python-humanfriendly/pull/35
.. _#36: https://github.com/xolox/python-humanfriendly/pull/36

`Release 6.1`_ (2020-02-10)
---------------------------

- Added a ``:pypy:`…``` role for easy linking to packages on the Python Package
  Index, for details refer to :func:`humanfriendly.sphinx.pypi_role()`.

- Wasted quite a bit of time debugging a MacOS failure on Travis CI caused by a
  broken :man:`pip` installation, fixed by using ``get-pip.py`` to bootstrap an
  installation that actually works 😉.

.. _Release 6.1: https://github.com/xolox/python-humanfriendly/compare/6.0...6.1

`Release 6.0`_ (2020-02-09)
---------------------------

**Noteworthy changes:**

- Enable :class:`~humanfriendly.testing.MockedProgram` to customize the shell
  script code of mocked programs. This was added to make it easy to mock a
  program that is expected to generate specific output (I'm planning to use
  this in the :pypi:`linux-utils` test suite).

- Defined ``__all__`` for all public modules that previously lacked "export
  control" and decided to bump the major version number as a precaution:

  - These changes should not have any impact on backwards compatibility,
    unless I forgot entries, in which case callers can get
    :exc:`~exceptions.ImportError` exceptions...

  - Imports of public modules were previously exported (implicitly) and this
    pollutes code completion suggestions which in turn can encourage bad
    practices (not importing things using their "canonical" name).

  - I started developing the ``humanfriendly`` package years before I learned
    about the value of defining ``__all__`` and so some modules lacked a
    definition until now. I decided that now was as good a time as any
    to add those definitions 😇.

**Miscellaneous changes:**

- Simplified the headings in ``docs/api.rst`` so that only the module names
  remain. This was done because Sphinx doesn't support nested links in HTML
  output and thus generated really weird "Table of Contents" listings.

- Fixed the reStructuredText references in the documentation of
  :func:`~humanfriendly.prompts.prompt_for_choice()`. This function is imported
  from :mod:`humanfriendly.prompts` to :mod:`humanfriendly` (for backwards
  compatibility) where it can't use relative references to refer to the other
  functions in the :mod:`humanfriendly.prompts` module.

- Changed the ``Makefile`` to default to Python 3 for development, make sure
  ``flake8`` is always up-to-date and silence the few targets whose commands
  were not already silenced.

- Embedded quite a few Python API references into recent changelog entries,
  just because I could (I ❤️  what hyperlinks can do for the usability of
  technical documentation, it gives a lot more context).

.. _Release 6.0: https://github.com/xolox/python-humanfriendly/compare/5.0...6.0

`Release 5.0`_ (2020-02-06)
---------------------------

- Added custom ``:man:`…``` role for easy linking to Linux manual pages to
  the :mod:`humanfriendly.sphinx` module.

- Changed rendering of pretty tables to expand tab characters to spaces:

  Until now pretty tables did not take the variable width of tab characters
  into account which resulted in tables whose "line drawing characters" were
  visually misaligned. Tabs are now expanded to spaces using
  ``str.expandtabs()``.

- Stop testing on Python 2.6 and drop official support. The world (including
  Travis CI) has moved on and preserving Python 2.6 compatibility was clearly
  starting to drag the project down...

I decided to bump the major version number because each of these changes can be
considered backwards incompatible in one way or another and version numbers are
cheap anyway so there 😛.

.. _Release 5.0: https://github.com/xolox/python-humanfriendly/compare/4.18...5.0

`Release 4.18`_ (2019-02-21)
----------------------------

- Added :func:`humanfriendly.text.generate_slug()` function.

- Fixed "invalid escape sequence" DeprecationWarning (pointed out by Python >= 3.6).

- Fought Travis CI (for way too long) in order to restore Python 2.6, 2.7, 3.4,
  3.5, 3.6 and 3.7 compatibility in the Travis CI configuration (unrelated to
  the ``humanfriendly`` package itself).

.. _Release 4.18: https://github.com/xolox/python-humanfriendly/compare/4.17...4.18

`Release 4.17`_ (2018-10-20)
----------------------------

- Add Python 3.7 to versions tested on Travis CI and using ``tox`` and document
  compatibility with Python 3.7.

- Add rudimentary caching decorator for functions:

  Over the years I've used several variations on this function in multiple
  projects and I'd like to consolidate all of those implementations into a
  single one that's properly tested and documented.

  Due to the simplicity and lack of external dependencies it seemed kind of
  fitting to include this in the ``humanfriendly`` package, which has become
  a form of extended standard library for my Python projects 😇.

.. _Release 4.17: https://github.com/xolox/python-humanfriendly/compare/4.16.1...4.17

`Release 4.16.1`_ (2018-07-21)
------------------------------

Yet another ANSI to HTML improvement: Emit an ANSI reset code before emitting
ANSI escape sequences that change styles, so that previously activated styles
don't inappropriately "leak through" to the text that follows.

.. _Release 4.16.1: https://github.com/xolox/python-humanfriendly/compare/4.16...4.16.1

`Release 4.16`_ (2018-07-21)
----------------------------

More HTML to ANSI improvements:

- Added :func:`humanfriendly.text.compact_empty_lines()` function.
- Enable optional ``callback`` argument to
  :func:`humanfriendly.terminal.html_to_ansi()`.
- Added a code sample and screenshot to the
  :class:`humanfriendly.terminal.HTMLConverter` documentation.
- Emit vertical whitespace for block tags like ``<div>``, ``<p>`` and ``<pre>``
  and post-process the generated output in ``__call__()`` to compact empty lines.
- Don't pre-process preformatted text using the user defined text callback.
- Improve robustness against malformed HTML (previously an ``IndexError`` would
  be raised when a closing ``</a>`` tag was encountered without a corresponding
  opening ``<a>`` tag).
- Emit an ANSI reset code when :func:`humanfriendly.terminal.html.HTMLConverter.close()`
  is called and a style is still active (improves robustness against malformed HTML).

.. _Release 4.16: https://github.com/xolox/python-humanfriendly/compare/4.15.1...4.16

`Release 4.15.1`_ (2018-07-14)
------------------------------

Bug fixes for HTML to ANSI conversion.

HTML entities were being omitted from conversion because I had neglected to
define the ``handle_charref()`` and ``handle_entityref()`` methods (whose
definitions are so conveniently given in the documentation of the
``HTMLParser`` class 😇).

.. _Release 4.15.1: https://github.com/xolox/python-humanfriendly/compare/4.15...4.15.1

`Release 4.15`_ (2018-07-14)
----------------------------

Added the :func:`humanfriendly.terminal.html_to_ansi()` function which is a
shortcut for the :class:`humanfriendly.terminal.HTMLConverter` class that's
based on ``html.parser.HTMLParser``.

This new functionality converts HTML with simple text formatting tags like
``<b>`` for bold, ``<i>`` for italic, ``<u>`` for underline, ``<span>`` for
colors, etc. to text with ANSI escape sequences.

I'm still working on that awesome new project (update: see chat-archive_), this
functionality was born there but seemed like a useful addition to the
``humanfriendly`` package, given the flexibility that this provides 😇.

.. _Release 4.15: https://github.com/xolox/python-humanfriendly/compare/4.14...4.15

`Release 4.14`_ (2018-07-13)
----------------------------

Support for 24-bit (RGB) terminal colors. Works by accepting a tuple or
list with three integers representing an RGB (red, green, blue) color.

.. _Release 4.14: https://github.com/xolox/python-humanfriendly/compare/4.13...4.14

`Release 4.13`_ (2018-07-09)
----------------------------

Support for *italic* text rendering on the terminal.

I'm working on an awesome new project (update: see chat-archive_) that's almost
ready to publish, but then I noticed that I couldn't render italic text on the
terminal using the humanfriendly package. I checked and sure enough my terminal
supported it just fine, so I didn't see any reason not to fix this now 😇.

.. _Release 4.13: https://github.com/xolox/python-humanfriendly/compare/4.12.1...4.13
.. _chat-archive: https://chat-archive.readthedocs.io/

`Release 4.12.1`_ (2018-05-10)
------------------------------

It was reported in issue `#28`_ that ``humanfriendly --demo`` didn't work
on Python 3 due to two unrelated ``TypeError`` exceptions. First I added
a failing regression test to the test suite (`here's the failing build
<https://travis-ci.org/xolox/python-humanfriendly/builds/377202561>`_)
and then I applied the changes suggested in issue `#28`_, confirming that both
issues are indeed fixed because the test now passes (`here's the successful
build <https://travis-ci.org/xolox/python-humanfriendly/builds/377203446>`_).

.. _Release 4.12.1: https://github.com/xolox/python-humanfriendly/compare/4.12...4.12.1
.. _#28: https://github.com/xolox/python-humanfriendly/issues/28

`Release 4.12`_ (2018-04-26)
----------------------------

- Make :func:`humanfriendly.format_timespan()` accept
  :class:`datetime.timedelta` objects (fixes `#27`_).

- Add ``license`` key to ``setup.py`` script (pointed out to me in `coloredlogs
  pull request #53 <https://github.com/xolox/python-coloredlogs/pull/53>`_).

.. _Release 4.12: https://github.com/xolox/python-humanfriendly/compare/4.11...4.12
.. _#27: https://github.com/xolox/python-humanfriendly/issues/27

`Release 4.11`_ (2018-04-26)
----------------------------

Added this changelog as requested in `#23`_.

I've held off on having to keep track of changelogs in my open source
programming projects until now (2018) because it's yet another piece of
bookkeeping that adds overhead to project maintenance versus just writing the
damn code and throwing it up on GitHub :-p. However all that time I felt bad
for not publishing change logs and I knew that requests would eventually come
in and indeed in the past months I've received two requests in `#23`_ and in
`issue #55 of coloredlogs <https://github.com/xolox/python-coloredlogs/issues/55>`_.

I actually wrote a Python script that uses the ``git tag`` and ``git
for-each-ref`` commands to automatically generate a ``CHANGELOG.rst``
"prototype" (requiring manual editing to clean it up) to bootstrap the contents
of this document. I'm tempted to publish that now but don't want to get
sidetracked even further :-).

.. _Release 4.11: https://github.com/xolox/python-humanfriendly/compare/4.10...4.11
.. _#23: https://github.com/xolox/python-humanfriendly/issues/23

`Release 4.10`_ (2018-03-31)
----------------------------

Added the :func:`humanfriendly.Timer.sleep()` method to sleep "no more than"
the given number of seconds.

.. _Release 4.10: https://github.com/xolox/python-humanfriendly/compare/4.9...4.10

`Release 4.9`_ (2018-03-28)
---------------------------

Added the :func:`humanfriendly.tables.format_rst_table()` function to render
RST (reStructuredText) tables.

.. _Release 4.9: https://github.com/xolox/python-humanfriendly/compare/4.8...4.9

`Release 4.8`_ (2018-01-20)
---------------------------

Added the :func:`humanfriendly.coerce_pattern()` function. I previously created
this for vcs-repo-mgr_ and now need the same thing in qpass_ so I'm putting it
in humanfriendly :-) because it kind of fits with the other coercion functions.

.. _Release 4.8: https://github.com/xolox/python-humanfriendly/compare/4.7...4.8
.. _vcs-repo-mgr: https://vcs-repo-mgr.readthedocs.io/
.. _qpass: https://qpass.readthedocs.io/

`Release 4.7`_ (2018-01-14)
---------------------------

- Added support for background colors and 256 color mode (related to `issue 35
  on the coloredlogs issue tracker <https://github.com/xolox/python-coloredlogs/issues/35>`_).

- Added tests for :func:`~humanfriendly.terminal.output()`,
  :func:`~humanfriendly.terminal.message()` and
  :func:`~humanfriendly.terminal.warning()`.

.. _Release 4.7: https://github.com/xolox/python-humanfriendly/compare/4.6...4.7

`Release 4.6`_ (2018-01-04)
---------------------------

Fixed issue #21 by implementing support for bright (high intensity) terminal colors.

.. _Release 4.6: https://github.com/xolox/python-humanfriendly/compare/4.5...4.6
.. _#21: https://github.com/xolox/python-humanfriendly/issues/21

`Release 4.5`_ (2018-01-04)
---------------------------

Fixed issue `#16` by merging pull request `#17`_: Extend byte ranges, add RAM
output to command line.

In the merge commit I removed the ``--format-bytes`` option that `#17`_ added
and instead implemented a ``--binary`` option which changes ``--format-size``
to use binary multiples of bytes (base-2) instead of decimal multiples of bytes
(base-10).

.. _Release 4.5: https://github.com/xolox/python-humanfriendly/compare/4.4.2...4.5
.. _#16: https://github.com/xolox/python-humanfriendly/issues/16
.. _#17: https://github.com/xolox/python-humanfriendly/pulls/17

`Release 4.4.2`_ (2018-01-04)
-----------------------------

- Fixed ``ImportError`` exception on Windows due to interactive prompts (fixes `#19`_ by merging `#20`_.).
- Enable MacOS builds on Travis CI and document MacOS compatibility.
- Change Sphinx documentation theme.

.. _Release 4.4.2: https://github.com/xolox/python-humanfriendly/compare/4.4.1...4.4.2
.. _#19: https://github.com/xolox/python-humanfriendly/issues/19
.. _#20: https://github.com/xolox/python-humanfriendly/pull/20

`Release 4.4.1`_ (2017-08-07)
-----------------------------

Include the Sphinx documentation in source distributions (same rationales as
for the similar change made to 'coloredlogs' and 'verboselogs').

.. _Release 4.4.1: https://github.com/xolox/python-humanfriendly/compare/4.4...4.4.1

`Release 4.4`_ (2017-07-16)
---------------------------

Added the :func:`~humanfriendly.testing.make_dirs()` and
:func:`~humanfriendly.testing.touch()` functions.

.. _Release 4.4: https://github.com/xolox/python-humanfriendly/compare/4.3...4.4

`Release 4.3`_ (2017-07-10)
---------------------------

Don't log duplicate output in :func:`~humanfriendly.testing.run_cli()`.

.. _Release 4.3: https://github.com/xolox/python-humanfriendly/compare/4.2...4.3

`Release 4.2`_ (2017-07-10)
---------------------------

Automatically reconfigure logging in :func:`~humanfriendly.testing.run_cli()`.

.. _Release 4.2: https://github.com/xolox/python-humanfriendly/compare/4.1...4.2

`Release 4.1`_ (2017-07-10)
---------------------------

Improve :func:`~humanfriendly.testing.run_cli()` to always log standard error
as well.

.. _Release 4.1: https://github.com/xolox/python-humanfriendly/compare/4.0...4.1

`Release 4.0`_ (2017-07-10)
---------------------------

Backwards incompatible improvements to :func:`~humanfriendly.testing.run_cli()`.

I just wasted quite a bit of time debugging a Python 3.6 incompatibility in
deb-pkg-tools (see build 251688788_) which was obscured by my naive
implementation of the ``run_cli()`` function. This change is backwards
incompatible because ``run_cli()`` now intercepts all exceptions whereas
previously it would only intercept ``SystemExit``.

.. _Release 4.0: https://github.com/xolox/python-humanfriendly/compare/3.8...4.0
.. _251688788: https://travis-ci.org/xolox/python-deb-pkg-tools/builds/251688788

`Release 3.8`_ (2017-07-02)
---------------------------

Make it easy to mock the ``$HOME`` directory.

.. _Release 3.8: https://github.com/xolox/python-humanfriendly/compare/3.7...3.8

`Release 3.7`_ (2017-07-01)
---------------------------

Enable customizable skipping of tests.

.. _Release 3.7: https://github.com/xolox/python-humanfriendly/compare/3.6.1...3.7

`Release 3.6.1`_ (2017-06-24)
-----------------------------

Improved the robustness of the :class:`~humanfriendly.testing.PatchedAttribute`
and :class:`~humanfriendly.testing.PatchedItem` classes.

.. _Release 3.6.1: https://github.com/xolox/python-humanfriendly/compare/3.6...3.6.1

`Release 3.6`_ (2017-06-24)
---------------------------

- Made the retry limit in interactive prompts configurable.
- Refactored the makefile and Travis CI configuration.

.. _Release 3.6: https://github.com/xolox/python-humanfriendly/compare/3.5...3.6

`Release 3.5`_ (2017-06-24)
---------------------------

Added ``humanfriendly.testing.TestCase.assertRaises()`` enhancements.

.. _Release 3.5: https://github.com/xolox/python-humanfriendly/compare/3.4.1...3.5

`Release 3.4.1`_ (2017-06-24)
-----------------------------

Bug fix for Python 3 syntax incompatibility.

.. _Release 3.4.1: https://github.com/xolox/python-humanfriendly/compare/3.4...3.4.1

`Release 3.4`_ (2017-06-24)
---------------------------

Promote the command line testing function to the public API.

.. _Release 3.4: https://github.com/xolox/python-humanfriendly/compare/3.3...3.4

`Release 3.3`_ (2017-06-24)
---------------------------

- Added the :func:`humanfriendly.text.random_string()` function.
- Added the :mod:`humanfriendly.testing` module with unittest helpers.
- Define ``humanfriendly.text.__all__``.

.. _Release 3.3: https://github.com/xolox/python-humanfriendly/compare/3.2...3.3

`Release 3.2`_ (2017-05-18)
---------------------------

Added the ``humanfriendly.terminal.output()`` function to auto-encode terminal
output to avoid encoding errors and applied the use of this function in various
places throughout the package.

.. _Release 3.2: https://github.com/xolox/python-humanfriendly/compare/3.1...3.2

`Release 3.1`_ (2017-05-06)
---------------------------

Improved usage message parsing and rendering.

While working on a new project I noticed that the ``join_lines()`` call in
``render_usage()`` could corrupt lists as observed here:

https://github.com/xolox/python-rsync-system-backup/blob/ed73787745e706cb6ab76c73acb2480e24d87d7b/README.rst#command-line (check the part after 'Supported locations include:')

To be honest I'm not even sure why I added that ``join_lines()`` call to begin
with and I can't think of any good reasons to keep it there, so gone it is!

.. _Release 3.1: https://github.com/xolox/python-humanfriendly/compare/3.0...3.1

`Release 3.0`_ (2017-05-04)
---------------------------

- Added support for min, mins abbreviations for minutes based on `#14`_.
- Added Python 3.6 to supported versions on Travis CI and in documentation.

I've decided to bump the major version number after merging pull request `#14`_
because the ``humanfriendly.time_units`` data structure was changed. Even
though this module scope variable isn't included in the online documentation,
nothing stops users from importing it anyway, so this change is technically
backwards incompatible. Besides, version numbers are cheap. In fact, they are
infinite! :-)

.. _Release 3.0: https://github.com/xolox/python-humanfriendly/compare/2.4...3.0
.. _#14: https://github.com/xolox/python-humanfriendly/pull/14

`Release 2.4`_ (2017-02-14)
---------------------------

Make ``usage()`` and ``show_pager()`` more user friendly by changing how
:man:`less` as a default pager is invoked (with specific options).

.. _Release 2.4: https://github.com/xolox/python-humanfriendly/compare/2.3.2...2.4

`Release 2.3.2`_ (2017-01-17)
-----------------------------

Bug fix: Don't hard code conditional dependencies in wheels.

.. _Release 2.3.2: https://github.com/xolox/python-humanfriendly/compare/2.3.1...2.3.2

`Release 2.3.1`_ (2017-01-17)
-----------------------------

Fix ``parse_usage()`` tripping up on commas in option labels.

.. _Release 2.3.1: https://github.com/xolox/python-humanfriendly/compare/2.3...2.3.1

`Release 2.3`_ (2017-01-16)
---------------------------

- Switch to monotonic clock for timers based on `#13`_.
- Change ``readthedocs.org`` to ``readthedocs.io`` everywhere.
- Improve intersphinx references in documentation.
- Minor improvements to setup script.

.. _Release 2.3: https://github.com/xolox/python-humanfriendly/compare/2.2.1...2.3
.. _#13: https://github.com/xolox/python-humanfriendly/issues/13

`Release 2.2.1`_ (2017-01-10)
-----------------------------

- Improve use of timers as context managers by returning the timer object (as originally intended).
- Minor improvements to reStructuredText formatting in various docstrings.

.. _Release 2.2.1: https://github.com/xolox/python-humanfriendly/compare/2.2...2.2.1

`Release 2.2`_ (2016-11-30)
---------------------------

- Fix and add a test for ``parse_date()`` choking on Unicode strings.
- Only use "readline hints" in prompts when standard input is a tty.

.. _Release 2.2: https://github.com/xolox/python-humanfriendly/compare/2.1...2.2

`Release 2.1`_ (2016-10-09)
---------------------------

Added ``clean_terminal_output()`` function to sanitize captured terminal output.

.. _Release 2.1: https://github.com/xolox/python-humanfriendly/compare/2.0.1...2.1

`Release 2.0.1`_ (2016-09-29)
-----------------------------

Update ``README.rst`` based on the changes in 2.0 by merging `#12`_.

.. _Release 2.0.1: https://github.com/xolox/python-humanfriendly/compare/2.0...2.0.1
.. _#12: https://github.com/xolox/python-humanfriendly/pull/12

`Release 2.0`_ (2016-09-29)
---------------------------

Proper support for IEEE 1541 definitions of units (fixes `#4`_, merges `#8`_ and `#9`_).

.. _Release 2.0: https://github.com/xolox/python-humanfriendly/compare/1.44.9...2.0
.. _#4: https://github.com/xolox/python-humanfriendly/issues/4
.. _#8: https://github.com/xolox/python-humanfriendly/pull/8
.. _#9: https://github.com/xolox/python-humanfriendly/pull/9

`Release 1.44.9`_ (2016-09-28)
------------------------------

- Fix and add tests for the timespan formatting issues reported in issues `#10`_ and `#11`_.
- Refactor ``Makefile``, switch to ``py.test``, add wheel support, etc.

.. _#10: https://github.com/xolox/python-humanfriendly/issues/10
.. _#11: https://github.com/xolox/python-humanfriendly/issues/11
.. _Release 1.44.9: https://github.com/xolox/python-humanfriendly/compare/1.44.8...1.44.9

`Release 1.44.8`_ (2016-09-28)
------------------------------

- Fixed `issue #7`_ (``TypeError`` when calling ``show_pager()`` on Python 3) and added a test.
- Minor improvements to the ``setup.py`` script.
- Stop testing tags on Travis CI.

.. _Release 1.44.8: https://github.com/xolox/python-humanfriendly/compare/1.44.7...1.44.8
.. _issue #7: https://github.com/xolox/python-humanfriendly/issues/7

`Release 1.44.7`_ (2016-04-21)
------------------------------

Minor improvements to usage message reformatting.

.. _Release 1.44.7: https://github.com/xolox/python-humanfriendly/compare/1.44.6...1.44.7

`Release 1.44.6`_ (2016-04-21)
------------------------------

Remove an undocumented ``.strip()`` call  from ``join_lines()``.

Why I noticed this: It has the potential to eat significant white
space in usage messages that are marked up in reStructuredText syntax.

Why I decided to change it: The behavior isn't documented and on
second thought I wouldn't expect a function called ``join_lines()``
to strip any and all leading/trailing white space.

.. _Release 1.44.6: https://github.com/xolox/python-humanfriendly/compare/1.44.5...1.44.6

`Release 1.44.5`_ (2016-03-20)
------------------------------

Improved the usage message parsing algorithm (also added a proper test). Refer
to ``test_parse_usage_tricky()`` for an example of a usage message that is now
parsed correctly but would previously confuse the dumb "parsing" algorithm in
``parse_usage()``.

.. _Release 1.44.5: https://github.com/xolox/python-humanfriendly/compare/1.44.4...1.44.5

`Release 1.44.4`_ (2016-03-15)
------------------------------

Made usage message parsing a bit more strict. Admittedly this still needs a lot
more love to make it more robust but I lack the time to implement this at the
moment. Some day soon! :-)

.. _Release 1.44.4: https://github.com/xolox/python-humanfriendly/compare/1.44.3...1.44.4

`Release 1.44.3`_ (2016-02-20)
------------------------------

Unbreak conditional importlib dependency after breakage observed here:
https://travis-ci.org/xolox/python-humanfriendly/builds/110585766

.. _Release 1.44.3: https://github.com/xolox/python-humanfriendly/compare/1.44.2...1.44.3

`Release 1.44.2`_ (2016-02-20)
------------------------------

- Make conditional importlib dependency compatible with wheels: While running
  tox tests of another project of mine that uses the humanfriendly package I
  noticed a traceback when importing the humanfriendly package (because
  importlib was missing). After some digging I found that tox uses pip to
  install packages and pip converts source distributions to wheel distributions
  before/during installation, thereby dropping the conditional importlib
  dependency.

- Added the Sphinx extension trove classifier to the ``setup.py`` script.

.. _Release 1.44.2: https://github.com/xolox/python-humanfriendly/compare/1.44.1...1.44.2

`Release 1.44.1`_ (2016-02-18)
------------------------------

- Fixed a non-fatal but obviously wrong log format error in ``prompt_for_choice()``.
- Added Python 3.5 to supported versions on Travis CI and in the documentation.

.. _Release 1.44.1: https://github.com/xolox/python-humanfriendly/compare/1.44...1.44.1

`Release 1.44`_ (2016-02-17)
----------------------------

Added the ``humanfriendly.sphinx`` module with automagic usage message
reformatting and a bit of code that I'd been copying and pasting between
``docs/conf.py`` scripts for years to include magic methods, etc in
Sphinx generated documentation.

.. _Release 1.44: https://github.com/xolox/python-humanfriendly/compare/1.43.1...1.44

`Release 1.43.1`_ (2016-01-19)
------------------------------

Bug fix for Python 2.6 compatibility in ``setup.py`` script.

.. _Release 1.43.1: https://github.com/xolox/python-humanfriendly/compare/1.43...1.43.1

`Release 1.43`_ (2016-01-19)
----------------------------

Replaced ``import_module()`` with a conditional dependency on ``importlib``.

.. _Release 1.43: https://github.com/xolox/python-humanfriendly/compare/1.42...1.43

`Release 1.42`_ (2015-10-23)
----------------------------

Added proper tests for ANSI escape sequence support.

.. _Release 1.42: https://github.com/xolox/python-humanfriendly/compare/1.41...1.42

`Release 1.41`_ (2015-10-22)
----------------------------

- Moved hard coded ANSI text style codes to a module level ``ANSI_TEXT_STYLES`` dictionary.
- Improved the related error reporting based on the new dictionary.

.. _Release 1.41: https://github.com/xolox/python-humanfriendly/compare/1.40...1.41

`Release 1.40`_ (2015-10-22)
----------------------------

Added support for custom delimiters in ``humanfriendly.text.split()``.

.. _Release 1.40: https://github.com/xolox/python-humanfriendly/compare/1.39...1.40

`Release 1.39`_ (2015-10-22)
----------------------------

Added the ``humanfriendly.compat`` module to group Python 2 / 3 compatibility logic.

.. _Release 1.39: https://github.com/xolox/python-humanfriendly/compare/1.38...1.39

`Release 1.38`_ (2015-10-22)
----------------------------

- Added the ``prompt_for_confirmation()`` function to render (y/n) prompts.
- Improved the prompt rendered by ``prompt_for_choice()``.
- Extracted supporting prompt functionality to separate functions.

.. _Release 1.38: https://github.com/xolox/python-humanfriendly/compare/1.37...1.38

`Release 1.37`_ (2015-10-22)
----------------------------

- Added support for wrapping ANSI escape sequences in "readline hints".
- Work around incompatibility between ``flake8-pep257==1.0.3`` and ``pep257==0.7.0``.

.. _Release 1.37: https://github.com/xolox/python-humanfriendly/compare/1.36...1.37

`Release 1.36`_ (2015-10-21)
----------------------------

Added ``message()`` and ``warning()`` functions to write informational and
warning messages to the terminal (on the standard error stream).

.. _Release 1.36: https://github.com/xolox/python-humanfriendly/compare/1.35...1.36

`Release 1.35`_ (2015-09-10)
----------------------------

Implemented the feature request in issue #6: Support for milleseconds in
timespan parsing/formatting. Technically speaking this breaks backwards
compatibility but only by dropping a nasty (not documented) implementation
detail. Quoting from the old code::

  # All of the first letters of the time units are unique, so
  # although this check is not very strict I believe it to be
  # sufficient.

That no longer worked with [m]illiseconds versus [m]inutes as was
also evident from the feature request / bug report on GitHub.

.. _Release 1.35: https://github.com/xolox/python-humanfriendly/compare/1.34...1.35

`Release 1.34`_ (2015-08-06)
----------------------------

Implemented and added checks to enforce PEP-8 and PEP-257 compliance.

.. _Release 1.34: https://github.com/xolox/python-humanfriendly/compare/1.33...1.34

`Release 1.33`_ (2015-07-27)
----------------------------

Added ``format_length()`` and `parse_length()`` functions via `pull request #5`_.

.. _Release 1.33: https://github.com/xolox/python-humanfriendly/compare/1.32...1.33
.. _pull request #5: https://github.com/xolox/python-humanfriendly/pull/5

`Release 1.32`_ (2015-07-19)
----------------------------

Added the ``humanfriendly.text.split()`` function.

.. _Release 1.32: https://github.com/xolox/python-humanfriendly/compare/1.31...1.32

`Release 1.31`_ (2015-06-28)
----------------------------

Added support for rendering of usage messages to reStructuredText.

.. _Release 1.31: https://github.com/xolox/python-humanfriendly/compare/1.30...1.31

`Release 1.30`_ (2015-06-28)
----------------------------

Started moving functions to separate modules.

.. _Release 1.30: https://github.com/xolox/python-humanfriendly/compare/1.29...1.30

`Release 1.29`_ (2015-06-24)
----------------------------

Added the ``parse_timespan()`` function.

.. _Release 1.29: https://github.com/xolox/python-humanfriendly/compare/1.28...1.29

`Release 1.28`_ (2015-06-24)
----------------------------

Extracted the "new" ``tokenize()`` function from the existing ``parse_size()`` function.

.. _Release 1.28: https://github.com/xolox/python-humanfriendly/compare/1.27...1.28

`Release 1.27`_ (2015-06-03)
----------------------------

Changed table formatting to right-align table columns with numeric data (and
pimped the documentation).

.. _Release 1.27: https://github.com/xolox/python-humanfriendly/compare/1.26...1.27

`Release 1.26`_ (2015-06-02)
----------------------------

Make table formatting 'smart' by having it automatically handle overflow of
columns by switching to a different more verbose vertical table layout.

.. _Release 1.26: https://github.com/xolox/python-humanfriendly/compare/1.25.1...1.26

`Release 1.25.1`_ (2015-06-02)
------------------------------

- Bug fix for a somewhat obscure ``UnicodeDecodeError`` in ``setup.py`` on Python 3.
- Travis CI now also runs the test suite on PyPy.
- Documented PyPy compatibility.

.. _Release 1.25.1: https://github.com/xolox/python-humanfriendly/compare/1.25...1.25.1

`Release 1.25`_ (2015-05-27)
----------------------------

Added the ``humanfriendly.terminal.usage()`` function for nice rendering of
usage messages on interactive terminals (try ``humanfriendly --help`` to see it
in action).

.. _Release 1.25: https://github.com/xolox/python-humanfriendly/compare/1.24...1.25

`Release 1.24`_ (2015-05-27)
----------------------------

Added the ``humanfriendly.terminal`` module with support for ANSI escape
sequences, detecting interactive terinals, finding the terminal size, etc.

.. _Release 1.24: https://github.com/xolox/python-humanfriendly/compare/1.23.1...1.24

`Release 1.23.1`_ (2015-05-26)
------------------------------

Bug fix for Python 3 compatibility in ``format_table()``.

.. _Release 1.23.1: https://github.com/xolox/python-humanfriendly/compare/1.23...1.23.1

`Release 1.23`_ (2015-05-26)
----------------------------

Added ``format_table()`` function to format tabular data in simple textual tables.

.. _Release 1.23: https://github.com/xolox/python-humanfriendly/compare/1.22...1.23

`Release 1.22`_ (2015-05-26)
----------------------------

Added additional string formatting functions ``compact()``, ``dedent()``,
``format()``, ``is_empty_line()`` and ``trim_empty_lines()``.

.. _Release 1.22: https://github.com/xolox/python-humanfriendly/compare/1.21...1.22

`Release 1.21`_ (2015-05-25)
----------------------------

Added support for formatting numbers with thousands separators.

.. _Release 1.21: https://github.com/xolox/python-humanfriendly/compare/1.20...1.21

`Release 1.20`_ (2015-05-25)
----------------------------

- Added a simple command line interface.
- Added trove classifiers to ``setup.py``.

.. _Release 1.20: https://github.com/xolox/python-humanfriendly/compare/1.19...1.20

`Release 1.19`_ (2015-05-23)
----------------------------

Made it possible to use spinners as context managers.

.. _Release 1.19: https://github.com/xolox/python-humanfriendly/compare/1.18...1.19

`Release 1.18`_ (2015-05-23)
----------------------------

Added a ``Spinner.sleep()`` method.

.. _Release 1.18: https://github.com/xolox/python-humanfriendly/compare/1.17...1.18

`Release 1.17`_ (2015-05-23)
----------------------------

- Improved interaction between spinner & verbose log outputs: The spinner until
  now didn't end each string of output with a carriage return because then the
  text cursor would jump to the start of the screen line and disturb the
  spinner, however verbose log output and the spinner don't interact well
  because of this, so I've decided to hide the text cursor while the spinner is
  active.
- Added another example to the documentation of ``parse_date()``.

.. _Release 1.17: https://github.com/xolox/python-humanfriendly/compare/1.16...1.17

`Release 1.16`_ (2015-03-29)
----------------------------

- Change spinners to use the 'Erase in Line' ANSI escape code to properly clear screen lines.
- Improve performance of Travis CI and increase multiprocessing test coverage.

.. _Release 1.16: https://github.com/xolox/python-humanfriendly/compare/1.15...1.16

`Release 1.15`_ (2015-03-17)
----------------------------

- Added support for ``AutomaticSpinner`` that animates without requiring ``step()`` calls.
- Changed the Python package layout so that all ``*.py`` files are in one directory.
- Added tests for ``parse_path()`` and ``Timer.rounded``.

.. _Release 1.15: https://github.com/xolox/python-humanfriendly/compare/1.14...1.15

`Release 1.14`_ (2014-11-22)
----------------------------

- Changed ``coerce_boolean()`` to coerce empty strings to ``False``.
- Added ``parse_path()`` function (a simple combination of standard library functions that I've repeated numerous times).

.. _Release 1.14: https://github.com/xolox/python-humanfriendly/compare/1.13...1.14

`Release 1.13`_ (2014-11-16)
----------------------------

Added support for spinners with an embedded timer.

.. _Release 1.13: https://github.com/xolox/python-humanfriendly/compare/1.12...1.13

`Release 1.12`_ (2014-11-16)
----------------------------

Added support for rounded timestamps.

.. _Release 1.12: https://github.com/xolox/python-humanfriendly/compare/1.11...1.12

`Release 1.11`_ (2014-11-15)
----------------------------

Added ``coerce_boolean()`` function.

.. _Release 1.11: https://github.com/xolox/python-humanfriendly/compare/1.10...1.11

`Release 1.10`_ (2014-11-15)
----------------------------

Improved ``pluralize()`` by making it handle the simple case of pluralizing by adding 's'.

.. _Release 1.10: https://github.com/xolox/python-humanfriendly/compare/1.9.6...1.10

`Release 1.9.6`_ (2014-09-14)
-----------------------------

Improved the documentation by adding a few docstring examples via pull request `#3`_.

.. _Release 1.9.6: https://github.com/xolox/python-humanfriendly/compare/1.9.5...1.9.6
.. _#3: https://github.com/xolox/python-humanfriendly/pull/3

`Release 1.9.5`_ (2014-06-29)
-----------------------------

Improved the test suite by making the timing related tests less sensitive to
slow test execution. See
https://travis-ci.org/xolox/python-humanfriendly/jobs/28706938 but the same
thing can happen anywhere. When looked at from that perspective the fix I'm
committing here really isn't a fix, but I suspect it will be fine :-).

.. _Release 1.9.5: https://github.com/xolox/python-humanfriendly/compare/1.9.4...1.9.5

`Release 1.9.4`_ (2014-06-29)
-----------------------------

- Fixed Python 3 compatibility (``input()`` versus ``raw_input()``). See https://travis-ci.org/xolox/python-humanfriendly/jobs/28700750.
- Removed a ``print()`` in the test suite, left over from debugging.

.. _Release 1.9.4: https://github.com/xolox/python-humanfriendly/compare/1.9.3...1.9.4

`Release 1.9.3`_ (2014-06-29)
-----------------------------

- Automatically disable ``Spinner`` when ``stream.isatty()`` returns ``False``.
- Improve the makefile by adding ``install`` and ``coverage`` targets.
- Remove the makefile generated by Sphinx (all we need from it is one command).
- Add unit tests for ``prompt_for_choice()`` bringing coverage back up to 95%.

.. _Release 1.9.3: https://github.com/xolox/python-humanfriendly/compare/1.9.2...1.9.3

`Release 1.9.2`_ (2014-06-29)
-----------------------------

Added support for 'B' bytes unit to ``parse_size()`` via `pull request #2`_.

.. _Release 1.9.2: https://github.com/xolox/python-humanfriendly/compare/1.9.1...1.9.2
.. _pull request #2: https://github.com/xolox/python-humanfriendly/pull/2

`Release 1.9.1`_ (2014-06-23)
-----------------------------

Improved the ``prompt_for_choice()`` function by clearly presenting the default
choice (if any).

.. _Release 1.9.1: https://github.com/xolox/python-humanfriendly/compare/1.9...1.9.1

`Release 1.9`_ (2014-06-23)
---------------------------

Added the ``prompt_for_choice()`` function.

.. _Release 1.9: https://github.com/xolox/python-humanfriendly/compare/1.8.6...1.9

`Release 1.8.6`_ (2014-06-08)
-----------------------------

Enable ``Spinner`` to show progress counter (percentage).

.. _Release 1.8.6: https://github.com/xolox/python-humanfriendly/compare/1.8.5...1.8.6

`Release 1.8.5`_ (2014-06-08)
-----------------------------

Make ``Timer`` objects "resumable".

.. _Release 1.8.5: https://github.com/xolox/python-humanfriendly/compare/1.8.4...1.8.5

`Release 1.8.4`_ (2014-06-07)
-----------------------------

Make the ``Spinner(label=...)`` argument optional.

.. _Release 1.8.4: https://github.com/xolox/python-humanfriendly/compare/1.8.3...1.8.4

`Release 1.8.3`_ (2014-06-07)
-----------------------------

Make it possible to override the label for individual steps of spinners.

.. _Release 1.8.3: https://github.com/xolox/python-humanfriendly/compare/1.8.2...1.8.3

`Release 1.8.2`_ (2014-06-01)
-----------------------------

Automatically rate limit ``Spinner`` instances.

.. _Release 1.8.2: https://github.com/xolox/python-humanfriendly/compare/1.8.1...1.8.2

`Release 1.8.1`_ (2014-05-11)
-----------------------------

- Improve Python 3 compatibility: Make sure sequences passed to ``concatenate()`` are lists.
- Submit test coverage from Travis CI to Coveralls.io.
- Increase test coverage of ``concatenate()``, ``Spinner()`` and ``Timer()``.
- Use ``assertRaises()`` instead of ``try``, ``except`` and ``isinstance()`` in test suite.

.. _Release 1.8.1: https://github.com/xolox/python-humanfriendly/compare/1.8...1.8.1

`Release 1.8`_ (2014-05-10)
---------------------------

- Added support for Python 3 thanks to a pull request.
- Document the supported Python versions (2.6, 2.7 and 3.4).
- Started using Travis CI to automatically run the test suite.

.. _Release 1.8: https://github.com/xolox/python-humanfriendly/compare/1.7.1...1.8

`Release 1.7.1`_ (2013-09-22)
-----------------------------

Bug fix for ``concatenate()`` when given only one item.

.. _Release 1.7.1: https://github.com/xolox/python-humanfriendly/compare/1.7...1.7.1

`Release 1.7`_ (2013-09-22)
---------------------------

Added functions ``concatenate()`` and ``pluralize()``, both originally
developed in private scripts.

.. _Release 1.7: https://github.com/xolox/python-humanfriendly/compare/1.6.1...1.7

`Release 1.6.1`_ (2013-09-22)
-----------------------------

Bug fix: Don't raise an error in ``format_path()`` if $HOME isn't set.

.. _Release 1.6.1: https://github.com/xolox/python-humanfriendly/compare/1.6...1.6.1

`Release 1.6`_ (2013-08-12)
---------------------------

Added a ``Spinner`` class that I originally developed for `pip-accel
<https://github.com/paylogic/pip-accel>`_.

.. _Release 1.6: https://github.com/xolox/python-humanfriendly/compare/1.5...1.6

`Release 1.5`_ (2013-07-07)
---------------------------

Added a ``Timer`` class to easily keep track of long running operations.

.. _Release 1.5: https://github.com/xolox/python-humanfriendly/compare/1.4.3...1.5

`Release 1.4.3`_ (2013-07-06)
-----------------------------

Fixed various edge cases in ``format_path()``, making it more robust.

.. _Release 1.4.3: https://github.com/xolox/python-humanfriendly/compare/1.4.2...1.4.3

`Release 1.4.2`_ (2013-06-27)
-----------------------------

Improved the project description in ``setup.py`` and added a link to online
documentation on PyPI.

.. _Release 1.4.2: https://github.com/xolox/python-humanfriendly/compare/1.4.1...1.4.2

`Release 1.4.1`_ (2013-06-27)
-----------------------------

Renamed the package from ``human-friendly`` to ``humanfriendly``.

.. _Release 1.4.1: https://github.com/xolox/python-humanfriendly/compare/1.4...1.4.1

`Release 1.4`_ (2013-06-17)
---------------------------

Added the ``parse_date()`` function.

.. _Release 1.4: https://github.com/xolox/python-humanfriendly/compare/1.3.1...1.4

`Release 1.3.1`_ (2013-06-17)
-----------------------------

- Improved the documentation by adding lots of examples.
- Renamed the arguments to the ``format_size()`` and ``format_timespan()`` functions.

.. _Release 1.3.1: https://github.com/xolox/python-humanfriendly/compare/1.3...1.3.1

`Release 1.3`_ (2013-06-17)
---------------------------

Added the ``format_timespan()`` function.

.. _Release 1.3: https://github.com/xolox/python-humanfriendly/compare/1.2...1.3

`Release 1.2`_ (2013-06-17)
---------------------------

Started using Sphinx to generate API documentation from docstrings.

.. _Release 1.2: https://github.com/xolox/python-humanfriendly/compare/1.1...1.2

`Release 1.1`_ (2013-06-17)
---------------------------

Added the ``format_path()`` function.

.. _Release 1.1: https://github.com/xolox/python-humanfriendly/compare/1.0...1.1

`Release 1.0`_ (2013-06-17)
---------------------------

The initial commit of the project, created by gathering functions from various
personal scripts that I wrote over the past years.

.. _Release 1.0: https://github.com/xolox/python-humanfriendly/tree/1.0
