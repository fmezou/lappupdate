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
:class:`BaseMockHandler`             :class:`FailureMockHandler`
:class:`ErrorMockHandler`            :class:`MockHandler`
===================================  ===================================
"""


import logging
import os
import os.path


from cots import core
from support import semver

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "BaseMockHandler",
    "MockHandler",
    "BrotherMockHandler",
    "FailureMockHandler",
    "ErrorMockHandler"
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
        msg = ">>> ()"
        _logger.debug(msg)
        super().__init__()

        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "BaseMocker"

        msg = "<<< ()=None"
        _logger.debug(msg)

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
        msg = ">>> (attributes={})"
        _logger.debug(msg.format(attributes))
        super().load(attributes)

        msg = "<<< ()=None"
        _logger.debug(msg)

    def dump(self):
        """
        Dump the handler class attributes.

        The method use a variable named ``attributes`` to store a copy of
        public attributes. The ``attributes`` content may be altered by the
        script.

        Returns:
            dict: Contain a copy of the instance variables values.
        """
        msg = ">>> ()"
        _logger.debug(msg)
        attributes = super().dump()

        msg = "<<< ()={}"
        _logger.debug(msg.format(attributes))
        return attributes

    def get_origin(self, version=None):
        """
        Get the mocking information.

        Args:
            version (str): The version of the reference product.

        Returns:
            bool: always True.
        """
        msg = ">>> (version={})"
        _logger.debug(msg.format(version))
        # check parameters type
        if version is not None and not isinstance(version, str):
            msg = "version argument must be a class 'str' or None. not {0}"
            msg = msg.format(version.__class__)
            raise TypeError(msg)

        result = True
        # set the instance variables to the default value
        self.target = core.TARGET_UNIFIED
        self.web_site_location = "http://mockapp.example.com"
        self.announce_location = ""
        self.feed_location = ""
        self.release_note_location = \
            "http://mockapp.example.com/history.html"
        self.std_inst_args = ""
        self.silent_inst_args = "/S"
        self.version = "1.0.0"
        self.display_name = "{} v{}".format(self.name, self.version)
        self.published = "2017-01-01T16:00:00"
        self.description = "Mocking handler"
        self.editor = "MockApp. Inc"
        self.location = "http://mockapp.example.com/dist.zip"
        self.icon = ""
        self.change_summary = "<ul><li>Stable version</li></ul>"
        self.file_size = 56
        self.secure_hash = ("sha1", "0b148ea595fb66a91b70b74893062d78341c5a54")

        msg = "Latest product information fetched ({} published on {})"
        _logger.info(msg.format(self.version, self.published))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def fetch(self, dirpath):
        """
        Download the mocking installer.


        Args:
            dirpath (str): The directory path name where to store the installer
                package.

        Returns:
            bool: `True` if the fake installer creation went well. In case of
            failure, the members are not modified and an error log is written.

        Raises:
            `TypeError`: Parameters type mismatch.
        """
        msg = ">>> (dirpath={})"
        _logger.debug(msg.format(dirpath))

        result = True
        content = "This file is the result of the use of a mocking handler."
        os.makedirs(dirpath, exist_ok=True)
        name = "{}_v{}_{}{}".format(self.name, self.version,
                                    self.target, ".txt")
        pathname = os.path.join(dirpath, name)
        try:
            with open(pathname, mode="w") as file:
                file.writelines(content)
        except OSError as err:
            msg = "OS error: {}"
            _logger.error(msg.format(str(err)))
            result = False
        else:
            self.installer = pathname
            msg = "Installer downloaded: '{}'".format(self.installer)
            _logger.info(msg)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def is_update(self, product):
        """
        Return if this instance is an update.

        This method compare the version of the two product, and return the
        comparison result. The version numbers used by the editor are compliant
        with the semantic versioning specification 2.0.0 (see `support.semver`
        module)

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: `True` if this instance is an update of the product specified
            by the `product` parameter.
        """
        msg = ">>> (product={})"
        _logger.debug(msg.format(product))
        result = bool(semver.SemVer(self.version) >
                      semver.SemVer(product.version))
        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class MockHandler(BaseMockHandler):
    """
    Mocking handler.

    This concrete class implements a mocking handler used to test the 
    `lapptrack` module or any python module using the `cots` package. Most of 
    information about handler mechanism are in the :mod:`cots.core` and more 
    particularly in the `BaseProduct` class documentation.
    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        super().__init__()
        self.name = "Mocker"
        msg = "<<< ()=None"
        _logger.debug(msg)


