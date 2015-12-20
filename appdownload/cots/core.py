"""COTS core module.

Classes
    Product : base class for a product

Exception

Function

Constant

"""

import logging
import time
import tempfile
import os
import urllib.request
import contextlib

__all__ = [
    "BaseProduct"
]


def _isu_format_prefix(value, unit):
    """ return a string using standard prefix for unit.

    The returned string represent the value in a compliant International
    System of Units format, which means with a prefix for unit.
    (see https://en.wikipedia.org/wiki/International_System_of_Units)

    Parameters
        :param value: is the value to format (may be a float or an integer.
        :param unit: is a string representing the unit of the value.

        :return: is a string representing value (5.75 MB for example).
    """
    # check parameters type
    if not (isinstance(value, int) or isinstance(value, float)):
        msg = "value argument must be a class 'int' or 'float'. not {0}"
        msg = msg.format(value.__class__)
        raise TypeError(msg)
    # check parameters type
    if not isinstance(unit, str):
        msg = "unit argument must be a class 'str'. not {0}"
        msg = msg.format(unit.__class__)
        raise TypeError(msg)

    mul_unit = " " + "" + unit
    isu_str = "----" + unit
    r = float(value)
    for prefix in ["", "k", "M", "G", "T", "P", "E", "Z", "Y"]:
        mul_unit = " " + prefix + unit
        if r < 1000.0:
            if r < 10.0:
                isu_str = ("{:>1.2f}" + mul_unit).format(r)
            elif r < 100.0:
                isu_str = ("{:>2.1f}" + mul_unit).format(r)
            else:
                isu_str = ("{:>4.0f}" + mul_unit).format(r)
            break
        else:
            r /= 1000.0
    else:
        isu_str = ">999 " + mul_unit

    return isu_str


def _isu_format_thousand(value):
    """Return a string using standard ISU thousand separator.

    The returned string represent the value in a compliant International
    System of Units format, which means with a space for thousand separator.
    (see https://en.wikipedia.org/wiki/International_System_of_Units)

    Parameters
        :param value: is the value to format (may be a float or an integer).

        :return: is a string representing value (5 000 for example).
    """
    # check parameters type
    if not (isinstance(value, int) or isinstance(value, float)):
        msg = "value argument must be a class 'int' or 'float'. not {0}"
        msg = msg.format(value.__class__)
        raise TypeError(msg)

    if isinstance(value, int):
        isu_str = ("{:>,d}".format(value)).replace(",", " ")
    else:
        isu_str = ("{:>,f}".format(value)).replace(",", " ")

    return isu_str


