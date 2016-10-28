"""Implementation of Product class for Adobe Flash Player ActiveX

Classes
    Product : base class for a product

Exceptions

Functions

Constants

"""

from cots import adobeflashplayer


__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


class Product(adobeflashplayer.Product):
    """Adobe Flash Player for Internet Explorer edition derived Product class.

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
    _PRODUCT_NAME = "Adobe Flash Player 32-bit/64-bit ActiveX"
    _DISPLAY_NAME = "Adobe Flash Player %n ActiveX"
    pass


