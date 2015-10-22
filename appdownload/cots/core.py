"""COTS core module

Classes
    Product : base class for a product

Exception

Function

Constant

"""


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
        published: is the date of the installer’s publication
          (in ISO 8601 format)
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
        silent_inst_arg: arguments to do a silent installation.
        update_available : flag indicating if a new version is available or not.

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

    def __init__(self):
        """Constructor

        Parameters
            None
        """
        self.id = None
        self.name = ""
        self.version = ""
        self.published = ""
        self.target = ""
        self.release_note = ""
        self.installer = ""
        self.std_inst_args = ""
        self.silent_inst_arg = ""
        self.update_available = False

        self._location = ""
        self._catalog_location = ""
        self._product_code = ""

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

