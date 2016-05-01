"""
This module is a dummy product handler. It provides as an example of
implementation.


Public Classes
==============
This module has only one public class.

===================================  ===================================
:class:`Product`                     ..
===================================  ===================================
"""


import datetime
import logging

from cots import core
from cots import semver


__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "Product"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Product(core.BaseProduct):
    """
    Dummy product handler.

    This concrete class implements the tracking mechanism for a dummy
    product. So most of information are in the :mod:`core` and more particularly
    in the `BaseProduct` class documentation. The information blow focuses on
    the added value of this class.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `_get_description`                   `_get_release_note`
        `_get_display_name`                  `_get_silent_inst_args`
        `_get_editor`                        `_get_std_inst_args`
        `_get_file_size`                     `_get_target`
        `_get_hash`                          `_get_url`
        `_get_icon`                          `_get_version`
        `_get_name`                          `_parse_catalog`
        `_get_published`                     ..
        ===================================  ===================================
    """
    def __init__(self):
        super().__init__()

        # At this point, only name and catalog url are known.
        # All others attributes will be discovered during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "Dummy Product"
        self._catalog_url = "http://www.example.com/index.html"

    def is_update(self, product):
        """
        Return if this instance is an update of product.

        This method compare the version of the two product, and return the
        comparison result. The version numbers used by the editor are compliant
        with the semantic versioning specification 2.0.0 (see `cots.semver`
        module)

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: True if this instance is an update of the product specified
                by the `product` parameter.

        Raises:
            TypeError: Parameters type mismatch.
        """
        # check parameters type
        if not isinstance(product, Product):
            msg = "product argument must be a class 'makemv.product'. not {0}"
            msg = msg.format(product.__class__)
            raise TypeError(msg)

        # comparison based on version number.
        result = False
        if semver.SemVer(self.version) < semver.SemVer(product.version):
            result = True
            msg = "A new version exist ({})."
            _logger.debug(msg.format(product.version))
        else:
            msg = "No new version available."
            _logger.debug(msg)
        return result

    def _parse_catalog(self, filename):
        """
        Parse the catalog.

        This method parses the downloaded product catalog to prepare
        ``_get_...`` methods call.

        Parameters
            filename (str): The local name of the downloaded product catalog.
         """
        _logger.debug(filename)

    def _get_name(self):
        """Extract the name of the product."""
        self.name = "Dummy Product"

    def _get_display_name(self):
        """
        Extract the name of the product as it appears in the 'Programs and
        Features' control panel.

        This name is built from the name and the version attribute, thus this
        method must be called after `_get_name` and `_get_version`.
        """
        name = "{} ({})"
        self.display_name = name.format(self.name, self.version)

    def _get_version(self):
        """Extract the current version of the product from the PAD File."""
        self.version = "1.0.1"

    def _get_published(self):
        """Extract the date of the installer’s publication from the PAD file."""
        dt = (datetime.datetime.now()).replace(microsecond=0)
        self.published = dt.isoformat()

    def _get_description(self):
        """Extract the short description of the product (~250 characters)."""
        self.description = "This dummy module is a trivial example of a " \
                           "Product class implementation. "

    def _get_editor(self):
        """Extract the name of the editor of the product."""
        self.editor = "Example. inc"

    def _get_url(self):
        """Extract the url of the current version of the installer."""
        self.url = "http://www.example.com/index.html"

    def _get_file_size(self):
        """Extract the size of the product installer expressed in bytes."""
        self.file_size = -1

    def _get_hash(self):
        """Extract the secure_hash value of the product installer (tuple)."""
        self.secure_hash = None

    def _get_icon(self):
        """Extract the name of the icon file."""
        self.icon = None

    def _get_target(self):
        """Extract the target architecture type (the Windows’ one)."""
        self.target = core.PROD_TARGET_UNIFIED

    def _get_release_note(self):
        """Extract the release note’s URL."""
        self.release_note = "http://www.example.com/release_note.txt"

    def _get_std_inst_args(self):
        """Extract the arguments to use for a standard installation."""
        self.std_inst_args = ""

    def _get_silent_inst_args(self):
        """Extract the arguments to use for a silent installation."""
        self.silent_inst_args = "/silent"
