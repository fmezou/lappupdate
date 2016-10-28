"""
This module defines core functions and classes for product handlers.

All product handlers are derived classes from `BaseProduct` class.


Public Classes
--------------
This module has only one public class.

===================================  ===================================
`BaseProduct`                        ..
===================================  ===================================


Public Functions
----------------
This module has a number of functions listed below in alphabetical order.

===================================  ===================================
`retrieve_file`                      `retrieve_tempfile`
===================================  ===================================


Public Exceptions
-----------------
This module has has a number of exceptions listed below in alphabetical order.

===================================  ===================================
`UnexpectedContentError`             `UnexpectedContentLengthError`
`UnexpectedContentTypeError`         ..
===================================  ===================================

.. _Uninstall Registry Key: https://msdn.microsoft.com/library/windows/desktop/
    aa372105%28v=vs.85%29.aspx
"""

import contextlib
import hashlib
import logging
import os
import tempfile
import urllib.request

from support import progressbar

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "BaseProduct",
    "retrieve_file",
    "retrieve_tempfile",
    "UnexpectedContentLengthError",
    "UnexpectedContentError",
    "UnexpectedContentTypeError"
]

# Target architecture supported (see `BaseProduct.target` attribute)
TARGET_X86 = "x86"
"""The application works only on 32 bits architecture."""

TARGET_X64 = "x64"
"""The application works only on 64 bits architecture."""

TARGET_UNIFIED = "unified"
"""The application or the installation program work on both architectures."""


# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Error(Exception):
    """
    Base class for COTS Core exceptions.

    Args:
        message (str, optional): Human readable string describing the exception.

    Attributes:
        message (str): Human readable string describing the exception.
    """
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return self.message


class UnexpectedContentLengthError(Error):
    """
    Raised when the content length don't match.

    Args:
        url (str): The URL of the fetched file.
        expected (int): The expected content length. Must be positive.
        received (int): The received content length. Must be positive.

    Attributes:
        url (str): The URL of the fetched file.
        expected (int): The expected content length. Must be positive.
        received (int): The received content length. Must be positive.
    """
    def __init__(self, url, expected, received):
        msg = "Unexpected content length: {0} received bytes vs. {1} " \
              "waited. \nUrl '{2}'."
        Error.__init__(self, msg.format(received, expected, url))
        self.expected = expected
        self.received = received
        self.url = url


class UnexpectedContentError(Error):
    """
    Raised when the content secure hash don't match.

    Args:
        url (str): The URL of the fetched file.
        algorithm (str): The name of the secure hash algorithm.
        expected (str): The expected secure hash value in hexadecimal notation.
        computed (str): The computed secure hash value in hexadecimal notation.

    Attributes:
        url (str): The URL of the fetched file.
        algorithm (str): The name of the secure hash algorithm.
        expected (str): The expected secure hash value in hexadecimal notation.
        computed (str): The computed secure hash value in hexadecimal notation.
    """
    def __init__(self, url, algorithm, expected, computed):
        msg = "Unexpected content secure hash: {0} computed bytes vs. {1} " \
              "waited. \nUrl '{2}'."
        Error.__init__(self, msg.format(computed, expected, url))
        self.algorithm = algorithm
        self.expected = expected
        self.computed = computed
        self.url = url


class UnexpectedContentTypeError(Error):
    """
    Raised when the content-type don't match.

    Args:
        url (str): The URL of the fetched file.
        expected (str): The expected content type.
        received (str): The received content length.

    Attributes:
        url (str): The URL of the fetched file.
        expected (str): The expected content type.
        received (str): The received content type.
    """

    def __init__(self, url, expected, received):
        msg = "Unexpected content type: '{0}' received vs. '{1}' waited. \n" \
              "Url '{2}'."
        Error.__init__(self, msg.format(received, expected, url))
        self.expected = expected
        self.received = received
        self.url = url


