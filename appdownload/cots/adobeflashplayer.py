""" Implementation of Product class for Adobe Flash Player

 {https://www.python.org/dev/peps/pep-0257/
The docstring for a module should generally list the classes, exceptions and
functions (and any other objects) that are exported by the module, with a
one-line summary of each. (These summaries generally give less detail than the
summary line in the object's docstring.)

"""


import os
import cots


__author__ = "Frederic MEZOU"
__version__ = "0.3.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


__all__ = [
    "AdobeFlashPlayer"
]


class AdobeFlashPlayer(cots.Product):
    """Adobe Flash Player derived Product class.

    {https://www.python.org/dev/peps/pep-0257/
    The docstring for a class should summarize its behavior and list the public
    methods and instance variables. If the class is intended to be subclassed,
    and has an additional interface for subclasses, this interface should be
    listed separately (in the docstring). The class constructor should be
    documented in the docstring for its __init__ method.
    Individual methods should be documented by their own docstring.

    If a class subclasses another class and its behavior is mostly inherited
    from that class, its docstring should mention this and summarize the
    differences. Use the verb "override" to indicate that a subclass method
    replaces a superclass method and does not call the superclass method; use
    the verb "extend" to indicate that a subclass method calls the superclass
    method (in addition to its own behavior).}

    Public instance variables
    name: name of the product
    version: current version of the product
    modified: modification date of the installer
    filename: filename of the installer (full path)
    inst_args: arguments to do a standard installation.
    silent_inst_arg: arguments to do a silent installation.

    Public methods
    None

    Subclass API variables (i.e. may be use by subclass)
    _url_origin: url of the latest version of the product

    Subclass API Methods (i.e. may be overwritten by subclass)
    check: checks if a new version is available
    download: download the latest version of the installer
    """
    pass
