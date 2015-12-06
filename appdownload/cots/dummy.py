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
            :param logger : is a logger object
        """
        super().__init__(logger)
        # set the default value
        self.id = "dummy"
        self.name = "dummy application display name"
        self.target = "x64"
        self.release_note = "http://www.example.com/release_note.txt"
        self.std_inst_args = "/STD"
        self.silent_inst_args = "/SILENT"

    def check_update(self):
        """checks if a new version is available

        Parameters
            None
        """
        msg = "Checks if a new version is available. " \
              "Current version is '{0}'".format(self.version)
        self._logger.info(msg)

        self.update_available = True
        self.update_version = "1.1"
        dt = (datetime.datetime.now()).replace(microsecond=0)
        self.update_published = dt.isoformat()

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

