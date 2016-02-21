"""
COTS core module.

Classes
    BaseProduct: common base class for all products

Exception

Function
    retrieve_file: retrieve a URL into a url on disk
    retrieve_tempfile: retrieve a URL into a temporary url on disk
    get_summary_header: return the header summary.
    get_summary_tail: return the tail of the summary.

Constant

"""

import contextlib
import hashlib
import logging
import os
import tempfile
import urllib.request

from cots import progressbar

__all__ = [
    "BaseProduct"
]

PROD_TARGET_X86 = "x86"
PROD_TARGET_X64 = "x64"
PROD_TARGET_UNIFIED = "unified"

# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Error(Exception):
    """Base class for COTS Core exceptions."""
    def __init__(self, message=""):
        """
        Constructor.

        Parameters
            :param message: is the message explaining the reason of the
            exception raise.
        """
        self.message = message

    def __str__(self):
        return self.message


class UnexpectedContentLengthError(Error):
    """Raised when content length don't match."""
    def __init__(self, url, expected, received):
        """
        Constructor.

        Parameters
            :param url: is a string specifying the URL.
            :param expected: is a positive integer specifying the expected
            content length.
            :param received: is a positive integer specifying the received
            content length.
        """
        msg = "Unexpected content length: {0} received bytes vs. {1} " \
              "waited. \nUrl '{2}'."
        Error.__init__(self, msg.format(received, expected, url))
        self.expected = expected
        self.received = received
        self.url = url


class UnexpectedContentError(Error):
    """Raised when content secure hash don't match."""
    def __init__(self, url, algorithm, expected, computed):
        """
        Constructor.

        Parameters
            :param url: is a string specifying the URL.
            :param algorithm: is a string specifying the name of the secure hash
            algorithm.
            :param expected: is a string specifying the expected secure hash
            value in hexadecimal notation.
            :param computed: is a string specifying the computed secure hash
            value in hexadecimal notation.
        """
        msg = "Unexpected content secure hash: {0} computed bytes vs. {1} " \
              "waited. \nUrl '{2}'."
        Error.__init__(self, msg.format(computed, expected, url))
        self.algorithm = algorithm
        self.expected = expected
        self.computed = computed
        self.url = url


class UnexpectedContentTypeError(Error):
    """Raised when content-type don't match."""

    def __init__(self, url, expected, received):
        """
        Constructor.

        Parameters
            :param url: is a string specifying the URL.
            :param expected: is a string specifying the expected content-type.
            :param received: is a string specifying the received content-type.
        """
        msg = "Unexpected content type: '{0}' received vs. '{1}' waited. \n" \
              "Url '{2}'."
        Error.__init__(self, msg.format(received, expected, url))
        self.expected = expected
        self.received = received
        self.url = url


