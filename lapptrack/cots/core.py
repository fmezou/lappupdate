"""
This module defines core functions and classes for product handlers.

Product handlers are derived classes from `BaseProduct` class.


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
`get_handler`                        `retrieve_file`
`get_file_hash`                      ..
===================================  ===================================


Public Exceptions
-----------------
This module has has a number of exceptions listed below in alphabetical order.

===================================  ===================================
`ContentError`                       `ContentTypeError`
`ContentLengthError`                 ..
===================================  ===================================

"""

import contextlib
import hashlib
import logging
import os
import urllib.request
import urllib.parse
import urllib.error
import importlib

from support import progressbar

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "BaseProduct",
    "retrieve_file",
    "get_file_hash",
    "get_handler",
    "ContentLengthError",
    "ContentError",
    "ContentTypeError"
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
# docs.python.org/3/howto/logging.html# configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Error(Exception):
    """
    Base class for Core exceptions.

    Args:
        message (str): (optional) Human readable string describing the
            exception.

    Attributes:
        message (str): Human readable string describing the exception.
    """
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return self.message


class ContentLengthError(Error):
    """
    Raised when the content length does not match the expected length.

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
              "waited. Url '{2}'."
        Error.__init__(self, msg.format(received, expected, url))
        self.expected = expected
        self.received = received
        self.url = url


class ContentError(Error):
    """
    Raised when the content secure hash does not match the expected hash.

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
        msg = "Unexpected content secure hash: {0} computed vs. {1} waited. " \
              "Url '{2}'."
        Error.__init__(self, msg.format(computed, expected, url))
        self.algorithm = algorithm
        self.expected = expected
        self.computed = computed
        self.url = url