class BaseProduct:
    """
    Common base class for all product handlers.


    Attributes:
        name (str): The name of the product (used in a_report mail and log
            file).
        display_name (str): The name of the product as it appears in the
            'Programs and Features' control panel (see
            `Uninstall Registry Key`_).
        version (str): The current version of the product using the editor
            versioning rules.
        published (str): The date of the installer’s publication expressed in
            the :rfc:`3339` format.
        target (str): The target architecture type (the Windows’ one) for the
            product. This argument must be one of the following values:
            `TARGET_X86`, `TARGET_X64` or `TARGET_UNIFIED`.
        description (str): Short description of the product (~250 characters).
        editor (str): The name of the editor of the product.
        web_site_location (str): The location of the editor ou product web site.
        location (str): The location of the current version of the installer.
        icon (str): The name of the icon file (in the same directory than the
            installer)
        announce_location (str): The location of the page announcing the product
            releases.
        feed_location (str): The location of the RSS feed announcing the product
            releases.
        release_note_location (str): The location of the release note for the
            detailed history change of the product.
        change_summary (str): The changelog of the product since the deployed
            product.
        installer (str): The filename of the installer (local full path).
        file_size (int): The size of the product installer expressed in bytes.
        secure_hash (2-tuple): The secure_hash value of the product installer.
            It's a 2-tuple containing, in this order, the name of secure_hash
            algorithm (see `hashlib.algorithms_guaranteed`) and the secure_hash
            value in hexadecimal notation.
        std_inst_args (str): Arguments to use with the installer for a standard
            installation.
        silent_inst_args (str): Arguments to use with the installer for a silent
            installation (i.e. without any user's interaction, typically while
            an automated deployment using ``appdeploy`` script).


    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `dump`                               `get_origin`
        `fetch`                              `is_update`
        `load`                               ..
        ===================================  ===================================


    **Methods to Override**
        This class is a base class, so a number of public methods must be
        overridden. They are listed below in alphabetical order.

        ===================================  ===================================
        `get_origin`                         `is_update`
        ===================================  ===================================


    **Using BaseProduct...**
        This class is the base class for product handler used by
        `appdownload.AppDownload` and this one only use the public methods.

        After created a class instance, the `get_origin` method populate the
        attributes with the most up-to-date information from the editor's
        site. An alternative way, is to call the `load` method to populate
        attributes with a set of data previously saved on disk.

        Then calling `fetch` method retrieves the current version (i.e. the one
        described in the attributes) of the installer and store it on the local
        disk.

        Then you can save the updated instances by calling the `dump` method.
    """
    def __init__(self):
        self.name = ""
        self.display_name = ""
        self.version = ""
        self.published = ""
        self.target = TARGET_UNIFIED
        self.description = ""
        self.editor = ""
        self.web_site_location = ""
        self.location = ""
        self.icon = ""
        self.announce_location = ""
        self.feed_location = ""
        self.release_note_location = ""
        self.change_summary = ""
        self.installer = ""
        self.file_size = -1
        self.secure_hash = None
        self.std_inst_args = ""
        self.silent_inst_args = ""

        self._catalog_url = ""

        msg = "Instance of {} created."
        _logger.debug(msg.format(self.__class__))

    def load(self, attributes=None):
        """
        Load a product class.

        Args:
            attributes (dict): The instance variables values to set. Previous
                value of the instance variables kept if this argument value is
                None. The key value pairs which don't exist in the
                instance variables dictionary are ignored.

        Raises:
            TypeError: Parameters type mismatch.
        """
        # check parameters type
        if attributes is not None:
            if not isinstance(attributes, dict):
                msg = "attributes argument must be a class 'dict'. not {0}"
                msg = msg.format(attributes.__class__)
                raise TypeError(msg)

        # set instance variables
        _logger.info("Load the product.")
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue  # non-public instance variables are ignored
            else:
                if attributes[k] is not None:
                    self.__dict__[k] = attributes[k]
                    msg = "Instance variables '{0}' : '{1}' -> '{2}'"
                    _logger.debug(msg.format(k, v, attributes[k]))

    def dump(self):
        """
        Dump a product class.

        Returns:
            dict: Contain a copy of the instance variables values.
        """
        attributes = {}
        _logger.info("Dump the product.")
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue  # non-public instance variables are ignored
            else:
                attributes[k] = v
        return attributes

    def get_origin(self, version=None):
        """
        Get product information from the remote repository.

        The latest catalog of the product is downloaded and parsed.

        Args:
            version (str): The version of the reference product (i.e. the
                deployed product). It'a string following the editor versioning
                rules.

        Raises:
            TypeError: Parameters type mismatch.
        """
        raise NotImplementedError

    def fetch(self, path):
        """
        Download the product installer.

        Args:
            path (str): The path name where to store the installer package.

        Raises:
            TypeError: Parameters type mismatch.
            UnexpectedContentLengthError: The content length don't match.
            UnexpectedContentError: The content secure hash don't match.
            Same as `urllib.request.urlopen`.
        """
        msg = "Downloads the latest version of the installer."
        _logger.debug(msg)

        # Update the update object
        local_filename = retrieve_file(self.location, path,
                                       content_length=self.file_size,
                                       content_hash=self.secure_hash)
        self._rename_installer(local_filename)
        msg = "Update downloaded in '{}'".format(self.installer)
        _logger.debug(msg)

    def is_update(self, product):
        """
        Return if this instance is an update of product

        This method compare the version of the two product, and return the
        comparison result.

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: True if this instance is an update of the product specified
                by the `product` parameter.
        """
        raise NotImplementedError

    def _rename_installer(self, filename):
        """
        Rename the installer executable.

        Installer name match the following format:
        ``<name>_<version>.<extension>``

        where

        * ``name``: is the name of the product
        * ``version``: is the version of the product
        * ``extension``: is the original extension of the download resource.


        Args:
            filename (str): The local name of the installer executable.

        Raises:
            TypeError: Parameters type mismatch.
            The others exception are the same as `os.replace`.
        """
        # check parameters type
        if not isinstance(filename, str):
            msg = "filename argument must be a class 'str'. not {0}"
            msg = msg.format(filename.__class__)
            raise TypeError(msg)

        # Compute the destination name and replace it
        basename = os.path.dirname(filename)
        ext = os.path.splitext(filename)[1]
        dest = "{}_{}{}".format(self.name, self.version, ext)
        self.installer = os.path.normpath(os.path.join(basename, dest))
        os.replace(filename, self.installer)


