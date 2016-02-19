"""
Implementation of the MakeMKV product class

Classes
    Product : MakeMKV product class

Exception

Function

Constant

"""


import datetime
import logging

from cots import core
from cots import pad
from cots import semver


# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Product(core.BaseProduct):
    """
    MakeMKV product class.

    Public instance variables
        Same as `core.BaseProduct`.

    Public methods
        Same as `core.BaseProduct`.

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None
    """
    def __init__(self):
        """Constructor

        Parameters
            None

        Exception
            None
        """
        super().__init__()

        # At this point, only name and catalog url are known.
        # All others attributes will be discovered during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "MakeMKV"
        self._catalog_url = "http://www.makemkv.com/makemkv.xml"
        self._parser = pad.PadParser()

    def is_update(self, product):
        """
        Return if this instance is an update of product

        This method compare the version of the two product, and return the
        comparison result. The version numbers used by the editor are compliant
        with the semantic versioning specification 2.0.0 (see `semver`module)

        Parameters
            :param product: is the reference product (i.e. the deployed product)

        Exceptions
            `semver` module exception raised by the rich comparison method of
            SemVer class.

        Returns
            :return: true if this instance is an update of the product specified
            by the `product` parameter.
        """
        # check parameters type
        if not isinstance(product, Product):
            msg = "product argument must be a class 'makemv.product'. not {0}"
            msg = msg.format(product.__class__)
            raise TypeError(msg)

        # comparison based on version number.
        result = False
        if semver.SemVer(self.version) > semver.SemVer(product.version):
            result = True
            msg = "A new version exist ({})."
            _logger.debug(msg.format(self.version))
        else:
            msg = "No new version available."
            _logger.debug(msg)
        return result

    def _parse_catalog(self, filename):
        """
        Parse the catalog.

        This method parses the downloaded product catalog to prepare
        `_get_...` call.
        This catalog is a PAD File (see `pad` module).

        Parameters
            :param filename: is a string specifying the local name of the
            downloaded product catalog.

        Exceptions
            pad module exception raised by the `parse` method.
         """
        self._parser.parse(filename)

    def _get_name(self):
        """
        Extract the name of the product (used in a_report mail and log file).

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.name = None
        path = "Program_Info/Program_Name"
        item = self._parser.find(path)
        if item is not None:
            self.name = item.text
            msg = "Product name :'{0}'"
            _logger.debug(msg.format(self.name))
        else:
            msg = "Unknown product name"
            _logger.warning(msg)

    def _get_display_name(self):
        """
        Extract the name of the product as it appears in the 'Programs and
        Features' control panel.

        This name is built from the name and the version attribute, thus this
        method must be called after `_get_name` and `_get_version`.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        name = "{} v{}"
        self.display_name = name.format(self.name, self.version)

    def _get_version(self):
        """
        Extract the current version of the product from the PAD File.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.version = None
        path = "Program_Info/Program_Version"
        item = self._parser.find(path)
        if item is not None:
            self.version = item.text
            msg = "Product version :'{0}'"
            _logger.debug(msg.format(self.version))
        else:
            msg = "Unknown product version"
            _logger.warning(msg)

    def _get_published(self):
        """
        Extract the date of the installer’s publication from the PAD file.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.        """
        self.published = None
        path = "Program_Info/Program_Release_Year"
        item = self._parser.find(path)
        if item is not None:
            year = int(item.text)
            path = "Program_Info/Program_Release_Month"
            item = self._parser.find(path)
            if item is not None:
                month = int(item.text)
                path = "Program_Info/Program_Release_Day"
                item = self._parser.find(path)
                if item is not None:
                    day = int(item.text)
                    self.published = datetime.date(year, month, day).isoformat()
                    msg = "Release date :'{0}'"
                    _logger.debug(msg.format(self.published))
                else:
                    msg = "Unknown release day"
                    _logger.warning(msg)
            else:
                msg = "Unknown release month"
                _logger.warning(msg)
        else:
            msg = "Unknown release year"
            _logger.warning(msg)

    def _get_description(self):
        """
        Extract the short description of the product (~250 characters).

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.description = None
        path = "Program_Descriptions/English/Char_Desc_250"
        item = self._parser.find(path)
        if item is not None:
            self.description = item.text
            msg = "Product description :'{0}'"
            _logger.debug(msg.format(self.description))
        else:
            msg = "Unknown product description"
            _logger.warning(msg)

    def _get_editor(self):
        """
        Extract the name of the editor of the product.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.editor = None
        path = "Company_Info/Company_Name"
        item = self._parser.find(path)
        if item is not None:
            self.editor = item.text
            msg = "Product editor :'{0}'"
            _logger.debug(msg.format(self.editor))
        else:
            msg = "Unknown product editor"
            _logger.warning(msg)

    def _get_url(self):
        """
        Extract the url of the current version of the installer

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.url = None
        path = "Web_Info/Download_URLs/Primary_Download_URL"
        item = self._parser.find(path)
        if item is not None:
            self.url = item.text
            msg = "Download url (for windows version) :'{0}'"
            _logger.debug(msg.format(self.url))
        else:
            msg = "Unknown Download url"
            _logger.warning(msg)

    def _get_file_size(self):
        """
        Extract the size of the product installer expressed in bytes

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.file_size = None
        # path = "Program_Info/File_Info/File_Size_Bytes"
        # item = self._parser.find(path)
        # if item is not None:
        #     self.file_size = int(item.text)
        #     msg = "File size :'{0}'"
        #     _logger.debug(msg.format(self.file_size))
        # else:
        #     msg = "Unknown File size"
        #     _logger.warning(msg)

    def _get_hash(self):
        """
        Extract the secure_hash value of the product installer (tuple).

        The PAD file doesn't specify a secure_hash for the installer product.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.secure_hash = None

    def _get_icon(self):
        """
        Extract the name of the icon file.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.icon = None
        path = "Web_Info/Application_URLs/Application_Icon_URL"
        item = self._parser.find(path)
        if item is not None:
            self.icon = item.text
            msg = "Icon file :'{0}'"
            _logger.debug(msg.format(self.icon))
        else:
            msg = "Unknown icon"
            _logger.warning(msg)

    def _get_target(self):
        """
        Extract the target architecture type (the Windows’ one).

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.target = core.PROD_TARGET_UNIFIED
        msg = "Target :'{0}'"
        _logger.debug(msg.format(self.icon))

    def _get_release_note(self):
        """
        Extract the release note’s URL from the PAD File.
        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.release_note = "http://www.makemkv.com/download/history.html"
        msg = "Release note :'{0}'"
        _logger.debug(msg.format(self.release_note))

    def _get_std_inst_args(self):
        """
        Extract the arguments to use for a standard installation.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.std_inst_args = ""
        msg = "Standard installation options :'{0}'"
        _logger.debug(msg.format(self.std_inst_args))

    def _get_silent_inst_args(self):
        """
        Extract the arguments to use for a silent installation.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.silent_inst_args = "/S"
        msg = "Silent installation option :'{0}'"
        _logger.debug(msg.format(self.silent_inst_args))
