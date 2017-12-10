"""
This module defines core functions and classes for product handlers.

Product handlers are derived classes from `BaseProduct` class.


Public Classes
--------------
This module has has several public class listed below in alphabetical order.

===================================  ===================================
`BaseProduct`                        `DownloadHandler`
===================================  ===================================


Public Functions
----------------
This module has a number of functions listed below in alphabetical order.

===================================  ===================================
`get_handler`                        `get_file_hash`
===================================  ===================================
"""

import contextlib
import hashlib
import logging
import os
import urllib.request
import urllib.parse
import urllib.error
import tempfile
import importlib

from support import progressindicator
from version import *

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "DownloadHandler",
    "BaseProduct",
    "get_file_hash",
    "get_handler"
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


class BaseProduct:
    """
    Common base class for all product handlers.


    Attributes:
        name (str): The name of the product. It is used in report mail, log
            file and as filename for the installer (see `fetch`)
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
        `load`                               `get_name`
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
        self.file_size = 0
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

    def get_origin(self):
        """
        Get product information from the remote repository.

        The latest catalog of the product is downloaded and parsed.

        Returns:
            bool: `True` if the download of the file went well. In case of
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
            bool: `True` if the download of the file went well. In case of
            failure, the members are not modified and an error log is written.

        Raises:
            `TypeError`: Parameters type mismatch.
        """
        msg = ">>> (dirpath={})"
        _logger.debug(msg.format(dirpath))

        result = True

        progress = progressindicator.new_download_progress(self.display_name)
        remote = DownloadHandler(self.location, path=dirpath,
                                 length=self.file_size, hash=self.secure_hash,
                                 progress=progress)
        result = remote.fetch()
        if result:
            p, n = os.path.split(remote.filename)
            ext = os.path.splitext(n)[1]
            filename = "{}_v{}_{}{}".format(self.name.lower(), self.version,
                                            self.target, ext)
            target_name = os.path.normcase(os.path.join(p, filename))

            try:
                os.replace(remote.filename, target_name)
            except OSError as err:
                msg = "OS error: {}"
                _logger.error(msg.format(str(err)))
                result = False
            else:
                self.file_size = remote.length
                self.secure_hash = (remote.hash.name, remote.hash.hexdigest())
                self.installer = target_name
                msg = "Installer downloaded: '{}'".format(self.installer)
                _logger.info(msg)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def is_update(self, product):
        """
        Return if this instance is an update of the product

        This method compare the version of the two product, and return the
        comparison result.

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: `True` if this instance is an update of the product specified
            by the `product` parameter.
        """
        raise NotImplementedError

    def get_name(self):
        """
        Return a comprehensive name of the product

        Returns:
            str: a human readable string with the handler attributes.
        """
        return "{} ({})".format(self.name.title(), self.target.title())


class DownloadHandler(object):
    """
    File Download Handler

    This class is a handler to download files available on a HTTP or FTP
    server. It fully manages the download process and the retrieved file may
    be stored in a regular or a temporary file.

    Args:
        url (str): The URL of the file to retrieve.
        path (str): The local pathname of the retrieved file. An empty string
            will force the use of a temporary file (see
            :func:`~tempfile.NamedTemporaryFile`). If the pathname is a
            directory, the retrieved file will be written in this directory, and
            the filename will be guessed from the url or HTTP response headers.
            [TODO]If the pathname is a valid filename, the retrieved file will use it.
        type (str): (optional) The expected mime type of the retrieved
            file. No check will be done if the value is `None`.
        length (int): (optional) The expected length of the retrieved
            file expressed in bytes. `None` means that the expected length is
            unknown.
        hash (tuple): The expected secure hash value of the retrieved
            file. No check will be done if the value is `None`. It's a 2-tuple
            containing, in this order, the name of secure hash algorithm
            (see :data:`~hashlib.algorithms_guaranteed`) and the secure hash
            value in hexadecimal notation. If the secure hash algorithm is not
            supported, it will be ignored.
        progress (~progressindicator.ProgressIndicatorWidget): The progress
            widget. The `None` value means that no progress indicator will be
            displayed.

    Raises:
        TypeError: Parameters type mismatch.

    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `fetch`                              ..
        ===================================  ===================================


    **Using DownloadHandler...**
        After created a class instance, the `fetch` method downloads the
        file and populates the attributes.
    """

    def __init__(self, url, path=None, type=None, length=None, hash=None,
                 progress=None):
        msg = ">>> (url={}, path={}, type={}, length={}, hash={}, " \
              "progress = {})"
        _logger.debug(msg.format(url, path, type, length, hash, progress))

        #: `str`: The URL of the retrieved file. It may differs from the
        #: original url if a redirect was followed.
        self.url = ""
        #: `int`: The length of the retrieved file expressed in bytes.
        self.length = 0
        #: `str`: The mime type of the retrieved file. The default value is
        #: ``application/octet-stream`` as defined by the `IANA`_.
        self.type = "application/octet-stream"
        #: `str`: The local pathname of the retrieved file.
        self.filename = ""
        #: `hashlib.hash`: The secure hash value of the retrieved file. A secure
        #: hash is always computed and the default algorithm is `SHA-1
        #: <http://csrc.nist.gov/publications/fips/fips180-2/fips180-2.pdf>`_.
        self.hash = hashlib.sha1()

        # internal attributes
        self._stream = None #  stream opened with urlopen
        self._file = None #  stream for the local file

        # internal attributes to store the parameters (see above)
        self.path = ""
        self._exp_type = None
        self._exp_length = None
        self._exp_hash = None

        # check parameters type
        if not isinstance(url, str):
            msg = "url argument must be a class 'str'. not {0}"
            msg = msg.format(url.__class__)
            raise TypeError(msg)
        self.url = url

        if path:
            if not isinstance(path, str):
                msg = "path argument must be a class 'str'. not {0}"
                msg = msg.format(path.__class__)
                raise TypeError(msg)
            self.path = path

        if type:
            if not isinstance(type, str):
                msg = "type argument must be a class 'str'. not {0}"
                msg = msg.format(type.__class__)
                raise TypeError(msg)
            self._exp_type = type

        if length:
            if not isinstance(length, int):
                msg = "length argument must be a class 'int'. not {0}"
                msg = msg.format(length.__class__)
                raise TypeError(msg)
            self._exp_length = length

        if hash:
            if isinstance(hash, tuple) and len(hash) == 2:
                if not isinstance(hash[0], str):
                    msg = "hash algorithm argument must be a class 'str'. not {0}"
                    msg = msg.format(hash[0].__class__)
                    raise TypeError(msg)
                if not isinstance(hash[1], str):
                    msg = "hash value argument must be a class 'str'. not {0}"
                    msg = msg.format(hash[1].__class__)
                    raise TypeError(msg)
                if hash[0] in hashlib.algorithms_available:
                    self.hash = hashlib.new(hash[0])
                    self._exp_hash = hash
                else:
                    msg = "Hash algorithm {} is not supported"
                    _logger.warning(msg.format(hash[0]))
            else:
                msg = "hash argument must be a class 'tuple'. not {0}"
                msg = msg.format(hash.__class__)
                raise TypeError(msg)

        self._progress_widget = \
            progressindicator.ProgressIndicatorWidget()
        if progress:
            if not isinstance(progress,
                              progressindicator.ProgressIndicatorWidget):
                msg = "progress argument must be a class " \
                      "'ProgressIndicatorWidget'. not {0}"
                msg = msg.format(progress.__class__)
                raise TypeError(msg)
            self._progress_widget = progress

        msg = "<<< ()=None"
        _logger.debug(msg)

    def fetch(self):
        """
        Download the product installer.

        Returns:
            bool: `True` if the download of the file went well. In case of
            failure, an error log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)
        # some web servers refuse to deliver pages when the user-agent is set to
        # 'Python-urllib'. So the user-agent is set to the name of the project.
        v = __version__.split(".")
        headers = {"User-Agent": "{}/{}.{}".format(__project__, v[0], v[1])}

        result = True
        request = urllib.request.Request(self.url, headers=headers)

        try:
            with contextlib.closing(urllib.request.urlopen(request)) as self._stream:
                result = self._pre_check_length()
                if result:
                    result = self._pre_check_type()
                if result:
                    msg = "Length: {} B [{}]"
                    _logger.debug(msg.format(self.length, self.type))
                    result = self._open_container()
                    if result:
                        self._write_container()
                        result = self._post_check_length()
                        if result:
                            result = self._post_check_hash()
        except urllib.error.URLError as err:
            msg = "Inaccessible resource: {} - url: {}"
            _logger.error(msg.format(str(err), self.url))
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
            msg = "'{}' retrieved - ({} B [{}], {}={})"
            msg = msg.format(os.path.basename(self.filename),
                             self.length, self.type,
                             self.hash.name, self.hash.hexdigest())
            _logger.info(msg)
        finally:
            if self._file:
                self._close_container(result)
            self._stream = None

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _open_container(self):
        """
        Open the container for the future retrieved file.

        This method opens either a temporary file or a regular file depending on
        the value of the :attr:`path` attribute. It sets the :attr:`_file`
        and the :attr:`filename` attributes.

        Returns:
            bool: `True` if the opening of the file went well.
        """
        msg = ">>> ()"
        _logger.debug(msg)
        result = True

        if not self.path:
            self._file = tempfile.NamedTemporaryFile(delete=False)
            self.filename = os.path.normcase(self._file.name)
            msg = "Retrieving to '{}'"
            _logger.debug(msg.format(self.filename))
        else:
            try:
                os.makedirs(self.path, exist_ok=True)
            except OSError as err:
                msg = "Failed to create the destination directory - " \
                      "OS error: {}"
                _logger.error(msg.format(str(err)))
                result = False
            else:
                fn = self._get_filename_from_headers()
                if not fn:
                    fn = self._get_filename_from_url()
                self.filename = os.path.normcase(os.path.join(self.path, fn))
                fn = self.filename + ".partial"
                try:
                    self._file = open(fn, mode="wb")
                except OSError as err:
                    msg = "OS error: {}"
                    _logger.error(msg.format(str(err)))
                    result = False
                else:
                    msg = "Retrieving to '{}'"
                    _logger.debug(msg.format(self._file.name))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _write_container(self):
        """
        Fill the container with the content of the retrieved files

        Returns:
            bool: `True` if the downloading of the file went well.
        """
        msg = ">>> ()"
        _logger.debug(msg)
        result = True

        assert self._file, "_file attribute must be defined"

        self.length = 0
        self._progress_widget.start(self.length, self._exp_length)
        data = self._stream.read(1500)
        while data:
            self.length += len(data)
            self._file.write(data)
            self.hash.update(data)
            self._progress_widget.update(self.length)
            data = self._stream.read(1500)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _close_container(self, keep=True):
        """
        Close the container and check its content.

        Args:
            keep (bool): `True` to indicate to keep the local copy of the
                retrieved file. The `False` value is usefull in case of error
                while the download process.

        Returns:
            bool: `True` if the downloading of the file went well.
        """
        msg = ">>> (keep={})"
        _logger.debug(msg.format(keep))
        result = True

        assert self._file, "_file attribute must be defined"

        self._progress_widget.finish(self.length)
        self._file.close()
        if keep:
            # rename with the real name if necessary
            if self.filename:
                try:
                    os.replace(self._file.name, self.filename)
                except OSError as err:
                    msg = "OS error: {}"
                    _logger.error(msg.format(str(err)))
                    result = False
        else:
            _logger.debug("cleaning up")
            try:
                os.remove(self._file.name)
            except OSError:
                pass

        self._file = None

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _pre_check_length(self):
        """
        Check the length of the file to retrieve.

        Returns:
            bool: `True` if the length is equal to that expected
            (:attr:`_exp_length`). The method return `True` if the control
            must be ignored (see ``length`` parameter)
        """
        msg = ">>> ()"
        _logger.debug(msg)
        result = True

        headers = self._stream.info()
        if "Content-Length" in headers:
            self.length = int(headers["Content-Length"])
        else:
            msg = "Content-Length header do not exist."
            _logger.warning(msg)

        if self._exp_length:
            if self.length != self._exp_length:
                result = False
                msg = "Unexpected content length : '{0}' received vs. " \
                      "'{1}' waited."
                _logger.error(msg.format(self.length, self._exp_length))
        else:
            # Content-Length control will be done."
            self._exp_length = self.length

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _post_check_length(self):
        """
        Check the length of the retrieved file.

        Returns:
            bool: `True` if the length is equal to that expected
            (:attr:`_exp_length`). The method return `True` if the control
            must be ignored (see ``length`` parameter)
        """
        msg = ">>> ()"
        _logger.debug(msg)
        result = True

        if self._exp_length:
            if self.length != self._exp_length:
                result = False
                msg = "Unexpected content length : '{0}' received vs. " \
                      "'{1}' waited."
                _logger.error(msg.format(self.length, self._exp_length))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _pre_check_type(self):
        """
        Check the mime type of the file to retrieve.

        Returns:
            bool: `True` if the MIME type is equal to that expected
            (:attr:`_exp_type`). The method return `True` if the control
            must be ignored (see ``type`` parameter)
        """
        msg = ">>> ()"
        _logger.debug(msg)
        result = True

        headers = self._stream.info()
        if "Content-Type" in headers:
            self.type = headers["Content-Type"]
        else:
            msg = "Content-Type header do not exist."
            _logger.warning(msg)

        if self._exp_type:
            if self.type != self._exp_type:
                result = False
                msg = "Unexpected content type : '{0}' received vs. " \
                      "'{1}' waited."
                _logger.error(msg.format(self.type, self._exp_type))
        else:
            msg = "Content-type control ignored."
            _logger.warning(msg)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _post_check_hash(self):
        """
        Check the secure hash of the retrieved file.

        Returns:
            bool: `True` if the computed secure hash is equal to that expected
            (:attr:`_exp_hash`). The method return `True` if the control
            must be ignored (see ``hash`` parameter)
        """
        msg = ">>> ()"
        _logger.debug(msg)
        result = True

        if self._exp_hash:
            if self.hash.hexdigest() != self._exp_hash[1]:
                result = False
                msg = "Unexpected content : '{0}' received vs. '{1}' waited."
                _logger.error(msg.format(self.hash.hexdigest(),
                                         self._exp_hash[1]))
        else:
            msg = "Secure hash control ignored."
            _logger.warning(msg)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _get_filename_from_headers(self):
        """
        Get the file name from the ``Content-Disposition`` header field.

        This method returns the file name specified in the
        ``Content-Disposition`` header field as described in the :rfc:`2183` if
        it exists.

        TODO
        This method checks the file name compatibility with the underlying file
        system. If the suggested file name is not compatible, the method returns
        `None`.

        Returns:
            str: a regular file name or `None`.
        """
        msg = ">>> ()"
        _logger.debug(msg)
        result = None

        headers = self._stream.info()
        _logger.debug("Headers=\n{}".format(headers))

        field = "Content-Disposition"
        header = headers["Content-Disposition"]
        if not header:
            msg = "Content-Disposition field do not exist."
            _logger.debug(msg)
        else:
            types = header.split(";", maxsplit=1)
            if types[0].lower().strip() == "attachment":
                params = types[1].split(";")
                for param in params:
                    p = param.split("=")
                    if len(p) == 2:
                        k = p[0].lower().strip()
                        v = p[1].lower().strip()
                        if k == "filename":
                            result = os.path.basename(v)  # prevent a path specs
                            break
                        else:
                            msg = "Content-Disposition param '{}' is ignored ."
                            _logger.debug(msg.format(k))
                    else:
                        msg = "Content-Disposition param '{}' is ignored ."
                        _logger.debug(msg.format(param))
            else:
                msg = "Content-Disposition type '{}' is ignored ."
                _logger.debug(msg.format(types[0].lower().strip()))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _get_filename_from_url(self):
        """
        Get the file name from the url attribute.

        This method returns the file name specified in the URL.

        TODO
        This method checks the file name compatibility with the underlying file
        system. If the suggested file name is not compatible, the method returns
        `None`.

        Returns:
            str: a regular file name or `None`.
        """
        msg = ">>> ()"
        _logger.debug(msg)
        result = None

        self.url = self._stream.geturl()
        _logger.debug("Real URL='{}'.".format(self.url))

        components = urllib.parse.urlsplit(self.url)
        result = os.path.basename(urllib.request.url2pathname(components.path))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def __str__(self):
        """
        Return the printable string representation of object.

        Returns:
            str: a human readable string with the handler attributes.
        """
        l = list()
        l.append("Download handler attributes:")
        l.append("- General --------------------------------------------------")
        l.append("  URL:          {}".format(self.url))
        l.append("  Length:       {}".format(self.length))
        l.append("  MIME Type:    {}".format(self.type))
        l.append("  Filename :    {}".format(self.filename))
        l.append("  Hash:         {} ({})".format(self.hash.name,
                                                  self.hash.hexdigest()))
        l.append("------------------------------------------------------------")
        return "\n".join(l)


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