def retrieve_tempfile(url,
                      content_type=None, content_length=-1, content_hash=None):
    """
    Retrieve a URL into a temporary url on disk.

    Args:
        url (str): The URL of the file to retrieve.
        content_type (str, optional): The mime type of the retrieved file. No
            check will be done if the value is None.
        content_length (int, optional): The expected length of the retrieved
            file expressed in bytes. -1 means that the expected length is
            unknown.
        content_hash (2-tuple): The expected secure hash value of the
            retrieved file. No check will be done if the value is None. It's a
            tuple containing, in this order, the name of secure hash algorithm
            (see `hashlib.algorithms_guaranteed`) and the secure hash value in
            hexadecimal notation. If the secure hash algorithm is not supported,
            it will be ignored.

    Returns:
        str: a string specifying the local file name.

    Raises:
        TypeError: Parameters type mismatch.
        UnexpectedContentTypeError: The downloaded content-type don't match.
        UnexpectedContentLengthError: The content length don't match.
        UnexpectedContentError: the content secure hash don't match.
        Same as `urllib.request.urlopen`.
    """
    # check parameters type
    if not isinstance(url, str):
        msg = "url argument must be a class 'str'. not {0}"
        msg = msg.format(url.__class__)
        raise TypeError(msg)

    # default value
    filename = ""

    with tempfile.NamedTemporaryFile(delete=False) as file:
        filename = file.name
        _retrieve_file(url, file, content_type, content_length, content_hash)

    return filename


def retrieve_file(url, dir_name,
                  content_type=None, content_length=-1, content_hash=None):
    """
    Retrieve a URL into a file on disk.

    The filename is the same as the name of the retrieved resource.

    Args:
        url (str): The URL of the file to retrieve.
        dir_name (str): The pathname of the directory where the retrieved file
            is going to be written.
        content_type (str, optional): The mime type of the retrieved file. No
            check will be done if the value is None.
        content_length (int, optional): The expected length of the retrieved
            file expressed in bytes. -1 means that the expected length is
            unknown.
        content_hash (2-tuple): The expected secure hash value of the
            retrieved file. No check will be done if the value is None. It's a
            tuple containing, in this order, the name of secure hash algorithm
            (see `hashlib.algorithms_guaranteed`) and the secure hash value in
            hexadecimal notation. If the secure hash algorithm is not supported,
            it will be ignored.

    Returns:
        str: a string specifying the local file name.

    Raises:
        TypeError: Parameters type mismatch.
        UnexpectedContentTypeError: The downloaded content-type don't match.
        UnexpectedContentLengthError: The content length don't match.
        UnexpectedContentError: The content secure hash don't match.
        Same as `urllib.request.urlopen`.
    """
    # check parameters type
    if not isinstance(url, str):
        msg = "url argument must be a class 'str'. not {0}"
        msg = msg.format(url.__class__)
        raise TypeError(msg)
    if not isinstance(dir_name, str):
        msg = "dir_name argument must be a class 'str'. not {0}"
        msg = msg.format(dir_name.__class__)
        raise TypeError(msg)

    # default value
    filename = ""

    os.makedirs(dir_name, exist_ok=True)
    basename = os.path.basename(urllib.request.url2pathname(url))
    filename = os.path.join(dir_name, basename)
    part_filename = filename + ".partial"
    with open(part_filename, mode="wb") as file:
        _retrieve_file(url, file, content_type, content_length, content_hash)
    os.replace(part_filename, filename)  # rename with the real name

    return filename


