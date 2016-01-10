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
        # (`check_update`) and update downloading (`fetch_update`)
        self.name = "dummy application display name"
        self._catalog_location = "http://www.example.com/index.html"

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
        # Reset the update property to have a up to date products catalog.
        # (i.e. obsolete information may be retrieved during the last checking)
        if self.update is not None:
            del self.update
            self.update = None
        major, minor = self.version.split(".")
        version = "{}.{}".format(major, (int(minor)+1))
        if version > self.version:
            prod = Product()
            prod.version = version
            dt = (datetime.datetime.now()).replace(microsecond=0)
            prod.published = dt.isoformat()
            prod.location = "http://www.example.com/index.html"
            self.update = prod
            msg = "A new version exist ({0}) published on {1}."
            msg = msg.format(self.update.version, self.update.published)
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

        # Update the update object
        prod = self.update
        if prod is not None:
            local_filename, headers = \
                self._file_retrieve(prod.location, path)

            prod.target = ""
            prod.release_note = "http://www.example.com/release_note.txt"
            prod.std_inst_args = ""
            prod.silent_inst_args = "/silent"
            prod.product_code = ""
            prod._rename_installer(local_filename)
            self.load(prod.dump())  # update the current instance
            msg = "Update downloaded in '{}'".format(self.installer)
            self._logger.info(msg)
        else:
            msg = "No new version available."
            self._logger.info(msg)


