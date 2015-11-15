"""COTS core module

Classes
    Product : base class for a product

Exception

Function

Constant

"""

import logging


__all__ = [
    "BaseProduct"
]


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

    Public methods
        None

    Subclass API variables (i.e. may be use by subclass)
        _location: location (url) of the last version of the installer.
        _catalog_location: location (url) of the product catalog.
        _product_code: UID of the product (see MSI product code)

    Subclass API Methods (i.e. must be overwritten by subclass)
        check_update: checks if a new version is available
        fetch_update: downloads the latest version of the installer
    """

    def __init__(self, logger=logging.getLogger(__name__)):
        """Constructor

        Parameters
            logger : is a logger object
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

        self._location = ""
        self._catalog_location = ""
        self._product_code = ""

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
        # attrib
        """Load a product class.

        Parameters
            attributes: is a dictionary object containing the instance
            variables values.
            If attributes is not present or have the None value, instance
            variables keep to their default values.
            Key value pairs which don't exist in the instance variables
            dictionary are ignored.
        """
        if attributes is not None:
            # check parameters type
            if not isinstance(attributes, dict):
                msg = "props argument must be a class 'dict'. not {0}"
                msg = msg.format(attributes.__class__)
                raise TypeError(msg)

        # set instance variables
        self._logger.info("Load the product.")
        for k,v in self.__dict__.items():
            if k.startswith('_'):
                continue # non-public instance variables are ignored
            else:
                attr = attributes.get(k)
                if attr is not None:
                    self.__dict__[k]=attributes.get(k)
                    msg = "Instance variables '{0}' : " \
                          "'{1}' -> '{2}'".format(k, v, attr)
                    self._logger.debug(msg)

    def dump(self):
        """Dump a product class.

        Parameters
            None

        Return
            attributes: is a dictionary object containing a copy of the instance
            variables values.
        """
        attributes = {}
        self._logger.info("Dump the product.")
        for k,v in self.__dict__.items():
            if k.startswith('_'):
                continue  # non-public instance variables are ignored
            else:
                attributes[k] = v
        return attributes

    def check_update(self):
        """checks if a new version is available

        Parameters
            None.
        """
        raise NotImplementedError

    def fetch_update(self, path):
        """downloads the latest version of the installer

        Parameters
            path: is the path name where to store the installer package.
        """
        raise NotImplementedError
