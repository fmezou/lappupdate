"""
This module defines a test suite for testing product handlers.
"""

import logging
import unittest

from cots import core

__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "HandlerTestCase",
    "MozillaHandlerTestCase"
]

# Modules to be tested use the logging facility, so a minimal
# configuration is set. To avoid side effects with the `unittest`
# console output, log entries are written in a file.
logging.basicConfig(
    format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
    filename="test_handler.log",
    filemode="a",
    level=logging.DEBUG)
_logger = logging.getLogger(__name__)


class HandlerTestCase(unittest.TestCase):
    """
    Product handler test suite

    This class implements additional mechanism.
    """
    #: list: List of the product handlers to test, each item is the qualified
    #: name of the handler class.
    qualnames = [
        "cots.makemkv.MakeMKVHandler",
    ]

    def setUp(self):
        _logger.info(53*"-")

    def tearDown(self):
        _logger.info(50*"-")
        # Clean up

    def test0001_get_origin(self):
        # Get product information from the remote repository.
        _logger.info("Starting...")
        for qualname in self.qualnames:
            name = (qualname.split("."))[-1:]
            _logger.info("(handler=%s)", name)
            with self.subTest(name=name):
                handler = core.get_handler(qualname)
                _logger.info(handler)
                result = handler.get_origin()
                self.assertTrue(result, "get_origin() failed")
                _logger.info(str(handler))
                del handler
        _logger.info("Completed")

    def test0002_loop_get_origin(self):
        # Get product information from the remote repository.
        _logger.info("Starting...")
        for qualname in self.qualnames:
            name = (qualname.split("."))[-1:]
            _logger.info("(handler=%s)", name)
            with self.subTest(name=name):
                handler = core.get_handler(qualname)
                _logger.info(str(handler))
                print("{} published on {}".format(handler.display_name,
                                                  handler.published))
                result = handler.get_origin()
                while result:
                    _logger.info(str(handler))
                    v = handler.version
                    print(" * UPDATE: {} published on {}".format(
                        handler.display_name, handler.published))
                    result = handler.get_origin()
                    if result:
                        _logger.info(str(handler))
                        if handler.version == v:
                            result = False
        _logger.info("Completed")

    def test0100_fetch_primary_version(self):
        # Download the primary version of the product installer..
        _logger.info("Starting...")
        for qualname in self.qualnames:
            name = (qualname.split("."))[-1:]
            _logger.info("(handler=%s)", name)
            with self.subTest(name=name):
                handler = core.get_handler(qualname)
                result = handler.fetch("../~store/app")
                self.assertTrue(result, "fetch() failed")
                _logger.info(str(handler))
        _logger.info("Completed")

    def test0101_fetch_latest_release(self, ):
        # Download the latest release of the product installer..
        _logger.info("Starting...")
        for qualname in self.qualnames:
            name = (qualname.split("."))[-1:]
            _logger.info("(handler=%s)", name)
            with self.subTest(name=name):
                handler = core.get_handler(qualname)
                result = handler.get_origin(version=handler.version)
                self.assertTrue(result, "get_origin() failed")
                result = handler.fetch("../~store/app")
                self.assertTrue(result, "fetch() failed")
                _logger.info(str(handler))
        _logger.info("Completed")

    def test_is_update(self, ):
        # Check if the remote version is an update.
        _logger.info("Starting...")
        for qualname in self.qualnames:
            name = (qualname.split("."))[-1:]
            _logger.info("(handler=%s)", name)
            with self.subTest(name=name):
                handler = core.get_handler(qualname)
                result = handler.get_origin(version=handler.version)
                self.assertTrue(result, "get_origin() failed")

                # The current version is not an update of itself.
                result = handler.is_update(handler)
                self.assertFalse(result,
                                 "The current version must not be an update "
                                 "of itself")

                previous = core.get_handler(qualname)
                result = handler.is_update(previous)
                self.assertTrue(result,
                                "The remote version must be an update")
                _logger.info(str(handler))
        _logger.info("Completed")


class MozillaHandlerTestCase(HandlerTestCase):
    """
    Mozilla handler test suite
    """
    #: list: List of the Mozilla handlers to test, each item is the qualified
    #: name of the handler class.
    qualnames = [
        "cots.mozilla.FirefoxWinHandler",
        "cots.mozilla.FirefoxWin64Handler",
        "cots.mozilla.ThunderbirdWinHandler"
    ]

if __name__ == '__main__':
    unittest.main()