def _retrieve_file(url, file,
                   content_type=None, content_length=-1, content_hash=None):
    """
    Retrieve a URL into a url on disk.


    Args:
        url (str): The URL of the file to retrieve.
        file (file-like object): A file-like object to use to store the
            retrieved data.
        content_type (str, optional): The mime type of the retrieved file. No
            check will be done if the value is None.
        content_length (int, optional): The expected length of the retrieved
            file expressed in bytes. -1 means that the expected length is
            unknown.
        content_hash (2-tuple): The expected secure hash value of the
            retrieved file. No check will be done if the value is None. It's a
            tuple containing, in this order, the name of secure hash algorithm
            (see `hashlib.algorithms_guaranteed`) and the secure hash value in
            hexadecimal notation. If the secure hash algorithm is not supported,
             it will be ignored.

    Raises:
        TypeError: Parameters type mismatch.
        UnexpectedContentTypeError: The downloaded content-type don't match.
        UnexpectedContentLengthError: The content length don't match.
        UnexpectedContentError: The content secure hash don't match.
        Same as `urllib.request.urlopen`.
    """
    # check parameters type
    if not isinstance(url, str):
        msg = "url argument must be a class 'str'. not {0}"
        msg = msg.format(url.__class__)
        raise TypeError(msg)
    if content_type is not None:
        if not isinstance(content_type, str):
            msg = "content_type argument must be a class 'str'. not {0}"
            msg = msg.format(content_type.__class__)
            raise TypeError(msg)
    if not isinstance(content_length, int):
        msg = "content_length argument must be a class 'int'. not {0}"
        msg = msg.format(content_length.__class__)
        raise TypeError(msg)
    if content_hash is not None:
        if not isinstance(content_hash, tuple):
            msg = "content_hash argument must be a class 'tuple'. not {0}"
            msg = msg.format(content_hash.__class__)
            raise TypeError(msg)
        if content_hash[0] not in hashlib.algorithms_available:
            msg = "Hash algorithm {} is not supported. Hash control " \
                  "will be ignored."
            _logger.warning(msg.format(content_hash[0]))
            content_hash = None  # Deactivate the secure hash control

    # retrieve the resource
    msg = "Retrieve '{}'"
    _logger.debug(msg.format(url))

    # some web servers refuse to deliver pages when the user-agent is set to
    # 'Python-urllib'. So the user-agent is set to the name of the project.
    headers = {"User-Agent": "lAppUpdate/0.1"}
    request = urllib.request.Request(url, headers=headers)
    with contextlib.closing(urllib.request.urlopen(request)) as stream:
        headers = stream.info()
        # Check the expected content
        if "Content-Type" in headers and content_type is not None:
            if headers["Content-Type"] != content_type:
                raise UnexpectedContentTypeError(url, content_type,
                                                 headers["Content-Type"])

        if "Content-Length" in headers:
            length = int(headers["Content-Length"])
            if content_length == -1:
                content_length = length
            else:
                if length != content_length:
                    raise UnexpectedContentLengthError(url,
                                                       content_length,
                                                       length)

        msg = "Retrieve '{}' in '{}'"
        _logger.debug(msg.format(url, file.name))

        length = 0
        secure_hash = None
        if content_hash is not None:
            secure_hash = hashlib.new(content_hash[0])

        progress_bar = progressbar.TextProgressBar(content_length)
        progress_bar.compute(length, content_length)

        while True:
            data = stream.read(4096)
            if not data:
                break
            length += len(data)
            file.write(data)
            if secure_hash is not None:
                secure_hash.update(data)
            progress_bar.compute(length, content_length)

        msg = "'{}' retrieved - ".format(url)
        msg += progress_bar.finish()
        _logger.debug(msg)

        # Content checking
        if content_length >= 0 and length < content_length:
            raise UnexpectedContentLengthError(url, content_length, length)
        if secure_hash is not None and secure_hash.hexdigest() != \
                content_hash[1]:
            raise UnexpectedContentError(url,
                                         content_hash[0],
                                         content_hash[1],
                                         secure_hash.hexdigest())
