"""Implementation of the MakeMKV product class

Classes
    Product : MakeMKV product class

Exception

Function

Constant

"""


import os
import datetime
import logging

from cots import core
from cots import pad
from cots import semver


class Product(core.BaseProduct):
    """MakeMKV product class.

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

        # To make the module as versatile as possible, an nullHandler is added.
        # see 'Configuring Logging for a Library'
        # docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
        self._logger = logging.getLogger(__name__)
        self._logger.addHandler(logging.NullHandler())
        self._logger.debug("Instance created.")

        # At this point, only name and catalog location are known.
        # All others attributes will be discovered during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "MakeMKV"
        self._catalog_location = "http://www.makemkv.com/makemkv.xml"
        self._parser = pad.PadParser()

    def get_origin(self, version=None):
        """Get product information from the remote repository.

        The latest catalog of the product is downloaded and parsed.
        This catalog is a PAD File (see `pad` module).

        Parameters
            :param version: is the version of the reference product (i.e. the
            deployed product). It'a string following the editor rule.
            Not used here.

        Exceptions
            pad module exception raised by the `parse` method.
            exception raised by the `_temporary_retrieve` method.
        """
        # check parameters type
        if version is not None and not isinstance(version, str):
            msg = "version argument must be a class 'str' or None. not {0}"
            msg = msg.format(version.__class__)
            raise TypeError(msg)

        msg = "Get the latest product information. Current version is '{0}'"
        self._logger.debug(msg.format(self.version))

        local_filename, headers = \
            self._temporary_retrieve(self._catalog_location)
        msg = "Catalog downloaded: '{0}'".format(local_filename)
        self._logger.debug(msg)

        # Parse the catalog based on a PAD File
        self._parser.parse(local_filename)
        self._get_name()
        self._get_version()
        self._get_display_name()
        self._get_published()
        self._get_description()
        self._get_editor()
        self._get_location()
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
        """Downloads the product installer.

        Parameters
            :param path: is the path name where to store the installer package.

        Exceptions
            exception raised by the `_file_retrieve` method.
        """
        msg = "Downloads the latest version of the installer."
        self._logger.debug(msg)

        # Update the update object
        local_filename, headers = \
            self._file_retrieve(self.location, path)
        self._rename_installer(local_filename)
        msg = "Update downloaded in '{}'".format(self.installer)
        self._logger.debug(msg)

    def is_update(self, product):
        """ Return if this instance is an update of product

        This method compare the version of the two product, and return the
        comparison result. The version numbers used by the editor are compliant
        with the semantic versioning specification 2.0.0 (see `semver`module)

        Parameters
            :param product: is the reference product (i.e. the deployed product)

        Exceptions
            pad module exception raised by the `parse` method.
            exception raised by the `_temporary_retrieve` method.

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
            self._logger.debug(msg.format(self.version))
        else:
            msg = "No new version available."
            self._logger.debug(msg)
        return result

    def _get_name(self):
        """Extract the name of the product (used in report mail and log file).

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
            self._logger.debug(msg.format(self.name))
        else:
            msg = "Unknown product name"
            self._logger.warning(msg)

    def _get_display_name(self):
        """Extract the name of the product as it appears in the 'Programs and
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
        """Extract the current version of the product from the PAD File.

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
            self._logger.debug(msg.format(self.version))
        else:
            msg = "Unknown product version"
            self._logger.warning(msg)

    def _get_published(self):
        """Extract the date of the installer’s publication from the PAD file.

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
                    self._logger.debug(msg.format(self.published))
                else:
                    msg = "Unknown release day"
                    self._logger.warning(msg)
            else:
                msg = "Unknown release month"
                self._logger.warning(msg)
        else:
            msg = "Unknown release year"
            self._logger.warning(msg)

    def _get_description(self):
        """Extract the short description of the product (~250 characters).

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
            self._logger.debug(msg.format(self.description))
        else:
            msg = "Unknown product description"
            self._logger.warning(msg)

    def _get_editor(self):
        """Extract the name of the editor of the product.

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
            self._logger.debug(msg.format(self.editor))
        else:
            msg = "Unknown product editor"
            self._logger.warning(msg)

    def _get_location(self):
        """Extract the location (url) of the current version of the installer

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.location = None
        path = "Web_Info/Download_URLs/Primary_Download_URL"
        item = self._parser.find(path)
        if item is not None:
            self.location = item.text
            msg = "Download url (for windows version) :'{0}'"
            self._logger.debug(msg.format(self.location))
        else:
            msg = "Unknown Download url"
            self._logger.warning(msg)

    def _get_file_size(self):
        """Extract the size of the product installer expressed in bytes

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.file_size = None
        path = "Program_Info/File_Info/File_Size_Bytes"
        item = self._parser.find(path)
        if item is not None:
            self.file_size = int(item.text)
            msg = "File size :'{0}'"
            self._logger.debug(msg.format(self.file_size))
        else:
            msg = "Unknown File size"
            self._logger.warning(msg)

    def _get_hash(self):
        """Extract the hash value of the product installer (tuple).

        The PAD file doesn't specify a hash for the installer product.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.hash = None

    def _get_icon(self):
        """Extract the name of the icon file.

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
            self._logger.debug(msg.format(self.icon))
        else:
            msg = "Unknown icon"
            self._logger.warning(msg)

    def _get_target(self):
        """Extract the target architecture type (the Windows’ one).

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.target = core.PROD_TARGET_UNIFIED
        msg = "Target :'{0}'"
        self._logger.debug(msg.format(self.icon))

    def _get_release_note(self):
        """Extract the release note’s URL from the PAD File.
        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.release_note = "http://www.makemkv.com/download/history.html"
        msg = "Release note :'{0}'"
        self._logger.debug(msg.format(self.release_note))

    def _get_std_inst_args(self):
        """Extract the arguments to use for a standard installation.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.std_inst_args = ""
        msg = "Standard installation options :'{0}'"
        self._logger.debug(msg.format(self.std_inst_args))

    def _get_silent_inst_args(self):
        """Extract the arguments to use for a silent installation.

        Parameters
            None.

        Exceptions
            None.

        Return
            None.
        """
        self.silent_inst_args = "/S"
        msg = "Silent installation option :'{0}'"
        self._logger.debug(msg.format(self.silent_inst_args))
