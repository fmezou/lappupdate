"""
This module specifies the metadata of the project to avoid duplicating theses
values across sources files. It’s one of the technique proposed in the
`Single-sourcing the Project Version`_  of the `Python Packaging User Guide`_.

The easiest way to use is to import the module as below.

>>> from version import __version__
>>> __version__
'0.1.0-dev.0'

>>> from version import *
>>> __license__
'GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007'

.. _Single-sourcing the Project Version: https://packaging.python.org/
    single_source_version/#single-sourcing-the-project-version
.. _Python Packaging User Guide: https://packaging.python.org/
"""

__project__ = "lAppDownload"
__version__ = "0.1.0-dev.0"
__author__ = "Frederic MEZOU"
__author_email__= "frederic.mezou@example.com"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__copyright__ = "2016, Frederic MEZOU"
__description__ = "Tracks and downloads application installers or its update."

__all__ = [
    "__project__",
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
    "__description__"
]

