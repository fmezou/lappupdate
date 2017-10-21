"""
This module is a dummy product handler. It provides as an example of
implementation.


Public Classes
--------------
This module has only one public class.

===================================  ===================================
:class:`DummyHandler`                ..
===================================  ===================================
"""

import datetime
import logging

from cots import core
from support import semver

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "DummyHandler"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html# configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class DummyHandler(core.BaseProduct):
    """
    Dummy product handler.

    This concrete class implements the tracking mechanism for a dummy
    product. So most of information are in the :mod:`core` and more particularly
    in the `BaseProduct` class documentation. The information below focuses on
    the added value of this class.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `get_origin`                         `is_update`
        ===================================  ===================================
    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        super().__init__()

        # At this point, only name and catalog location are known.
        # All others attributes will be discovered during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "Dummy Product"

        msg = "<<< ()=None"
        _logger.debug(msg)

    def is_update(self, product):
        """
        Return if this instance is an update of product.

        This method compare the version of the two product, and return the
        comparison result. The version numbers used by the editor are compliant
        with the semantic versioning specification 2.0.0 (see `support.semver`
        module)

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: `True` if this instance is an update of the product specified
            by the `product` parameter.

        Raises:
            TypeError: Parameters type mismatch.
        """
        msg = ">>> (product={})"
        _logger.debug(msg.format(product))

        # check parameters type
        if not isinstance(product, DummyHandler):
            msg = "product argument must be a class 'makemv.product'. not {0}"
            msg = msg.format(product.__class__)
            raise TypeError(msg)

        # comparison based on version number.
        result = True
        try:
            a = semver.SemVer(self.version)
        except ValueError as err:
            msg = "Internal error: current product version - {}"
            _logger.error(msg.format(str(err)))
            result = False
        else:
            try:
                b = semver.SemVer(product.version)
            except ValueError as err:
                msg = "Internal error: deployed product version - {}"
                _logger.error(msg.format(str(err)))
                result = False
            else:
                result = bool(a > b)

        if result:
            msg = "It is an update ({} vs. {})."
            _logger.info(msg.format(self.version, product.version))
        else:
            msg = "{} is not an update."
            _logger.info(msg.format(self.version))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def get_origin(self, version=None):
        """
        Get product information from the remote repository.

        Args:
            version (str): The version of the reference product (i.e. the
                deployed product). It'a string following the editor versioning
                rules.

        Returns:
            bool: `True` if the download of the file went well. In case of
            failure, the members are not modified and an error log is written.

        Raises:
            TypeError: Parameters type mismatch.
        """
        msg = ">>> (version={})"
        _logger.debug(msg.format(version))

        # check parameters type
        if version is not None and not isinstance(version, str):
            msg = "version argument must be a class 'str' or None. not {0}"
            msg = msg.format(version.__class__)
            raise TypeError(msg)

        msg = "Fetching the latest product information since the version {}"
        _logger.info(msg.format(self.version))
        result = True
        self.name = "Dummy Product"
        self.version = "1.0.1"
        self.display_name = "{} v{}".format(self.name, self.version)
        dt = (datetime.datetime.now()).replace(microsecond=0)
        self.published = dt.isoformat()
        self.target = core.TARGET_UNIFIED
        self.description = "This dummy module is a trivial example of a " \
                           "Product class implementation. "
        self.editor = "Example. inc"
        self.web_site_location = "http://www.example.com/index.html"
        self.location = "http://www.example.com/dist.zip"
        self.icon = ""
        self.announce_location = "http://www.example.com/news.txt"
        self.feed_location = "http://www.example.com/feed.rss"
        self.release_note_location = "http://www.example.com/release_note.txt"
        self.change_summary = \
            "<ul>" \
            "<li>version 1.0.0 published on 2016-02-02</li>" \
            "<ul>" \
            "<li>a dummy feature</li>" \
            "<li>Small miscellaneous improvements and bugfixes</li>" \
            "</ul>" \
            "<li>version 0.1.0 published on 2015-02-02</li>" \
            "<ul>" \
            "<li>initial commit</li>" \
            "</ul>" \
            "</ul>"
        self.file_size = -1
        self.secure_hash = None
        self.std_inst_args = ""
        self.silent_inst_args = "/silent"

        msg = "Latest product information fetched ({} published on {})"
        _logger.info(msg.format(self.version, self.published))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result