class ContentTypeError(Error):
    """
    Raised when the content-type does not match the expected type.

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
        msg = "Unexpected content type: '{0}' received vs. '{1}' waited. " \
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
            The "build target" of the application to retrieve. This part must
            contain one of the following values:

            * ``win``: Windows 32 bits
            * ``win64``: Windows 64 bits
            * ``osx``: MacOS X
            * ``linux64``: Linux x86 64 bits
            * ``linux``: Linux i686
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
            an automated deployment using ``lappdeploy`` script).


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
        `lapptrack.LAppTrack` and this one only use the public methods.

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
        msg = ">>> ()"
        _logger.debug(msg)

        self.name = ""
        self.display_name = ""
        self.version = "0.0.0"  # Match with the semantic versioning rules
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

        msg = "<<< ()=None"
        _logger.debug(msg)

    def __str__(self):
        """
        Return the printable string representation of object.

        Returns:
            str: a human readable string with the handler attributes.
        """
        l = list()
        l.append("Product attributes:")
        l.append("- General --------------------------------------------------")
        l.append("  Name:         {}".format(self.name))
        l.append("  Display name: {}".format(self.display_name))
        l.append("  Version:      {}".format(self.version))
        l.append("  Published:    {}".format(self.published))
        l.append("------------------------------------------------------------")
        l.append("- Details --------------------------------------------------")
        l.append("  Target:       {}".format(self.target))
        l.append("  Description:  {}".format(self.description))
        l.append("  Editor:       {}".format(self.editor))
        l.append("  Web site:     {}".format(self.web_site_location))
        l.append("  Icon:         {}".format(self.icon))
        l.append("  Announce:     {}".format(self.announce_location))
        l.append("  Feed:         {}".format(self.feed_location))
        l.append("  Release Note: {}".format(self.release_note_location))
        l.append("------------------------------------------------------------")
        l.append("- Change summary -------------------------------------------")
        l.append(self.change_summary)
        l.append("------------------------------------------------------------")
        l.append("- Installer ------------------------------------------------")
        l.append("  URL:          {}".format(self.location))
        l.append("  Location:     {}".format(self.installer))
        l.append("  Size:         {} bytes".format(self.file_size))
        if self.secure_hash is not None:
            hn, hv = self.secure_hash
        else:
            hn, hv = ["", ""]
        l.append("  Hash:         {} ({})".format(hv, hn))
        l.append("  Command line option")
        l.append("    Silent mode:   {}".format(self.silent_inst_args))
        l.append("    Standard mode: {}".format(self.std_inst_args))
        l.append("------------------------------------------------------------")
        return "\n".join(l)

    def load(self, attributes):
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
        msg = ">>> (attributes={})"
        _logger.debug(msg.format(attributes))
        # check parameters type
        if not isinstance(attributes, dict):
            msg = "attributes argument must be a class 'dict'. not {0}"
            msg = msg.format(attributes.__class__)
            raise TypeError(msg)

        # set instance variables
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue  # non-public instance variables are ignored
            else:
                if k in attributes:
                    self.__dict__[k] = attributes[k]
                    msg = "Instance variables '{0}' : '{1}' -> '{2}'"
                    _logger.debug(msg.format(k, v, attributes[k]))
                else:
                    msg = "Instance variables '{0}' : not modified"
                    _logger.debug(msg.format(k))

        msg = "<<< ()=None"
        _logger.debug(msg)

    def dump(self):
        """
        Dump a product class.

        Returns:
            dict: Contain a copy of the instance variables values.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        attributes = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue  # non-public instance variables are ignored
            else:
                attributes[k] = v

        msg = "<<< ()={}"
        _logger.debug(msg.format(attributes))
        return attributes

    def get_origin(self, version=None):
        """
        Get product information from the remote repository.

        The latest catalog of the product is downloaded and parsed.

        Args:
            version (str): The version of the reference product (i.e. the
                deployed product). It'a string following the editor versioning
                rules.

        Returns:
            bool: True if the download of the file went well. In case of
            failure, the members are not modified and an error log is written.

        Raises:
            TypeError: Parameters type mismatch.
        """
        raise NotImplementedError

    def fetch(self, dirpath):
        """
        Download the product installer.

        Args:
            dirpath (str): The directory path name where to store the installer
                package.

        Returns:
            bool: True if the download of the file went well. In case of
            failure, the members are not modified and an error log is written.

        Raises:
            `TypeError`: Parameters type mismatch.
        """
        msg = ">>> (dirpath={})"
        _logger.debug(msg.format(dirpath))

        result = True
        # TODO (fmezou): l'url ne contient pas necessairement le nom de la
        # ressource, il faut utiliser le champs Content-disposition
        # Content-Disposition: attachment; filename=my_sandbox.tar.gz
        # see RFC 2183
        components = urllib.parse.urlsplit(self.location)
        name = os.path.basename(
            urllib.request.url2pathname(components.path))
        ext = os.path.splitext(name)[1]
        filename = "{}_v{}{}".format(self.name, self.version, ext)
        pathname = os.path.normcase(os.path.join(dirpath, filename))
        tempname = pathname + ".partial"

        try:
            os.makedirs(dirpath, exist_ok=True)
        except OSError as err:
            msg = "Failed to create the destination directory - OS error: {}"
            _logger.error(msg.format(str(err)))
            result = False

        if result:
            try:
                with open(tempname, mode="wb") as file:
                    t, l, h = retrieve_file(self.location,
                                            file,
                                            exp_clength=self.file_size,
                                            exp_chash=self.secure_hash)
                os.replace(tempname, pathname)  # rename with the real name
            except urllib.error.URLError as err:
                msg = "Inaccessible resource: {} - url: {}"
                _logger.error(msg.format(str(err), self.location))
                result = False
            except (ContentTypeError, ContentLengthError, ContentError) as err:
                msg = "Unexpected content: {}"
                _logger.error(msg.format(str(err)))
                result = False
            except ValueError as err:
                msg = "Internal error: {}"
                _logger.error(msg.format(str(err)))
                result = False
            except OSError as err:
                msg = "OS error: {}"
                _logger.error(msg.format(str(err)))
                result = False
            else:
                self.file_size = l
                self.secure_hash = h
                self.installer = pathname
                msg = "Installer downloaded: '{}'".format(self.installer)
                _logger.info(msg)

        # clean up
        if not result:
            try:
                os.remove(tempname)
            except OSError:
                pass

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

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