class TextProgressBar:
    """Progress bar for console output.

    Public instance variables
        None

    Public methods
        compute: compute the progress bar and print it.
        finish: compute the completion progress bar and return the computed
        string.

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None
    """

    def __init__(self, max_len=-1):
        """Constructor.

        Parameters
            :param max_len: is a positive integer specifying the content length
            that the progress bar is going to represent. A negative number
            specify that the content length is unknown.
        """
        # check parameters type
        if not isinstance(max_len, int):
            msg = "max_len argument must be a class 'int'. not {0}"
            msg = msg.format(max_len.__class__)
            raise TypeError(msg)

        self._t0 = time.time()
        self._length = 0
        self._content_length = max_len
        self._t1 = 0.0

    def compute(self, length, content_length=-1):
        """Compute the progress bar and print it.

        The printed string match the following format:
        aaa% [==============================] lll,lll,lll,lll - rrrr XB/s - eta nn:nn:nn
        aaa: is the percentage of progress
        ===: is the bar graph of progress (step=1/30)
        lll,lll,lll,lll: is the number of received bytes
        rrrr: is the bytes rate where X represent a multiple of the unit bytes
        per second (G, M or k).
        nn:nn:nn: is the estimated time to achieve the download.

        note : to prevent the display flicking, the refresh period is limited to
        4 time per second.

        Parameters
            :param length: is a positive integer specifying the length of
                received data.
            :param content_length: is a positive integer specifying the content
            length that the progress bar is going to represent. A negative
            number specify that the content length is unknown.
        """
        # check parameters type
        if not isinstance(length, int):
            msg = "length argument must be a class 'int'. not {0}"
            msg = msg.format(length.__class__)
            raise TypeError(msg)

        if not isinstance(content_length, int):
            msg = "content_length argument must be a class 'int'. not {0}"
            msg = msg.format(content_length.__class__)
            raise TypeError(msg)

        self._content_length = content_length
        self._length = length

        last_refresh = time.time() - self._t1
        if last_refresh > 0.25:
            self._t1 = time.time()
            # compute the rate
            base_unit = "B/s"
            duration = int(time.time() - self._t0)
            if duration != 0 and length != 0:
                rate = _isu_format_prefix(length / duration, base_unit)
            else:
                rate = "----" + " " + "" + base_unit

            # compute the eta
            eta = "--:--:--"
            if length <= self._content_length and length != 0:
                t = (self._content_length - length) / length * duration
                h = int(t // 3600)
                r = int(t % 3600)
                m = int(r // 60)
                s = int(r % 60)
                eta = "{:02d}:{:02d}:{:02d}".format(h, m, s)

            # compute the percent
            bargraph = ""
            percent = " --%"
            if length <= self._content_length != 0:
                p = length / self._content_length
                percent = "{:>4.0%}".format(p)
                bargraph = "[" + ("=" * int(p * 30)).ljust(30) + "]"

            # compute the length of received data
            receive = _isu_format_thousand(length).rjust(15)

            progress = "{} {} {} - {} - eta {}".format(percent, bargraph,
                                                       receive, rate, eta)
            print("\r" + progress, end="")

    def finish(self):
        """ Compute the completion progress bar and return the computed string.

        The returned string match the following format:
        llll XB received - rrrr XB/s in nn:nn:nn
        lll XB: is the number of received bytes where X represent a multiple
        of the unit byte(G, M or k).
        rrrr: is the bytes rate where X represent a multiple of the unit bytes
        per second (G, M or k).
        nn:nn:nn: is the time of downloading.

        Parameters

            :return: is a string representing the progress information.
        """
        # compute the length of received data
        receive = _isu_format_prefix(self._length, "B")

        # compute the rate
        base_unit = "B/s"
        duration = int(time.time() - self._t0)
        if duration != 0 and self._length != 0:
            rate = _isu_format_prefix(self._length / duration, base_unit)
        else:
            rate = "----" + " " + "" + base_unit

        # compute the time
        h = int(duration // 3600)
        r = int(duration % 3600)
        m = int(r // 60)
        s = int(r % 60)
        eta = "{:02d}:{:02d}:{:02d}".format(h, m, s)

        progress = "{} received - {} in {}".format(receive, rate, eta)
        progress = progress.ljust(80)  # to overwrite the previous progress bar
        print("\r" + progress)
        return progress


class BaseProduct:
    """Common base class for all products.

    Public instance variables
        id: id of the product (may be the name or any unique id)
        name: is the name of the application as it appears in the Program
          Control Panel.
        version: is the current version of the product
        published: is the date of the installer’s publication (ISO 8601 format)
        target: is the target architecture type (the Windows’ one) for the
          application. This argument must be one of the following values:
          'x86', 'x64' or 'unified'.
          x86: the application works only on 32 bits architecture
          x64: the application works only on 64 bits architecture
          unified: the application or the installation program work on both
           architectures
        release_note: is the release note’s URL for the current version of the
          application.
        installer: filename of the installer (local full path)
        std_inst_args: arguments to do a standard installation.
        silent_inst_args: arguments to do a silent installation.
        update_available: is a flag indicating if a new version is available
          or not.
        update_version: is the version of the last release of the product.
        update_published:is the publication date of the last release of
          the product.
        update_location: location (url) of the last version of the installer.
        product_code: UID of the product (see MSI product code)

    Public methods
        load: load a product class.
        dump: dump a product class.

    Subclass API variables (i.e. may be use by subclass)
        _catalog_location: location (url) of the product catalog.

    Subclass API Methods (i.e. must be overwritten by subclass)
        check_update: checks if a new version is available
        fetch_update: downloads the latest version of the installer
    """
# TODO suppress the id attribute, it's the name of module.

    def __init__(self, logger=logging.getLogger(__name__)):
        """Constructor.

        Parameters
            :param logger: is a logger object
        """
        self.id = None
        self.name = ""
        self.version = ""
        self.published = ""
        self.target = ""
        self.release_note = ""
        self.installer = ""
        self.std_inst_args = ""
        self.silent_inst_args = ""
        self.update_available = False
        self.update_version = ""
        self.update_published = ""
        self.update_location = ""
        self.product_code = ""

        self._catalog_location = ""
        self._temp_files = []

        # check logger parameter
        self._logger = logger
        if not isinstance(logger, logging.Logger):
            msg = "logger argument must be a class 'logging.Logger'. not {0}"
            msg = msg.format(logger.__class__)
            raise TypeError(msg)
        # To make the module as versatile as possible, an nullHandler is added.
        # see 'Configuring Logging for a Library'
        # docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
        self._logger.addHandler(logging.NullHandler())
        self._logger.debug("Instance created.")

    def load(self, attributes=None):
        """Load a product class.

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
        self._logger.info("Load the product.")
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue  # non-public instance variables are ignored
            else:
                attr = attributes.get(k)
                if attr is not None:
                    self.__dict__[k] = attributes.get(k)
                    msg = "Instance variables '{0}' : '{1}' -> '{2}'"
                    self._logger.debug(msg.format(k, v, attr))

    def dump(self):
        """Dump a product class.

        Parameters
            None

        Return
            :return: a dictionary object containing a copy of the instance
            variables values.
        """
        attributes = {}
        self._logger.info("Dump the product.")
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue  # non-public instance variables are ignored
            else:
                attributes[k] = v
        return attributes

    def check_update(self):
        """checks if a new version is available.

        Parameters
            None.
        """
        raise NotImplementedError

    def fetch_update(self, path):
        """downloads the latest version of the installer

        Parameters
            :param path: is the path name where to store the installer package.
        """
        raise NotImplementedError

    def _temporary_retrieve(self, url, content_type=None):
        """Retrieve a URL into a temporary location on disk.

        Parameters  The catalog is
            :param url: is a string specifying the URL.
            :param content_type: is a string specifying the content type of the
            retrieved resource. If the received type is different, an exception
            BadTypeResource is raised.

        Exceptions
            TypeError: Raised a parameter have an inappropriate type.
            BadTypeResource: Raised when downloaded content-type does not match.
            ContentTooShortError:Raised when downloaded size does not match
            content-length.
            The others exception are the same as for `urllib.request.urlopen()`.

        Return
            :return: a tuple (filename, headers) where filename is the local
            file name, and headers is whatever the info() method of the object
            returned by urlopen() returned.
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

        # default value
        content_length = -1
        length = 0
        result = None

        # retrieve the resource
        msg = "Retrieve '{}'"
        self._logger.debug(msg.format(url))

        with contextlib.closing(urllib.request.urlopen(url)) as stream:
            headers = stream.info()
            if "Content-Type" in headers and content_type is not None:
                if headers["Content-Type"] != content_type:
                    raise BadTypeResource(url, headers["Content-Type"],
                                          content_type)
            if "Content-Length" in headers:
                content_length = int(headers["Content-Length"])
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                self._temp_files.append(temp_file.name)
                result = temp_file.name, headers
                msg = "Retrieve '{}' in '{}'"
                self._logger.debug(msg.format(url, temp_file.name))

                progress_bar = TextProgressBar(content_length)
                progress_bar.compute(length, content_length)
                while True:
                    data = stream.read(4096)
                    if not data:
                        break
                    length += len(data)
                    temp_file.write(data)
                    progress_bar.compute(length, content_length)
                msg = "'{}' retrieved - ".format(url)
                msg = msg + progress_bar.finish()
                self._logger.debug(msg)

        if content_length >= 0 and length < content_length:
            raise ContentTooShortError(url, length, content_length)

        return result

    def _file_retrieve(self, url, dir_name, content_type=None):
        """Retrieve a catalog URL into a location on disk.

        The filename is the same as the name of the retrieved resource.

        Parameters  The catalog is
            :param url: is a string specifying the URL of the catalog.
            :param dir_name: is a string specifying the directory location on
              the disk where the retrieved is going to be written.
            :param content_type: is a string specifying the mime type of the
            retrieved catalog. If the received type is different, a
            BadTypeResource is raised.

        Exceptions
            TypeError: Raised a parameter have an inappropriate type.
            BadTypeResource: Raised when downloaded content-type does not match.
            ContentTooShortError:Raised when downloaded size does not match
            content-length.
            The others exception are the same as for `urllib.request.urlopen()`.

        Return
            :return: a tuple (filename, headers) where filename is the local
            file name, and headers is whatever the info() method
            of the object returned by urlopen() returned.
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
        if content_type is not None:
            if not isinstance(content_type, str):
                msg = "content_type argument must be a class 'str'. not {0}"
                msg = msg.format(content_type.__class__)
                raise TypeError(msg)

        # default value
        content_length = -1
        length = 0
        result = None

        # retrieve the resource
        msg = "Retrieve '{}'"
        self._logger.debug(msg.format(url))

        with contextlib.closing(urllib.request.urlopen(url)) as stream:
            headers = stream.info()
            if "Content-Type" in headers and content_type is not None:
                if headers["Content-Type"] != content_type:
                    raise BadTypeResource(url, headers["Content-Type"],
                                          content_type)
            if "Content-Length" in headers:
                content_length = int(headers["Content-Length"])

            # TODO : treat the exception for os.makedirs
            os.makedirs(dir_name, exist_ok=True)
            basename = os.path.basename(urllib.request.url2pathname(url))
            filename = os.path.join(dir_name, basename)
            part_filename = filename + ".partial"
            with open(part_filename, mode="wb") as file:
                result = filename, headers
                msg = "Retrieve '{}' in '{}'"
                self._logger.debug(msg.format(url, file.name))

                progress_bar = TextProgressBar(content_length)
                progress_bar.compute(length, content_length)
                while True:
                    data = stream.read(4096)
                    if not data:
                        break
                    length += len(data)
                    file.write(data)
                    progress_bar.compute(length, content_length)
                msg = "'{}' retrieved - ".format(url)
                msg = msg + progress_bar.finish()
                self._logger.debug(msg)
            os.replace(part_filename, filename)

        if content_length >= 0 and length < content_length:
            raise ContentTooShortError(url, length, content_length)

        return result

    def _rename_installer(self, filename):
        """Rename the installer executable.

        Installer name match the following format:
        <name>_<version>.<extension>
        name: is the name of the product
        version: is the version of the product
        extension: is the original extension of the download resource.

        Parameters  The catalog is
            :param filename: is a string specifying the local name of the
            installer executable.

        Exceptions
            TypeError: Raised a parameter have an inappropriate type.
            The others exception are the same as for `os.rename`.

        Return
            None.
        """
        # check parameters type
        if not isinstance(filename, str):
            msg = "url argument must be a class 'str'. not {0}"
            msg = msg.format(filename.__class__)
            raise TypeError(msg)

        # Compute the destination name and rename
        basename = os.path.dirname(filename)
        ext = os.path.splitext(filename)[1]
        dest = "{}_{}{}".format(self.name, self.version, ext)
        self.installer = os.path.normpath(os.path.join(basename, dest))
        os.rename(filename, self.installer)


class Error(Exception):
    """Base class for COTS Core exceptions."""

    def __init__(self, message=""):
        """Constructor.

        Parameters
            :param message: is the message explaining the reason of the
            exception raise.
        """
        self.message = message

    def __str__(self):
        return self.message


class ContentTooShortError(Error):
    """Raised when downloaded size does not match content-length."""

    def __init__(self, url, length, content_length):
        """Constructor.

        Parameters
            :param url: is a string specifying the URL.
            :param length: is a positive integer specifying the length of
                received data.
            :param content_length: is a positive integer specifying the content
             length. A negative number specify that the content length is
             unknown.
        """
        msg = "Retrieval incomplete: {0} received bytes vs. {1} waited. \n" \
              "Url '{2}'."
        Error.__init__(self, msg.format(length, content_length, url))
        self.length = length
        self.max_len = content_length
        self.url = url


class BadTypeResource(Error):
    """Raised when downloaded content-type does not match."""

    def __init__(self, url, content_type, waited_content_type):
        """Constructor.

        Parameters
            :param url: is a string specifying the URL.
            :param content_type: is a string specifying the received
            content_type.
            :param waited_content_type: is a string specifying the waited
            content_type.
        """
        msg = "Unexpected content type: '{0}' received vs. '{1}' waited. \n" \
              "Url '{2}'."
        Error.__init__(self, msg.format(content_type, waited_content_type, url))
        self.read_type = content_type
        self.waited_type = waited_content_type
        self.url = url
