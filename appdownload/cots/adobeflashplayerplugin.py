"""Implementation of Product class for Adobe Flash Player Plug-in

Classes
    Product : base class for a product

Exception

Function

Constant

"""

from cots import adobeflashplayer


class Product(adobeflashplayer.Product):
    """Adobe Flash Player Plug-in derived Product class.

    Public instance variables
        name: name of the product
        version: current version of the product
        modified: modification date of the installer
        filename: filename of the installer (full path)
        inst_args: arguments to do a standard installation.
        silent_inst_arg: arguments to do a silent installation.

    Public methods
        None

    """
    _TITLE = "Adobe Flash Player"
    _PRODUCT_NAME = "Adobe Flash Player 32-bit/64-bit Plugin"
    _DISPLAY_NAME = "Adobe Flash Player %n NAPI"
    pass
