"""Implementation of a dummy product class.

Classes
    Product : dummy product class

Exception

Function

Constant

"""


import os
import datetime
import logging

from cots import core


class Product(core.BaseProduct):
    """Dummy product class.

    Public instance variables
        Same as `core.BaseProduct`.

    Public methods
        Same as `core.BaseProduct`.

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None
    """
    def __init__(self, logger=logging.getLogger(__name__)):
        """Constructor

        Parameters
            :param logger: is a logger object

        Exception
            None
        """
        super().__init__(logger)

        # At this point, only name and catalog location are known.
        # All others attributes will be discovered during catalog parsing
        # (`check_update`) and update downloading (`fetch_update`)
        self.name = "dummy application display name"
        self._catalog_location = "http://www.example.com/catalog.xml"

    def check_update(self):
        """checks if a new version is available

        Parameters
            None

        The latest catalog of the product is downloaded and parsed.

        Parameters
            None

        Exceptions
            exception raised by the `_temporary_retrieve` method.
       """
        msg = "Checks if a new version is available. Current version is '{0}'"
        self._logger.info(msg.format(self.version))

        local_filename, headers = \
            self._temporary_retrieve(self._catalog_location)
        msg = "Catalog downloaded: '{0}'".format(local_filename)
        self._logger.debug(msg)

        # Parse the catalog
        # Reset the update properties to have a up to date products catalog.
        # (i.e. obsolete information may be retrieved during the last checking)
        self.update_available = False
        self.update_version = ""
        self.update_published = ""
        self.update_location = ""
        version = "1.1"
        if version > self.version:
            self.update_available = True
            self.update_version = version
            dt = (datetime.datetime.now()).replace(microsecond=0)
            self.update_published = dt.isoformat()
            self.update_location = "http://www.example.com/update.exe"
            msg = "A new version exist ({0}) published on {1}."
            msg = msg.format(self.update_version, self.update_published)
            self._logger.info(msg)
        else:
            msg = "No new version available."
            self._logger.info(msg)

        # clean up the temporary files
        os.unlink(local_filename)

    def fetch_update(self, path):
        """Downloads the latest version of the installer.

        Parameters
            :param path: is the path name where to store the installer package.

        Exceptions
            exception raised by the `_file_retrieve` method.
        """
        msg = "Downloads the latest version of the installer."
        self._logger.info(msg)

        local_filename, headers = \
            self._file_retrieve(self.update_location, path)

        # Update the properties
        self.version = self.update_version
        self.published = self.update_published
        self.target = ""
        self.release_note = "http://www.example.com/release_note.xml"
        self.std_inst_args = ""
        self.silent_inst_args = "/silent"
        self.product_code = ""
        self._rename_installer(local_filename)
        msg = "Update downloaded in '{}'".format(self.installer)
        self._logger.info(msg)

