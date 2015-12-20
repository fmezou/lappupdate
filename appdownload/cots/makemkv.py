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


class Product(core.BaseProduct):
    """MakeMKV product class.

    Public instance variables
        .

    Public methods
        None

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
        self.id = "makemkv"
        self.name = "MakeMKV"
        self._catalog_location = "http://www.makemkv.com/makemkv.xml"
        self._parser = pad.PadParser()

    def check_update(self):
        """Checks if a new version is available.

        The latest catalog of the product is downloaded and parsed.
        This catalog is a PAD File (see `pad` module).

        Parameters
            None

        Exceptions
            pad module exception raised by the `parse` method.
            exception raised by the `_temporary_retrieve` method.
        """
        msg = "Checks if a new version is available. " \
              "Current version is '{0}'".format(self.version)
        self._logger.info(msg)

        local_filename, headers = \
            self._temporary_retrieve(self._catalog_location)
        msg = "Catalog downloaded: '{0}'".format(local_filename)
        self._logger.debug(msg)

        # Parse the catalog based on a PAD File
        # Reset the update properties to have a up to date products catalog.
        # (i.e. obsolete information may be retrieved during the last checking)
        self.update_available = False
        self.update_version = ""
        self.update_published = ""
        self.update_location = ""
        self._parser.parse(local_filename)
        version = self._get_version()
        if version is not None:
            # TODO: do a comparison based on semantic versioning specification
            if version > self.version:
                self.update_available = True
                self.update_version = version
                self.update_published = self._get_release_date()
                self.update_location = self._get_location()
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
        # fixme: an other solution is to create an other product object for the
        # updated one and to link it into the current object.
        self.name = "MakeMKV"
        self.version = self.update_version
        self.published = self.update_published
        self.target = ""
        self.release_note = self._get_release_note()
        self.std_inst_args = ""
        self.silent_inst_args = "/S"
        self.product_code = ""
        self._rename_installer(local_filename)
        msg = "Update downloaded in '{}'".format(self.installer)
        self._logger.info(msg)

    def _get_version(self):
        """Get the version from the PAD File.

        :return: a string specifying the version or None.
        """
        version = None
        path = "Program_Info/Program_Version"
        item = self._parser.find(path)
        if item is not None:
            version = item.text
            msg = "Program version :'{0}'"
            self._logger.info(msg.format(version))
        else:
            msg = "Unknown program version"
            self._logger.warning(msg)
        return version

    def _get_release_date(self):
        """Get the release date from the PAD File.

        :return: a string specifying the release date in ISO format or None.
        """
        release_date = None
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
                    dt = datetime.date(year, month, day)
                    release_date = dt.isoformat()
                    msg = "Release date :'{0}'"
                    self._logger.info(msg.format(release_date))
                else:
                    msg = "Unknown release day"
                    self._logger.warning(msg)
            else:
                msg = "Unknown release month"
                self._logger.warning(msg)
        else:
            msg = "Unknown release year"
            self._logger.warning(msg)

        return release_date

    def _get_release_note(self):
        """Get the release note URL from the PAD File.

        :return: a string specifying the URL or None.
        """
        release_note = "http://www.makemkv.com/download/"
        msg = "Release note :'{0}'"
        self._logger.info(msg.format(release_note))
        return release_note

    def _get_location(self):
        """Get the location from the PAD File.

        :return: a string specifying the version or None.
        """
        location = None
        path = "Web_Info/Download_URLs/Primary_Download_URL"
        item = self._parser.find(path)
        if item is not None:
            location = item.text
            msg = "Download url (for windows version) :'{0}'"
            self._logger.info(msg.format(location))
        else:
            msg = "Unknown Download url"
            self._logger.warning(msg)
        return location