def retrieve_file(url, file, exp_ctype=None, exp_clength=-1, exp_chash=None):
    """
    Retrieve a URL into a file-like object.


    Args:
        url (str): The URL of the file to retrieve.
        file (file-like object): A file-like object to use to store the
            retrieved data.
        exp_ctype (str): (optional) The expected mime type of the retrieved
            file. No check will be done if the value is None.
        exp_clength (int): (optional) The expected length of the retrieved
            file expressed in bytes. -1 means that the expected length is
            unknown.
        exp_chash (2-tuple): The expected secure hash value of the retrieved
            file. No check will be done if the value is None. It's a tuple
            containing, in this order, the name of secure hash algorithm
            (see `hashlib.algorithms_guaranteed`) and the secure hash value in
            hexadecimal notation. If the secure hash algorithm is not supported,
            it will be ignored.

    Returns:
        tuple: it's a 3-tuple containing, in this order, the content type, the
        content length and the content hash and . If the content hash algorithm
        is not specified in the :dfn:`content_hash` parameter, the sha-1
        algorithm will be used.

    Raises:
        TypeError: Parameters type mismatch.
        ContentTypeError: The downloaded content-type don't match.
        ContentLengthError: The content length don't match.
        ContentError: The content secure hash don't match.
        Same as `urllib.request.urlopen`.
    """
    msg = ">>> (url={}, file={}, exp_ctype={}, exp_clength={}, exp_chash={})"
    _logger.debug(msg.format(url, file, exp_ctype, exp_clength, exp_chash))

    # check parameters type
    if not isinstance(url, str):
        msg = "url argument must be a class 'str'. not {0}"
        msg = msg.format(url.__class__)
        raise TypeError(msg)

    if exp_ctype is not None:
        if not isinstance(exp_ctype, str):
            msg = "exp_ctype argument must be a class 'str'. not {0}"
            msg = msg.format(exp_ctype.__class__)
            raise TypeError(msg)

    if not isinstance(exp_clength, int):
        msg = "exp_clength argument must be a class 'int'. not {0}"
        msg = msg.format(exp_clength.__class__)
        raise TypeError(msg)

    if exp_chash is not None:
        if isinstance(exp_chash, tuple) and len(exp_chash) == 2:
            if not isinstance(exp_chash[0], str):
                msg = "hash algorithm argument must be a class 'str'. not {0}"
                msg = msg.format(exp_chash[0].__class__)
                raise TypeError(msg)
            if not isinstance(exp_chash[1], str):
                msg = "hash value argument must be a class 'str'. not {0}"
                msg = msg.format(exp_chash[1].__class__)
                raise TypeError(msg)
        else:
            msg = "exp_chash argument must be a class 'tuple'. not {0}"
            msg = msg.format(exp_chash.__class__)
            raise TypeError(msg)

    # retrieve the resource
    check_ctype = True
    check_clength = True
    check_chash = True
    rcv_ctype = ""
    rcv_clength = -1
    rcv_hash = hashlib.sha1()

    # some web servers refuse to deliver pages when the user-agent is set to
    # 'Python-urllib'. So the user-agent is set to the name of the project.
    # TODO (fmezou): mettre le nom et la version du projet dans le user-agent
    # see version.py
    headers = {"User-Agent": "lAppUpdate/0.1"}

    request = urllib.request.Request(url, headers=headers)
    with contextlib.closing(urllib.request.urlopen(request)) as stream:
        headers = stream.info()
        _logger.debug("Headers=\n{}".format(headers))
        _logger.debug("Real URL='{}'.".format(stream.geturl()))
        # Check the expected content
        if "Content-Type" in headers:
            rcv_ctype = headers["Content-Type"]
            if exp_ctype is not None:
                if rcv_ctype != exp_ctype:
                    raise ContentTypeError(url, exp_ctype, rcv_ctype)
            else:
                check_ctype = False
                msg = "Content-type is not specified."
                _logger.warning(msg)
        else:
            check_ctype = False
            msg = "Content-type header do not exist."
            _logger.warning(msg)
        if not check_ctype:
            msg = "Content-type control will be ignored."
            _logger.warning(msg)

        if "Content-Length" in headers:
            rcv_clength = int(headers["Content-Length"])
            if exp_clength != -1 and rcv_clength != exp_clength:
                raise ContentLengthError(url, exp_clength, rcv_clength)
        else:
            if exp_clength == -1:
                check_clength = False
                msg = "Content-Length is not specified."
                _logger.warning(msg)
        if not check_clength:
            msg = "Content-Length control will be ignored."
            _logger.warning(msg)

        if exp_chash:
            if exp_chash[0] in hashlib.algorithms_available:
                rcv_hash = hashlib.new(exp_chash[0])
            else:
                check_chash = False
                msg = "Hash algorithm {} is not supported"
                _logger.warning(msg.format(exp_chash[0]))
        else:
            check_chash = False
            msg = "Hash algorithm is not specified"
            _logger.warning(msg)
        if not check_chash:
            msg = "Content-Hash control will be ignored."
            _logger.warning(msg)

        msg = "Retrieving '{}' -> '{}'"
        _logger.info(msg.format(url, file.name))
        length = 0
        # TODO (fmezou) prevoir le passage en paramètre de l'objet
        progress_bar = progressbar.TextProgressBar(exp_clength)
        progress_bar.compute(length, exp_clength)
        data = stream.read(1500)
        while data:
            length += len(data)
            file.write(data)
            rcv_hash.update(data)
            progress_bar.compute(length, rcv_clength)
            data = stream.read(1500)
        progress_bar.finish()
        msg = "'{}' retrieved - (length: {}B, mime type: {}, {}={})"
        msg = msg.format(file.name, rcv_clength, rcv_ctype,
                         rcv_hash.name, rcv_hash.hexdigest())
        _logger.info(msg)

        # Post content checking
        if check_clength:
            if length != rcv_clength:
                raise ContentLengthError(url, rcv_clength, length)
        if check_chash:
            if rcv_hash.hexdigest() != exp_chash[1]:
                raise ContentError(url, exp_chash[0], exp_chash[1],
                                   rcv_hash.hexdigest())

    result = (rcv_ctype, rcv_clength, (rcv_hash.name, rcv_hash.hexdigest()))

    msg = "<<< ()={}"
    _logger.debug(msg.format(result))
    return result


