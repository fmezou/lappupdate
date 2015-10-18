"""Implementation of a dummy product class

Classes
    Product : dummy product class

Exception

Function

Constant

"""


import os
import datetime

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
        self.id = "dummy"
        self.name = "dummy application display name"
        self.version = None
        self.published = None
        self.target = "Unified"
        self.release_note = None
        self.installer = None
        self.std_inst_args = "/STD"
        self.silent_inst_arg = "/SILENT"
        self.update_available = False

        self._location = None
        self._catalog_location = None
        self._product_code = None

    def check_update(self):
        """checks if a new version is available

        Parameters
            version: version of the currently deployed product.
            modified: release date of the currently deployed product.
        """
        print("checks if a new version is available, current version {0} - "
              "released {1}".format(self.version, self.published))
        self.version = "1.0"
        dt = (datetime.datetime.now()).replace(microsecond=0)
        self.published = dt.isoformat()
        self.release_note = "http://www.example.com/release_note.txt"
        self._location = "http://www.example.com/dummy.zip"
        self.update_available = True

    def fetch_update(self):
        """downloads the latest version of the installer

        Parameters
            None
        """
        print("downloads the latest version of the installer.")
        self.installer = r"..\dummy\aninstaller.cmd"

