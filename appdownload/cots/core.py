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
import re
import tempfile
import urllib.request
import email.mime.multipart
import email.mime.text
import email.utils
import mimetypes
import socket
import smtplib

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
        name: is the name of the product (used in report mail and log file)
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
        Extract the name of the product (used in report mail and log file).

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


class Report:
    """
    Make a report activity and publish it with the registered handler.

    The report is based on a template using named keyword argument and composed
    of named sections.

    The use of the named keyword argument is based on the [string module]
    (https://docs.python.org/3/library/string.html#format-string-syntax).
    These named keyword are the ones returned by the `dump` method of the
    product class instance.

    Each section starts with a HTML comment and it ends with the start of
    next section or the end of the file. The comment match the following format
    and must be on one line:
    <!-- $lau:<name>$ -->
    `name` MUST comprise only ASCII alphanumerics and hyphen [0-9A-Za-z-] and
     MUST NOT be empty.

     If a named section is not declared in `Report.names`, its contents is added
     to the current section (i.e. no section is created).

    The 'summary.html' template is used by default.

    Public class variables
       names: is the list of the well-known named sections in a report template.

    Public instance variables
       ?name: is the name of the product (used in report mail and log file)

    Public methods
        add_section: add a section to the report.
        publish: publish the report with the registered handler
        (see `add_handler`).
        add_handler: add a handler to publish the report.

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None

    """
    names = [
        "Head",
        "HeaderStart",
        "Title",
        "HeaderEnd",
        "BodyStart",
        "TOCStart",
        "TOCEntry",
        "TOCEnd",
        "SummaryStart",
        "SummaryEntry",
        "SummaryEnd",
        "BodyEnd",
        "Tail"
    ]

    # Regular expression which match the section name in report templates.
    # Like the regular expression is fixed, it is compiled at the loading of the
    # module to improve the efficiency of the `Report` class method.
    _re = re.compile("^\s*<!--\s+\$lau:(?P<name>[0-9A-Za-z-]+)\$\s+-->$",
                     flags=0)
    _SUMMARY = os.path.join(os.path.dirname(__file__), "summary_tmpl.html")

    def __init__(self, template=_SUMMARY, separator=""):
        """
        Constructor

        Parameters
        :param template: is the full path name of the template file. The format
        of the template file is described below.
        :param separator: is the separator added at the end of each added
        section in the report.
        """
        # check parameters type
        if not isinstance(template, str):
            msg = "template argument must be a class 'str'. not {0}"
            msg = msg.format(template.__class__)
            raise TypeError(msg)

        if not isinstance(separator, str):
            msg = "separator argument must be a class 'str'. not {0}"
            msg = msg.format(separator.__class__)
            raise TypeError(msg)

        self._sections = []
        self._template = {}
        self._subtype = "plain"
        self._charset = "utf-8"
        self._handler = []
        self._separator = separator

        self._parse_template(template)

        msg = "Instance of {} created."
        _logger.debug(msg.format(self.__class__))

    def add_section(self, attributes):
        """
        Add a section to the report.

        Parameters
        :param attributes: is a dictionary containing the product attributes
        (typically the one returned by the `dump` method).
        """
        # check parameters type
        if not isinstance(attributes, dict):
            msg = "attributes argument must be a class 'dict'. not {0}"
            msg = msg.format(attributes.__class__)
            raise TypeError(msg)

        # make a copy of the attributes because a unique identifier is added
        section = attributes.copy()
        section["id"] = str(id(section))
        self._sections.append(section)

    def publish(self, attributes):
        """
        Publish the report with the registered handler

        :param attributes: is a dictionary containing the product attributes
        (typically the one returned by the `dump` method).
        """
        # Generate the report as a string
        report = ""
        report += self._template["Head"]
        report += self._template["HeaderStart"]
        report += self._template["Title"].format_map(attributes)
        report += self._template["HeaderEnd"]
        report += self._template["BodyStart"].format_map(attributes)

        report += self._template["TOCStart"]
        for section in self._sections:
            report += self._template["TOCEntry"].format_map(section)
            report += self._separator
        report += self._template["TOCEnd"]

        report += self._template["SummaryStart"]
        for section in self._sections:
            report += self._template["SummaryEntry"].format_map(section)
            report += self._separator
        report += self._template["SummaryEnd"]

        report += self._template["BodyEnd"].format_map(attributes)
        report += self._template["Tail"].format_map(attributes)

        # Publish it
        for handler in self._handler:
            handler.publish(attributes["title"], report,
                            self._subtype, self._charset)

    def add_handler(self, handler):
        """
        Add a handler to publish the report.

        :param handler: is a class instance derived from the `BaseHandler` base
        class.
        """
        # check parameters type
        if not isinstance(handler, BaseHandler):
            msg = "handler argument must be a class 'BaseHandler'. not {0}"
            msg = msg.format(handler.__class__)
            raise TypeError(msg)

        self._handler.append(handler)
        msg = "{} added."
        _logger.debug(msg.format(handler.__class__))

    def _parse_template(self, filename):
        """
        Parse the template to extract the report sections.

        :param filename: is the full path name of the template file.
        """
        # check parameters type
        if not isinstance(filename, str):
            msg = "format_string argument must be a class 'str'. not {0}"
            msg = msg.format(filename.__class__)
            raise TypeError(msg)

        # Guess the content type based on the template file's extension.
        # If the content type cannot be guessed, the template is considered as
        # text plain. A plain text template is considered as using the utf-8
        # charset.
        content_type, encoding = mimetypes.guess_type(filename)
        if content_type is not None:
            maintype, subtype = content_type.split("/", 1)
            if maintype != "text":
                msg = "The template must be a text-like format such as html"
                raise ValueError(msg)

            self._subtype=subtype
            if self._subtype == "html":
                self._charset=None
        else:
            msg = "The type of '{}' cannot be guessed. Considered as " \
                  "text/plain."
            _logger.warning(msg.format(os.path.basename(filename)))

        name = self.names[0]
        self._template[name] = ""
        with open(filename) as file:
            for line in file:
                match = self._re.match(line)
                if match is None:
                    self._template[name] += line
                    msg = "Add the following line to {} section : '{}'."
                    _logger.debug(msg.format(name, repr(line)))
                else:
                    if match.group("name") in self.names:
                        name = match.group("name")
                        self._template[name] = ""
                        msg = "Start a new section '{}'."
                        _logger.debug(msg.format(name))
                    else:
                        # The named section is not a well-known section,
                        # its content is simply added to the current section
                        msg = "'{}' is not a well-know section. Line ignored"
                        _logger.warning(msg.format(name))


