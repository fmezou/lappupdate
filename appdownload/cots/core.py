"""
This module defines core functions and classes for product handlers.

All product handlers are derived classes from `BaseProduct` class.


Public Classes
==============
This module has only one public class.

===================================  ===================================
`BaseProduct`                        ..
===================================  ===================================


Public Functions
================
This module has a number of functions listed below in alphabetical order.

===================================  ===================================
`retrieve_file`                      `retrieve_tempfile`
===================================  ===================================


Public Exceptions
=================
This module has has a number of exceptions listed below in alphabetical order.

===================================  ===================================
`UnexpectedContentError`             `UnexpectedContentLengthError`
`UnexpectedContentTypeError`         ..
===================================  ===================================
"""

import contextlib
import hashlib
import logging
import os
import tempfile
import urllib.request

from cots import progressbar

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
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

PROD_TARGET_X86 = "x86"
PROD_TARGET_X64 = "x64"
PROD_TARGET_UNIFIED = "unified"


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
        name (str): The name of the product (used in a_report mail and log file)
        display_name (str): The name of the product as it appears in the
            'Programs and Features' control panel.
        version (str): The current version of the product.
        published (str): The date of the installer’s publication using the ISO
            8601 format.
        description (str): Short description of the product (~250 characters).
        editor (str): The name of the editor of the product.
        url (str): The url of the current version of the installer.
        file_size (int): The size of the product installer expressed in bytes.
        secure_hash (2-tuple): The secure_hash value of the product installer.
            It's a 2-tuple containing, in this order, the name of secure_hash
            algorithm (see `hashlib.algorithms_guaranteed`) and the secure_hash
            value in hexadecimal notation.
        icon (str): The name of the icon file (in the same directory than the
            installer)
        target (str): The target architecture type (the Windows’ one) for the
            product. This argument must be one of the following values:
            'x86', 'x64' or 'unified'.

            * x86: the application works only on 32 bits architecture.
            * x64: the application works only on 64 bits architecture.
            * unified: the application or the installation program work on both
                architectures.

        release_note (str): The release note’s URL for the current version of
            the product.
        installer (str): The filename of the installer (local full path).
        std_inst_args (str): Arguments to use with the installer for a standard
            installation.
        silent_inst_args (str): Arguments to use with the installer for a silent
            installation.


    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `dump`                               `get_origin`
        `fetch`                              `load`
        ===================================  ===================================


    **Methods to Override**
        This class is a base class, so a number of public methods must be
        overridden. They are listed below in alphabetical order.

        ===================================  ===================================
        `_get_description`                   `_get_release_note`
        `_get_display_name`                  `_get_silent_inst_args`
        `_get_editor`                        `_get_std_inst_args`
        `_get_file_size`                     `_get_target`
        `_get_hash`                          `_get_url`
        `_get_icon`                          `_get_version`
        `_get_name`                          `_parse_catalog`
        `_get_published`                     `is_update`
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
        self.description = ""
        self.editor = ""
        self.url = ""
        self.file_size = -1
        self.secure_hash = None
        self.icon = ""
        self.target = ""
        self.release_note = ""
        self.installer = ""
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
                attr = attributes.get(k)
                if attr is not None:
                    self.__dict__[k] = attributes.get(k)
                    msg = "Instance variables '{0}' : '{1}' -> '{2}'"
                    _logger.debug(msg.format(k, v, attr))

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
        # check parameters type
        if version is not None and not isinstance(version, str):
            msg = "version argument must be a class 'str' or None. not {0}"
            msg = msg.format(version.__class__)
            raise TypeError(msg)

        msg = "Get the latest product information. Current version is '{0}'"
        _logger.debug(msg.format(self.version))

        local_filename = retrieve_tempfile(self._catalog_url)
        msg = "Catalog downloaded: '{0}'".format(local_filename)
        _logger.debug(msg)

        # Parse the catalog and retrieve information
        self._parse_catalog(local_filename)
        self._get_name()
        self._get_version()
        self._get_display_name()
        self._get_published()
        self._get_description()
        self._get_editor()
        self._get_url()
        self._get_file_size()
        self._get_hash()
        self._get_icon()
        self._get_target()
        self._get_release_note()
        self._get_std_inst_args()
        self._get_silent_inst_args()

        # clean up the temporary files
        os.unlink(local_filename)

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
        local_filename = retrieve_file(self.url, path,
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

    def _parse_catalog(self, filename):
        """
        Parse the catalog.

        This method parses the downloaded product catalog to prepare
        ``_get_...`` methods call.

        Parameters
            filename (str): The local name of the downloaded product catalog.
         """
        raise NotImplementedError

    def _get_name(self):
        """
        Extract the name of the product (used in a_report mail and log file).

        This method fixes the `name` attribute with a hardcoded value or an
        extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_display_name(self):
        """
        Extract the name of the product as it appears in the 'Programs and
        Features' control panel.

        This method fixes the `display_name` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_version(self):
        """
        Extract the current version of the product.

        This method fixes the `version` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_published(self):
        """
        Extract the date of the installer’s publication (ISO 8601 format).

        This method fixes the `published` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_description(self):
        """
        Extract the short description of the product (~250 characters).

        This method fixes the `description` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_editor(self):
        """
        Extract the name of the editor of the product.

        This method fixes the `editor` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_url(self):
        """
        Extract the url of the current version of the installer

        This method fixes the `url` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_file_size(self):
        """
        Extract the size of the product installer expressed in bytes

        This method fixes the `file_size` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_hash(self):
        """
        Extract the secure_hash value of the product installer (tuple).

        This method fixes the `secure_hash` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_icon(self):
        """
        Extract the name of the icon file.

        This method fixes the `secure_hash` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_target(self):
        """
        Extract the target architecture type (the Windows’ one).

        This method fixes the `target` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_release_note(self):
        """
        Extract the release note’s URL.

        This method fixes the `release_note` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_std_inst_args(self):
        """
        Extract the arguments to use for a standard installation.

        This method fixes the `std_inst_args` attribute with a hardcoded value
        or an extracted value from the remote product catalog.
        """
        raise NotImplementedError

    def _get_silent_inst_args(self):
        """
        Extract the arguments to use for a silent installation.

        This method fixes the `silent_inst_args` attribute with a hardcoded
        value or an extracted value from the remote product catalog.
        """
        raise NotImplementedError


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
        msg = msg + progress_bar.finish()
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
