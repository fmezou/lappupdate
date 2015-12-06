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
import urllib.request

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
        """
        super().__init__(logger)
        # set the default value
        self.id = "dummy"
        self.name = "dummy application display name"
        self.target = "x64"
        self.release_note = "http://www.example.com/release_note.txt"
        self.std_inst_args = "/STD"
        self.silent_inst_args = "/SILENT"

        self._catalog_location = "http://www.makemkv.com/makemkv.xml"
        self._parser = pad.PadParser()

    def check_update(self):
        """checks if a new version is available

        Parameters
            None
        """
        msg = "Checks if a new version is available. " \
              "Current version is '{0}'".format(self.version)
        self._logger.info(msg)

        local_filename, headers = \
            urllib.request.urlretrieve(self._catalog_location)
        msg = "Catalog downloaded: '{0}'".format(local_filename)
        self._logger.debug(msg)

        #check
        self._parser.parse(local_filename)
        version = self._get_version()
        if version is not None:
            # TODO: do a real comparison based on semver specs
            if version > self.version:
                self.update_available = True
                self.update_version = version
                self.update_published = self._get_release_date()
                self.update_location = self._get_location()
        else:
            msg = "Unknown program version"
            self._logger.warning(msg)

        urllib.request.urlcleanup()

        if self.update_available:
            msg = "A new version exist ({0}) published " \
                  "on {1}.".format(self.update_version, self.update_published)
            self._logger.info(msg)
        else:
            self._logger.info("No new version available.")

    def fetch_update(self, path):
        """downloads the latest version of the installer

        Parameters
            :param path: is the path name where to store the installer package.
        """
        self.version = "1.0"
        dt = (datetime.datetime.now()).replace(microsecond=0)
        self.published = dt.isoformat()
        self.target = "x64"
        self.release_note = "http://www.example.com/release_note.txt"
        self.update_location = "http://www.example.com/dummy.zip"
        filename = "aninstaller_{0}.cmd".format(self.version)
        self.installer = os.path.join(path, filename)
        self.std_inst_args = "/STD"
        self.silent_inst_args = "/SILENT"
        msg = "New version of fetched. saved as '{0}'."\
              .format(self.installer)
        self._logger.info(msg)

    def _get_version(self):
        """Get the version from the PAD File.

        :return: a string specifying the version or None.
        """
        version = None
        path="Program_Info/Program_Version"
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
        path="Program_Info/Program_Release_Year"
        item = self._parser.find(path)
        if item is not None:
            year = int(item.text)
            path="Program_Info/Program_Release_Month"
            item = self._parser.find(path)
            if item is not None:
                month = int(item.text)
                path="Program_Info/Program_Release_Day"
                item = self._parser.find(path)
                if item is not None:
                    day = int(item.text)
                    dt=datetime.date(year, month, day)
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
        path="Web_Info/Download_URLs/Primary_Download_URL"
        item = self._parser.find(path)
        if item is not None:
            location = item.text
            msg = "Download url (for windows version) :'{0}'"
            self._logger.info(msg.format(location))
        else:
            msg = "Unknown Download url"
            self._logger.warning(msg)
        return location
