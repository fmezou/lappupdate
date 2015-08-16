"""COTS core module

Classes
    Product : base class for a product

Exception

Function

Constant

"""


__all__ = [
    "Product"
]


class Product:
    """Product base class.

    Public instance variables
        name: name of the product
        update_available : flag indicating if a new version is available or not.
        version: current version of the product
        modified: modification date of the installer
        location: url of the latest version of the product
        installer: filename of the installer (local full path)
        std_inst_args: arguments to do a standard installation.
        silent_inst_arg: arguments to do a silent installation.
        product_code: (future) UID of the product (see MSI product code)
        display_name: name of the application as it appears in the Program
          Control Panel.

    Public methods
        None

    Subclass API variables (i.e. may be use by subclass)
        _catalog_location: location (url) of the product catalog.

    Subclass API Methods (i.e. must be overwritten by subclass)
        check_update: checks if a new version is available
        fetch_update: downloads the latest version of the installer
    """

    def __init__(self):
        """Constructor

        Parameters
            None
        """
        self.name = None
        self.update_available = False
        self.version = None
        self.modified = None
        self.location = None
        self.installer = None
        self.std_inst_args = None
        self.silent_inst_arg = None
        self.product_code = None
        self.display_name = None

        self._catalog_location = None

    def check_update(self, version=None, modified=None):
        """checks if a new version is available

        Parameters
            version: version of the currently deployed product.
            modified: release date of the currently deployed product.
        """
        raise NotImplementedError

    def fetch_update(self):
        """downloads the latest version of the installer

        Parameters
            None
        """
        raise NotImplementedError
