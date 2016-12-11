"""
This module is a mocking product handler to test the `lapptrack` module or any
python module using the `cots` package.

This module differs from the dummy module, because the latter exists as an
example (more precisely as a skeleton) to implement a product handler.


Public Classes
--------------
This module includes a number of *handlers* listed below in alphabetical order.
A mocking handler is a derived class from the `BaseMockHandler` class.

===================================  ===================================
:class:`ContentErrorMockHandler`     :class:`MockHandler`
:class:`HTTPMockHandler`
===================================  ===================================
"""


import datetime
import logging
import os
import os.path
import urllib.error


from cots import core


__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "MockHandler",
    "HTTPMockHandler",
    "ContentErrorMockHandler"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html# configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BaseMockHandler(core.BaseProduct):
    """
    Common base class for mocking handler.

    This class is a base class for mocking handler used to test the `lapptrack`
    module or any python module using the `cots` package. Most of information
    about handler mechanism are in the :mod:`cots.core` module and more
    particularly in the `BaseProduct` class documentation.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `dump`                               `is_update`
        `fetch`                              `load`
        `get_origin`                          ..
        ===================================  ===================================
    """
    def __init__(self):
        super().__init__()

        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "BaseMocker"

    def load(self, attributes=None):
        """
        Load the saved handler class attributes.

        Args:
            attributes (dict): The instance variables values to set. Previous
                value of the instance variables kept if this argument value is
                None. The key value pairs which don't exist in the
                instance variables dictionary are ignored.

        Raises:
            TypeError: Parameters type mismatch.
        """
        msg = "load(attributes={})".format(attributes)
        _logger.debug(msg)
        super().load(attributes)

    def dump(self):
        """
        Dump the handler class attributes.

        The method use a variable named ``attributes`` to store a copy of
        public attributes. The ``attributes`` content may be altered by the
        script.

        Returns:
            dict: Contain a copy of the instance variables values.
        """
        attributes = super().dump()
        msg = "dump() -> attributes={}".format(attributes)
        _logger.debug(msg)
        return attributes

    def get_origin(self, version=None):
        """
        Get the mocking information.

        Args:
            version (str): The version of the reference product.
        """
        # check parameters type
        msg = "get_origin(version={})".format(version)
        _logger.debug(msg)

        if version is not None and not isinstance(version, str):
            msg = "version argument must be a class 'str' or None. not {0}"
            msg = msg.format(version.__class__)
            raise TypeError(msg)

        if version is None:
            # set the instance variables to the default value
            self.target = core.TARGET_UNIFIED
            self.web_site_location = "http://mockapp.example.com"
            self.announce_location = ""
            self.feed_location = ""
            self.release_note_location = \
                "http://mockapp.example.com/history.html"
            self.std_inst_args = ""
            self.silent_inst_args = "/S"

            patch = 0
            if version:
                patch = 1 + int(version.split(".")[2])
            self.version = "1.0.{}".format(patch)
            self.display_name = "{} v{}".format(self.name, self.version)

            dt = (datetime.datetime.now()).replace(microsecond=0)
            self.published = dt.isoformat()

            self.description = "Mocking handler"
            self.editor = "MockApp. Inc"
            self.location = "http://mockapp.example.com/dist.zip"
            self.icon = None
            self.change_summary = \
                "<ul>" \
                "<li>a feature</li>" \
                "<li>Small miscellaneous improvements and bugfixes</li>" \
                "</ul>"
            self.file_size = -1
            self.secure_hash = None
        else:
            assert self.target == core.TARGET_UNIFIED
            assert self.web_site_location == "http://mockapp.example.com"
            assert self.announce_location == ""
            assert self.feed_location == ""
            assert self.release_note_location == \
                "http://mockapp.example.com/history.html"
            assert self.std_inst_args == ""
            assert self.silent_inst_args == "/S"
            assert self.display_name == "{} v{}".format(self.name, self.version)

            patch = 0
            if version:
                patch = 1 + int(version.split(".")[2])
            self.version = "1.0.{}".format(patch)

            dt = (datetime.datetime.now()).replace(microsecond=0)
            self.published = dt.isoformat()

            assert self.description == "Mocking handler"
            assert self.editor == "MockApp. Inc"
            assert self.location == "http://mockapp.example.com/dist.zip"
            assert self.icon is None
            assert self.change_summary == \
                "<ul>" \
                "<li>a feature</li>" \
                "<li>Small miscellaneous improvements and bugfixes</li>" \
                "</ul>"
            assert self.file_size == -1
            assert self.secure_hash is None

    def fetch(self, dirpath):
        """
        Download the mocking installer.

        Args:
            dirpath (str): The path name where to store the installer package.
        """
        msg = "fetch(dirpath={})".format(dirpath)
        _logger.debug(msg)

        content = """
        This file is the result of the use of a mocking handler.
        """
        os.makedirs(dirpath, exist_ok=True)
        name = "{}_{}{}".format(self.name, self.version, ".txt")
        pathname = os.path.join(dirpath, name)
        with open(pathname, mode="w") as file:
            file.writelines(content)

    def is_update(self, product):
        """
        Return if this instance is an update.

        The method use a variable named ``update`` to store the result of the
        comparison. The ``update`` content may be altered by the script.

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: True if this instance is an update of the product specified
            by the :dfn:`product` parameter.
        """
        # Execute the additional statement in the context of the current method.
        update = False
        msg = "is_update(product={}) -> {}".format(product, update)
        _logger.debug(msg)
        return update


