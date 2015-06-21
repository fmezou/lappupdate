"""Initialise COTS package

The docstring for a package (i.e., the docstring of the package's
__init__.py module) should also list the modules and subpackages exported by
the package.
see __all__
"""


import datetime


__author__ = "Frederic MEZOU"
__version__ = "0.3.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


__all__ = [
    "Product"
]


class Product:
    """Product base class.

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

    def __init__(self, name):
        """Constructor
        Parameters
            name: name of the product.
        """
        self.name = name
        self.version = ""
        self.date = None
        self._url_update = None
        self.installer_filename = None
        self.args = ""
        self.silent_args = ""

    def check_upgrade(self):
        raise NotImplementedError

    def download_upgrade(self):
        raise NotImplementedError