class BrotherMockHandler(BaseMockHandler):
    """
    Mocking handler.

    This concrete class implements a mocking handler (similar to `MockHandler`)
    used to test the `lapptrack` module or any python module using the `cots`
    package.
    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        super().__init__()
        self.name = "Brother Mocker"
        msg = "<<< ()=None"
        _logger.debug(msg)

    def get_origin(self, version=None):
        """
        Get the mocking information.

        Args:
            version (str): The version of the reference product.

        Returns:
            bool: always True.
        """
        msg = ">>> (version={})"
        _logger.debug(msg.format(version))

        result = super().get_origin(version)
        self.file_size = 0
        self.secure_hash = None

        msg = "Latest product information fetched ({} published on {})"
        _logger.info(msg.format(self.version, self.published))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class ReleaseOftenMockHandler(BaseMockHandler):
    """
    Release Often mocking handler.

    This concrete class implements a mocking handler used to test the
    `lapptrack` module or any python module using the `cots` package. This
    handler notifies that a new version is available.
    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        super().__init__()
        self.name = "Release Often Mocker"
        msg = "<<< ()=None"
        _logger.debug(msg)

    def get_origin(self, version=None):
        """
        Get the mocking information.

        This method return always `True` to indicate that the most-update
        information are available. On each call, the version patch number is
        incremented to be compliant with the `semantic versioning
        specification`_ 2.0.0.

        Args:
            version (str): The version of the reference product.

        Returns:
            bool: always True.
        """
        msg = ">>> (version={})"
        _logger.debug(msg.format(version))

        result = super().get_origin(version)
        if version is None:
            self.version = "1.0.0"
        else:
            patch = 0
            if version:
                patch = 1 + int(version.split(".")[2])
            self.version = "1.0.{}".format(patch)
            self.display_name = "{} v{}".format(self.name, self.version)
            self.published = "2017-01-01T18:00:00"
            self.file_size = 156
            self.secure_hash = ("sha1",
                                "0b148ea595fb66a91b70b74893062d78341c0000")

        msg = "Latest product information fetched ({} published on {})"
        _logger.info(msg.format(self.version, self.published))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class FailureMockHandler(BaseMockHandler):
    """
    Failure mocking handler.

    This concrete class implements a mocking handler used to test the
    `lapptrack` module or any python module using the `cots` package. This
    handler always return an error on the `fetch` or `get_origin` method call.
    In this context, `is_update` method should not be called so his call raise
    an `RuntimeError` exception.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `fetch`                              `is_update`
        `get_origin`
        ===================================  ===================================
    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        super().__init__()
        self.name = "FailureMocker"
        msg = "<<< ()=None"
        _logger.debug(msg)

    def get_origin(self, version=None):
        """
        Get the mocking information.

        This method always return `False` to indicate that an error has occurred
        while the fetching of the product information.

        Args:
            version (str): The version of the reference product.

        Returns:
            bool: always False.
        """
        msg = ">>> (version={})"
        _logger.debug(msg.format(version))

        msg = "Inaccessible resource: ERROR 403 - url: {}"
        _logger.error(msg.format(self.location))
        result = False

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def fetch(self, dirpath):
        """
        Download the mocking installer.

        This method always return `False` to indicate that an error has occurred
        while the product installer fetching.

        Args:
            dirpath (str): The directory path name where to store the installer
                package.

        Returns:
            bool: `True` if the download of the file went well. In case of
            failure, the members are not modified and an error log is written.

        Returns:
            bool: always False.
        """
        msg = ">>> (dirpath={})"
        _logger.debug(msg.format(dirpath))

        msg = "Inaccessible resource: ERROR 403 - url: {}"
        _logger.error(msg.format(self.location))
        result = False

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def is_update(self, product):
        """
        Return if this instance is an update.

        In this context, this method should not be called.

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Raises:
            `RuntimeError`: see above.
        """
        # Execute the additional statement in the context of the current method.
        msg = ">>> (product={})"
        _logger.debug(msg.format(product))
        msg = "In this context, this method should not be called."
        raise RuntimeError(msg)


class ErrorMockHandler(BaseMockHandler):
    """
    Error mocking handler.

    This concrete class implements a mocking handler used to test the 
    `lapptrack` module or any python module using the `cots` package. This 
    handler raises an `TypeError` exception on the `fetch` or `get_origin`
    method call. In this context, `is_update` method should not be called so
    his call raise an `RuntimeError` exception.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `fetch`                              `is_update`
        `get_origin`
        ===================================  ===================================
    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        super().__init__()

        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "ErrorMocker"

        msg = "<<< ()=None"
        _logger.debug(msg)

    def get_origin(self, version=None):
        """
        Get the mocking information.

        This method always raises an `TypeError` exception.

        Args:
            version (str): The version of the reference product.

        Raises:
            `TypeError`: see above.
        """
        msg = ">>> (version={})"
        _logger.debug(msg.format(version))

        msg = "It is a fake error."
        raise TypeError(msg)

    def fetch(self, dirpath):
        """
        Download the mocking installer.

        This method always raises an `TypeError` exception.

        Args:
            dirpath (str): The path name where to store the installer package.

        Raises:
            `TypeError`: see above.
        """
        msg = ">>> (dirpath={})"
        _logger.debug(msg.format(dirpath))

        msg = "It is a fake error."
        raise TypeError(msg)

    def is_update(self, product):
        """
        Return if this instance is an update.

        In this context, this method should not be called.

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Raises:
            `RuntimeError`: see above.
        """
        msg = ">>> (product={})"
        _logger.debug(msg.format(product))
        msg = "In this context, this method should not be called."
        raise RuntimeError(msg)