class MockHandler(BaseMockHandler):
    """
    Mocking handler.

    This concrete class implements a mocking handler used to test the 
    `lapptrack` module or any python module using the `cots` package. Most of 
    information about handler mechanism are in the :mod:`cots.core` and more 
    particularly in the `BaseProduct` class documentation.
    """
    def __init__(self):
        super().__init__()

        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "Mocker"


class HTTPMockHandler(BaseMockHandler):
    """
    HTTP Error mocking handler.

    This concrete class implements a mocking handler used to test the
    `lapptrack` module or any python module using the `cots` package. This
    handler raises an `urllib.error.HTTPError` exception on the `fetch` or
    `get_origin` method call. In this context, `is_update` method should not be
    called so his call raise an `AssertionError` exception.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `fetch`                              `is_update`
        `get_origin`
        ===================================  ===================================
    """
    def __init__(self):
        super().__init__()

        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "HTTPMocker"

    def get_origin(self, version=None):
        """
        Get the mocking information.

        This method always raises an `urllib.error.HTTPError` exception with
        the status code 403 (see :rfc:`2616` which defines HTTP status code)

        Args:
            version (str): The version of the reference product.
        """
        msg = "get_origin(version={})".format(version)
        _logger.debug(msg)

        raise urllib.error.HTTPError("", 403, "Forbidden", [], None)

    def fetch(self, dirpath):
        """
        Download the mocking installer.

        This method always raises an `urllib.error.HTTPError` exception with
        the status code 403 (see :rfc:`2616` which defines HTTP status code)

        Args:
            dirpath (str): The path name where to store the installer package.
        """
        msg = "fetch(dirpath={})".format(dirpath)
        _logger.debug(msg)

        raise urllib.error.HTTPError("", 403, "Forbidden", [], None)

    def is_update(self, product):
        """
        Return if this instance is an update.

        In this context, this method should not be called.

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: True if this instance is an update of the product specified
            by the `product` parameter.
        """
        # Execute the additional statement in the context of the current method.
        assert False


class ContentErrorMockHandler(BaseMockHandler):
    """
    Content Error mocking handler.

    This concrete class implements a mocking handler used to test the 
    `lapptrack` module or any python module using the `cots` package. This 
    handler raises an `core.ContentTypeError` exception on the `fetch`
    or `get_origin` method call. In this context, `is_update` method should not 
    be called so his call raise an `AssertionError` exception.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `fetch`                              `is_update`
        `get_origin`
        ===================================  ===================================
    """
    def __init__(self):
        super().__init__()

        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "ContentMocker"

    def get_origin(self, version=None):
        """
        Get the mocking information.

        This method always raises an `core.ContentTypeError`
        exception.

        Args:
            version (str): The version of the reference product.
        """
        msg = "get_origin(version={})".format(version)
        _logger.debug(msg)

        raise core.ContentTypeError("", "unknown", "text/plain")

    def fetch(self, dirpath):
        """
        Download the mocking installer.

        This method always raises an `core.ContentTypeError`
        exception.

        Args:
            dirpath (str): The path name where to store the installer package.
        """
        msg = "fetch(dirpath={})".format(dirpath)
        _logger.debug(msg)

        raise core.ContentTypeError("", "unknown", "text/plain")

    def is_update(self, product):
        """
        Return if this instance is an update.

        In this context, this method should not be called.

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: True if this instance is an update of the product specified
            by the `product` parameter.
        """
        # Execute the additional statement in the context of the current method.
        assert False