class BaseHandler:
    """
    Base class for report publishing.

    Public instance variables
        ?name: is the name of the product (used in report mail and log file)

    Public methods
        publish: publish the report.

    Subclass API variables (i.e. may be use by subclass)
        ?_catalog_url: url of the product catalog.

    Subclass API Methods (i.e. must be overwritten by subclass)
        ?_parse_catalog: parse the catalog

    """
    def __init__(self):
        """
        Constructor

        """

        msg = "Instance of {} created."
        _logger.debug(msg.format(self.__class__))

    def publish(self, title, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param title: is a string specifying the subject of the email
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text).
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        raise NotImplementedError


class MailHandler(BaseHandler):
    """
    Send the report by mail.

    Public instance variables
        None

    Public methods
        publish: send the report.
    """
    def __init__(self, host, to_addresses, from_address=None, credentials=None):
        """Constructor

        Parameters
        :param host: is a string containing the full qualified name of the SMTP
        server host, or a tuple containing the full qualified name of the SMTP
        server and the port number to use.
        :param to_addresses: is a string or a list containing the mail addresses
        of the recipient.
        :param from_address: is a string containing the mail addresses of the
        sender. The default value is set to the local hostname. (see
        socket.getfqdn())
        :param credentials: is a tuple containing the username and the password
        to connect to SMTP server.

        Exception
            None
        """
        #
        # check parameters type
        if not isinstance(host, (str, tuple)):
            msg = "host argument must be a class 'str' or 'tuple'. not {0}"
            msg = msg.format(host.__class__)
            raise TypeError(msg)
        if not isinstance(to_addresses, (str, list)):
            msg = "to_addresses argument must be a class 'str' or 'list'. " \
                  "not {0}"
            msg = msg.format(to_addresses.__class__)
            raise TypeError(msg)
        if from_address is not None and not isinstance(from_address, str):
            msg = "from_address argument must be a class 'str'. not {0}"
            msg = msg.format(from_address.__class__)
            raise TypeError(msg)
        if credentials is not None and not isinstance(credentials, tuple):
            msg = "credentials argument must be a class 'tuple'. not {0}"
            msg = msg.format(from_address.__class__)
            raise TypeError(msg)

        # Initial values
        super().__init__()
        self._host = ""
        self._port = 0
        self._username = None
        self._password = None
        self._to_addresses = []
        self._from_address = ""

        if isinstance(host, tuple):
            self._host, self._port = host
        else:
            self._host = host
        if isinstance(to_addresses, list):
            self._to_addresses = to_addresses
        else:
            self._to_addresses = [to_addresses]
        if from_address is not None:
            self._from_address = from_address
        else:
            self._from_address = socket.getfqdn()
        if credentials is not None:
            self._username, self._password = credentials

    def publish(self, title, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param title: is a string specifying the subject of the email
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text). By default, the report is an HTML encoded one.
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        # check parameters type
        if not isinstance(title, str):
            msg = "title argument must be a class 'str'. not {0}"
            msg = msg.format(title.__class__)
            raise TypeError(msg)
        if not isinstance(report, str):
            msg = "report argument must be a class 'str'. not {0}"
            msg = msg.format(report.__class__)
            raise TypeError(msg)
        if not isinstance(subtype, str):
            msg = "subtype argument must be a class 'str'. not {0}"
            msg = msg.format(subtype.__class__)
            raise TypeError(msg)
        if charset is not None and not isinstance(charset, str):
            msg = "charset argument must be a class 'str'. not {0}"
            msg = msg.format(charset.__class__)
            raise TypeError(msg)

        # Create the message container
        mail = email.mime.text.MIMEText(report, subtype, charset)
        mail["Subject"] = title
        mail["From"] = self._from_address
        mail["To"] = ", ".join(self._to_addresses)

        # Send the message
        with smtplib.SMTP(self._host, self._port) as handler:
            if self._username is not None:
                handler.login(self._username, self._password)
            handler.send_message(mail)

        # FIXME: make a local copy to test
        with open(title, mode="w") as file:
            file.write(mail.as_string())


class FileHandler(BaseHandler):
    """
    Write the report in file.

    Public instance variables
        ?

    Public methods
        publish: send the report.
    """
    def __init__(self, filename):
        """Constructor

        Parameters
            None

        Exception
            None
        """
        super().__init__()
        self._filename = filename

    def publish(self, title, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param title: is a string specifying the subject of the email
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text). By default, the report is an HTML encoded one.
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        with open(self._filename, mode="w") as file:
            file.write(report)


class StreamHandler(BaseHandler):
    """
    Write the report in file.

    Public instance variables
        ?

    Public methods
        publish: send the report.
    """
    def __init__(self):
        """Constructor

        Parameters
            None

        Exception
            None
        """
        super().__init__()

    def publish(self, title, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param title: is a string specifying the subject of the email
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text). By default, the report is an HTML encoded one.
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        print(report)