def get_handler(qualname):
    """
    Retrieve an instance of a handler class.

    A handler class is appointed by its :term:`qualified name`
    (:class:`package.module.MyHandler` for example). If the module part is not
    specified, an ImportError exception is raised.

    Args:
        qualname (str): The qualified name of the handler class.

    Returns:
        BaseProduct: an instance of the handler class.

    Raises:
        TypeError: Parameters type mismatch.
        ImportError:  Import fails to find the handler module or class.
    """
    msg = ">>> (qualname={})"
    _logger.debug(msg.format(qualname))
    # check parameters type
    if not isinstance(qualname, str):
        msg = "qualname argument must be a class 'str'. not {0}"
        msg = msg.format(qualname.__class__)
        raise TypeError(msg)

    names = qualname.split(".")
    if len(names) < 2:
        name = names[-1]
        msg = "No module named for handler class '{}'".format(name)
        raise ImportError(msg, name=name, path="")

    path = ".".join(names[:-1])
    name = names[-1]
    module = importlib.import_module(path)
    if name not in module.__dict__:
        msg = "No handler class named '{}' in module '{}'".format(name, path)
        raise ImportError(msg, name=name, path=path)

    handler_class = module.__dict__[name]
    if not issubclass(handler_class, BaseProduct):
        msg = "Handler class must be a class 'BaseProduct'. not {0}"
        msg = msg.format(handler_class)
        raise TypeError(msg)

    msg = "{} handler loaded from {} package"
    _logger.info(msg.format(handler_class, path))
    result = handler_class()
    msg = "<<< ()={}"
    _logger.debug(msg.format(result))
    return result


def get_file_hash(path, hash_name):
    """
    Compute a secure hash based on the content of a file.

    Args:
        path (str): The pathname of the file
        hash_name: The name of secure hash algorithm (see
            `hashlib.algorithms_guaranteed`). If the secure hash algorithm is
            not supported, a `ValueError` exception is raised.

    Returns:
        HASH: A hash object instance (see `hashlib`). This instance contains
        the computed hash of the given path.

    """
    msg = ">>> (path={}, hash_name={})"
    _logger.debug(msg.format(path, hash_name))
    # check parameters type
    if not isinstance(path, str):
        msg = "path argument must be a class 'str'. not {0}"
        msg = msg.format(path.__class__)
        raise TypeError(msg)
    if hash_name not in hashlib.algorithms_available:
        msg = "Hash algorithm {} is not supported."
        raise ValueError(msg)

    secure_hash = hashlib.new(hash_name)
    with open(path, mode="rb") as file:
        while True:
            data = file.read(4096)
            if not data:
                break
            secure_hash.update(data)

    msg = "<<< ()={}"
    _logger.debug(msg.format(secure_hash))
    return secure_hash