class BaseProduct:
    """
    Common base class for all products.

    Public instance variables
        name: is the name of the product (used in a_report mail and log file)
        display_name: is the name of the product as it appears in the 'Programs
        and Features' control panel
        version: is the current version of the product (string)
        published: is the date of the installer’s publication (ISO 8601 format)
        description: is a short description of the product (~250 characters)
        editor: is the name of the editor of the product
        url: is the url of the current version of the installer
        file_size: is the size of the product installer expressed in bytes
        secure_hash : is the secure_hash value of the product installer. 
        It's a tuple containing, in this order, the name of secure_hash 
        algorithm (see `hashlib.algorithms_guaranteed`) and the secure_hash 
        value in hexadecimal notation.
        icon: is the name of the icon file (in the same directory the installer)
        target: is the target architecture type (the Windows’ one) for the
          product. This argument must be one of the following values:
          'x86', 'x64' or 'unified'.
          x86: the application works only on 32 bits architecture
          x64: the application works only on 64 bits architecture
          unified: the application or the installation program work on both
           architectures
        release_note: is the release note’s URL for the current version of the
        product
        installer: filename of the installer (local full path)
        std_inst_args: arguments to use to for a standard installation.
        silent_inst_args: arguments to use for a silent installation.

    Public methods
        load: load a product class
        dump: dump a product class
        get_origin: get product information from the remote repository
        fetch : download the product installer
        is_update: return if this instance is an update of product

    Subclass API variables (i.e. may be use by subclass)
        _catalog_url: url of the product catalog.

    Subclass API Methods (i.e. must be overwritten by subclass)
        _parse_catalog: parse the catalog
        _get_name: extract the name of the product
        _get_display_name: extract the name of the product as it appears in
         the 'Programs and Features' control panel.
        _get_version: extract the current version of the product
        _get_published: Extract the date of the installer’s publication
        _get_description: extract the short description of the product
        _get_editor: extract the name of the editor of the product
        _get_url: Extract the url of the current version of the installer
        _get_file_size: extract the size of the product installer
        _get_hash: extract the secure_hash value of the product installer
        _get_icon: Extract the name of the icon file
        _get_target: Extract the target architecture type
        _get_release_note: extract the release note’s URL
        _get_std_inst_args: extract the arguments to use for a standard
         installation
        _get_silent_inst_args: extract the arguments to use for a silent
         installation.
    """
    def __init__(self):
        """
        Constructor.

        Parameters
            None
        """
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

        Parameters
            :param attributes: is a dictionary object containing the instance
            variables values. If attributes is not present or have the None
            value, instance variables keep to their default values.
            Key value pairs which don't exist in the instance variables
            dictionary are ignored.
        """
        # check parameters type
        if attributes is not None:
            if not isinstance(attributes, dict):
                msg = "props argument must be a class 'dict'. not {0}"
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

        Parameters
            None

        Return
            :return: a dictionary object containing a copy of the instance
            variables values.
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

        Parameters
            :param version: is the version of the reference product (i.e. the
            deployed product). It'a string following the editor rule.

        Exceptions
            exception raised by the `parse` method.
            exception raised by the `retrieve_tempfile` function.
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

        Parameters
            :param path: is the path name where to store the installer package.

        Exceptions
            exception raised by the `_file_retrieve` method.
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
        comparison result. The version numbers used by the editor are compliant
        with the semantic versioning specification 2.0.0 (see `semver`module)

        Parameters
            :param product: is the reference product (i.e. the deployed product)

        Returns
            :return: true if this instance is an update of the product specified
            by the `product` parameter.
        """
        raise NotImplementedError

    def _rename_installer(self, filename):
        """
        Rename the installer executable.

        Installer name match the following format:
        <name>_<version>.<extension>
        name: is the name of the product
        version: is the version of the product
        extension: is the original extension of the download resource.

        Parameters
            :param filename: is a string specifying the local name of the
            installer executable.

        Exceptions
            TypeError: Raised a parameter have an inappropriate type.
            The others exception are the same as for `os.replace`.

        Return
            None.
        """
        # check parameters type
        if not isinstance(filename, str):
            msg = "url argument must be a class 'str'. not {0}"
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
        `_get_...` call.

        Parameters
            :param filename: is a string specifying the local name of the
            downloaded product catalog.
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

    Parameters
        :param url: is a string specifying the URL.
        :param content_type: is a string specifying the mime type of the
        retrieved catalog. If the received type is different, a
        UnexpectedContentTypeError is raised.
        :param content_length: is the expected length of the retrieved file
        expressed in bytes. -1 means that the expected length is unknown.
        :param content_hash : is the expected secure hash value of the
        retrieved file.
        It's a tuple containing, in this order, the name of secure hash
        algorithm (see `hashlib.algorithms_guaranteed`) and the secure hash
        value in hexadecimal notation. If the secure hash algorithm is not
        supported, it will be ignored.

    Exceptions
        TypeError: Raised a parameter have an inappropriate type.
        UnexpectedContentTypeError: Raised when downloaded content-type
        don't match.
        UnexpectedContentLengthError: Raised when content length don't match.
        UnexpectedContentError: raised when content secure hash don't match.
        The others exception are the same as for `urllib.request.urlopen()`.

    Return
        :return: a string specifying the local file name.
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
    Retrieve a URL into a url on disk.

    The filename is the same as the name of the retrieved resource.

    Parameters  The catalog is
        :param url: is a string specifying the URL of the catalog.
        :param dir_name: is a string specifying the directory url on
          the disk where the retrieved is going to be written.
        :param content_type: is a string specifying the mime type of the
        retrieved catalog. If the received type is different, a
        UnexpectedContentTypeError is raised.
        :param content_length: is the expected length of the retrieved file
        expressed in bytes. -1 means that the expected length is unknown.
        :param content_hash : is the expected secure hash value of the
        retrieved file.
        It's a tuple containing, in this order, the name of secure hash
        algorithm (see `hashlib.algorithms_guaranteed`) and the secure hash
        value in hexadecimal notation. If the secure hash algorithm is not
        supported, it will be ignored.

    Exceptions
        TypeError: Raised a parameter have an inappropriate type.
        UnexpectedContentTypeError: Raised when downloaded content-type
        don't match.
        UnexpectedContentLengthError: Raised when content length don't match.
        UnexpectedContentError: raised when content secure hash don't match.
        The others exception are the same as for `urllib.request.urlopen()`.

    Return
        :return: a string specifying the local file name.
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

    # TODO : treat the exception for os.makedirs
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

    Parameters  The catalog is
        :param url: is a string specifying the URL of the catalog.
        :param file: is a file-like object to use to store the retrieved data.
        :param content_type: is a string specifying the mime type of the
        retrieved catalog. If the received type is different, a
        UnexpectedContentTypeError is raised.
        :param content_length: is the expected length of the retrieved file
        expressed in bytes. -1 means that the expected length is unknown.
        :param content_hash : is the expected secure hash value of the
        retrieved file.
        It's a tuple containing, in this order, the name of secure hash
        algorithm (see `hashlib.algorithms_guaranteed`) and the secure hash
        value in hexadecimal notation. If the secure hash algorithm is not
        supported, it will be ignored.

    Exceptions
        TypeError: Raised a parameter have an inappropriate type.
        UnexpectedContentTypeError: Raised when downloaded content-type
        don't match.
        UnexpectedContentLengthError: Raised when content length don't match.
        UnexpectedContentError: raised when content secure hash don't match.
        The others exception are the same as for `urllib.request.urlopen()`.

    Return
        None
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

    with contextlib.closing(urllib.request.urlopen(url)) as stream:
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
