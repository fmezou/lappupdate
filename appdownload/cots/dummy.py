"""Implementation of a dummy product class

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
    def __init__(self):
        """Constructor

        Parameters
            None
        """
        super().__init__()
        # To make the module as versatile as possible, an nullHandler is added.
        # see 'Configuring Logging for a Library'
        # docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.logger.debug("Instance created")

    def check_update(self):
        """checks if a new version is available

        Parameters
            version: version of the currently deployed product.
            modified: release date of the currently deployed product.
        """
        self.update_available = True
        self.update_version = "1.1"
        dt = (datetime.datetime.now()).replace(microsecond=0)
        self.update_published = dt.isoformat()
        self.logger.debug("An update is available")

    def fetch_update(self, path):
        """downloads the latest version of the installer

        Parameters
            None
        """
        self.id = "dummy"
        self.name = "dummy application display name"
        self.version = "1.0"
        dt = (datetime.datetime.now()).replace(microsecond=0)
        self.published = dt.isoformat()
        self.target = "x64"
        self.release_note = "http://www.example.com/release_note.txt"
        self._location = "http://www.example.com/dummy.zip"
        filename = "aninstaller_{0}.cmd".format(self.version)
        self.installer = os.path.join(path, filename)
        self.std_inst_args = "/STD"
        self.silent_inst_arg = "/SILENT"
        self.logger.debug("An update fetched")

