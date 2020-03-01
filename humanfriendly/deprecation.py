# Human friendly input/output in Python.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 1, 2020
# URL: https://humanfriendly.readthedocs.io

"""
Support for deprecation warnings when importing names from old locations.

When software evolves, things tend to move around. This is usually detrimental
to backwards compatibility (in Python this primarily manifests itself as
:exc:`~exceptions.ImportError` exceptions).

While backwards compatibility is very important, it should not get in the way
of progress. It would be great to have the agility to move things around
without breaking backwards compatibility.

This is where the :mod:`humanfriendly.deprecation` module comes in: It enables
the definition of backwards compatible aliases that emit a deprecation warning
when they are accessed.

The way it works is that it wraps the original module in an :class:`DeprecationProxy`
object that defines a :func:`~DeprecationProxy.__getattr__()` special method to
override attribute access of the module.
"""

# Standard library modules.
import collections
import importlib
import sys
import types
import warnings

# Modules included in our package.
from humanfriendly.text import format

# Registry of known aliases (used by humanfriendly.sphinx).
REGISTRY = collections.defaultdict(dict)

# Public identifiers that require documentation.
__all__ = ("DeprecationProxy", "define_aliases", "get_aliases")


def define_aliases(module_name, **aliases):
    """
    Update a module with backwards compatible aliases.

    :param module_name: The ``__name__`` of the module (a string).
    :param aliases: Each keyword argument defines an alias. The values
                    are expected to be "dotted paths" (strings).

    The behavior of this function depends on whether the Sphinx documentation
    generator is active, because the use of :class:`DeprecationProxy` to shadow the
    real module in :data:`sys.modules` has the unintended side effect of
    breaking autodoc support for ``:data:`` members (module variables).

    To avoid breaking Sphinx the proxy object is omitted and instead the
    aliased names are injected into the original module namespace, to make sure
    that imports can be satisfied when the documentation is being rendered.

    If you run into cyclic dependencies caused by :func:`define_aliases()` when
    running Sphinx, you can try moving the call to :func:`define_aliases()` to
    the bottom of the Python module you're working on.
    """
    module = sys.modules[module_name]
    proxy = DeprecationProxy(module, aliases)
    # Populate the registry of aliases.
    for name, target in aliases.items():
        REGISTRY[module.__name__][name] = target
    # Avoid confusing Sphinx.
    if "sphinx" in sys.modules:
        for name, target in aliases.items():
            setattr(module, name, proxy.resolve(target))
    else:
        # Install a proxy object to raise DeprecationWarning.
        sys.modules[module_name] = proxy


def get_aliases(module_name):
    """
    Get the aliases defined by a module.

    :param module_name: The ``__name__`` of the module (a string).
    :returns: A dictionary with string keys and values:

              1. Each key gives the name of an alias
                 created for backwards compatibility.

              2. Each value gives the dotted path of
                 the proper location of the identifier.

              An empty dictionary is returned for modules that
              don't define any backwards compatible aliases.
    """
    return REGISTRY.get(module_name, {})


class DeprecationProxy(types.ModuleType):

    """Emit deprecation warnings for imports that should be updated."""

    def __init__(self, module, aliases):
        """
        Initialize an :class:`DeprecationProxy` object.

        :param module: The original module object.
        :param aliases: A dictionary of aliases.
        """
        # Initialize our superclass.
        super(DeprecationProxy, self).__init__(name=module.__name__)
        # Store initializer arguments.
        self.module = module
        self.aliases = aliases

    def __getattr__(self, name):
        """
        Override module attribute lookup.

        :param name: The name to look up (a string).
        :returns: The attribute value.
        """
        # Check if the given name is an alias.
        target = self.aliases.get(name)
        if target is not None:
            # Emit the deprecation warning.
            warnings.warn(
                format("%s.%s was moved to %s, please update your imports", self.module.__name__, name, target),
                category=DeprecationWarning,
                stacklevel=2,
            )
            # Resolve the dotted path.
            return self.resolve(target)
        # Look up the name in the original module namespace.
        value = getattr(self.module, name, None)
        if value is not None:
            return value
        # Fall back to the default behavior.
        raise AttributeError(format("module '%s' has no attribute '%s'", self.module.__name__, name))

    def resolve(self, target):
        """
        Look up the target of an alias.

        :param target: The fully qualified dotted path (a string).
        :returns: The value of the given target.
        """
        module_name, _, member = target.rpartition(".")
        module = importlib.import_module(module_name)
        return getattr(module, member)
