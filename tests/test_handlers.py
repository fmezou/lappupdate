"""
This module defines a test suite for testing product handlers.
"""

import logging
import unittest

from cots import core
from cots import mozilla

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

    def test0201_is_update(self, ):
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


class MozVerTestCase(unittest.TestCase):
    def setUp(self):
        _logger.info(53*"-")

    def tearDown(self):
        _logger.info(50*"-")

    def test0101_left_op(self):
        # Left operand testing
        _logger.info("Starting...")
        exprs = [
            "v == 0",
            "v != 0",
            "v < 0",
            "v > 0"
        ]
        v = mozilla.MozVer("1.0")
        for expr in exprs:
            _logger.info("(expr=%s)", expr)
            with self.subTest(expr=expr):
                with self.assertRaises(TypeError):
                    eval(expr)
        _logger.info("Completed")

    def test0201_beta_version(self):
        # Beta version
        _logger.info("Starting...")
        msg = "(a|alpha|b|beta|pre|rc) at the end of string is for beta " \
              "version."
        v = mozilla.MozVer("1.1a")
        self.assertTrue(v.unstable, msg=msg)
        v = mozilla.MozVer("1.1alpha1")
        self.assertTrue(v.unstable, msg=msg)
        v = mozilla.MozVer("1.1b1")
        self.assertTrue(v.unstable, msg=msg)
        v = mozilla.MozVer("1.1beta1")
        self.assertTrue(v.unstable, msg=msg)
        v = mozilla.MozVer("1.1pre1")
        self.assertTrue(v.unstable, msg=msg)
        v = mozilla.MozVer("1.1rc1")
        self.assertTrue(v.unstable, msg=msg)

        v = mozilla.MozVer("1.0")
        self.assertFalse(v.unstable, msg=msg)
        v = mozilla.MozVer("1.0release0")
        self.assertFalse(v.unstable, msg=msg)
        v = mozilla.MozVer("1.0rc0.1")
        self.assertFalse(v.unstable, msg=msg)
        _logger.info("Completed")

    def test0202_beta_precedence(self):
        # Beta version precedence
        _logger.info("Starting...")
        msg = "Beta versions have a lower precedence than the " \
              "associated normal version"
        v1 = mozilla.MozVer("1.0alpha1")
        v2 = mozilla.MozVer("1.0")
        self.assertTrue(v1 < v2, msg=msg)
        self.assertFalse(v1 > v2, msg=msg)
        self.assertTrue(v2 > v1, msg=msg)
        self.assertFalse(v2 < v1, msg=msg)
        _logger.info("Completed")

    def test0301_precedence(self):
        # Precedence rules
        # see line 2 of the example in the reference.
        _logger.info("Starting...")
        msg = "Precedence is determined by the first difference when " \
              "comparing each of these identifiers from left to right."
        v1 = mozilla.MozVer("1")
        v2 = mozilla.MozVer("1.")
        v3 = mozilla.MozVer("1.0")
        v4 = mozilla.MozVer("1.0.0")
        self.assertTrue(v1 == v2, msg=msg)
        self.assertTrue(v2 == v3, msg=msg)
        self.assertTrue(v3 == v4, msg=msg)
        self.assertFalse(v1 != v2, msg=msg)
        self.assertFalse(v2 != v3, msg=msg)
        self.assertFalse(v3 != v4, msg=msg)
        _logger.info("Completed")

    def test0302_precedence(self):
        # Precedence rules
        # see line 3 of the example in the reference.
        _logger.info("Starting...")
        msg = "Precedence is determined by the first difference when " \
              "comparing each of these identifiers from left to right."
        v1 = mozilla.MozVer("1.1a")
        v2 = mozilla.MozVer("1.1aa")
        v3 = mozilla.MozVer("1.1ab")
        v4 = mozilla.MozVer("1.1b")
        v5 = mozilla.MozVer("1.1c")
        self.assertTrue(v1 < v2, msg=msg)
        self.assertTrue(v2 < v3, msg=msg)
        self.assertTrue(v3 < v4, msg=msg)
        self.assertTrue(v4 < v5, msg=msg)
        self.assertTrue(v5 > v4, msg=msg)
        self.assertTrue(v4 > v3, msg=msg)
        self.assertTrue(v3 > v2, msg=msg)
        self.assertTrue(v2 > v1, msg=msg)

        self.assertFalse(v1 > v2, msg=msg)
        self.assertFalse(v2 > v3, msg=msg)
        self.assertFalse(v3 > v4, msg=msg)
        self.assertFalse(v4 > v5, msg=msg)
        self.assertFalse(v5 < v4, msg=msg)
        self.assertFalse(v4 < v3, msg=msg)
        self.assertFalse(v3 < v2, msg=msg)
        self.assertFalse(v2 < v1, msg=msg)
        _logger.info("Completed")

    def test0303_precedence(self):
        # Precedence rules
        # see line 4 of the example in the reference.
        _logger.info("Starting...")
        msg = "Precedence is determined by the first difference when " \
              "comparing each of these identifiers from left to right."
        v1 = mozilla.MozVer("1.1pre")
        v2 = mozilla.MozVer("1.1pre0")
        v3 = mozilla.MozVer("1.0+")
        self.assertTrue(v1 == v2, msg=msg)
        self.assertTrue(v2 == v3, msg=msg)
        self.assertFalse(v1 != v2, msg=msg)
        self.assertFalse(v2 != v3, msg=msg)
        _logger.info("Completed")

    def test0304_precedence(self):
        # Precedence rules
        # see line 5 of the example in the reference.
        _logger.info("Starting...")
        msg = "Precedence is determined by the first difference when " \
              "comparing each of these identifiers from left to right."
        v1 = mozilla.MozVer("1.1pre1a")
        v2 = mozilla.MozVer("1.1pre1aa")
        v3 = mozilla.MozVer("1.1pre1b")
        v4 = mozilla.MozVer("1.1pre1")
        self.assertTrue(v1 < v2, msg=msg)
        self.assertTrue(v2 < v3, msg=msg)
        self.assertTrue(v3 < v4, msg=msg)
        self.assertTrue(v4 > v3, msg=msg)
        self.assertTrue(v3 > v2, msg=msg)
        self.assertTrue(v2 > v1, msg=msg)

        self.assertFalse(v1 > v2, msg=msg)
        self.assertFalse(v2 > v3, msg=msg)
        self.assertFalse(v3 > v4, msg=msg)
        self.assertFalse(v4 < v3, msg=msg)
        self.assertFalse(v3 < v2, msg=msg)
        self.assertFalse(v2 < v1, msg=msg)
        _logger.info("Completed")

    def test0305_precedence(self):
        # Precedence rules
        # see line 9 of the example in the reference.
        _logger.info("Starting...")
        msg = "Precedence is determined by the first difference when " \
              "comparing each of these identifiers from left to right."
        v1 = mozilla.MozVer("1.1")
        v2 = mozilla.MozVer("1.1.0")
        v3 = mozilla.MozVer("1.1.00")
        self.assertTrue(v1 == v2, msg=msg)
        self.assertTrue(v2 == v3, msg=msg)
        self.assertFalse(v1 != v2, msg=msg)
        self.assertFalse(v2 != v3, msg=msg)
        _logger.info("Completed")

    def test0306_precedence(self):
        # Precedence rules
        # see line 11 of the example in the reference.
        _logger.info("Starting...")
        msg = "Precedence is determined by the first difference when " \
              "comparing each of these identifiers from left to right."
        v1 = mozilla.MozVer("1.*")
        v2 = mozilla.MozVer("1.*.1")
        self.assertTrue(v1 < v2, msg=msg)
        self.assertTrue(v2 > v1, msg=msg)

        self.assertFalse(v1 > v2, msg=msg)
        self.assertFalse(v2 < v1, msg=msg)
        _logger.info("Completed")

    def test0307_precedence(self):
        # Precedence rules
        # see the example in the reference.
        _logger.info("Starting...")
        msg = "Precedence is determined by the first difference when " \
              "comparing each of these identifiers from left to right."
        v1 = mozilla.MozVer("1.-1")
        v2 = mozilla.MozVer("1")
        v3 = mozilla.MozVer("1.1a")
        v4 = mozilla.MozVer("1.1pre")
        v5 = mozilla.MozVer("1.1pre1a")
        v6 = mozilla.MozVer("1.1pre2")
        v7 = mozilla.MozVer("1.1pre10")
        v8 = mozilla.MozVer("1.1.-1")
        v9 = mozilla.MozVer("1.1")
        v10 = mozilla.MozVer("1.10")
        v11 = mozilla.MozVer("1.*")
        v12 = mozilla.MozVer("2.0")

        self.assertTrue(v1 < v2, msg=msg)
        self.assertTrue(v2 < v3, msg=msg)
        self.assertTrue(v3 < v4, msg=msg)
        self.assertTrue(v4 < v5, msg=msg)
        self.assertTrue(v5 < v6, msg=msg)
        self.assertTrue(v6 < v7, msg=msg)
        self.assertTrue(v7 < v8, msg=msg)
        self.assertTrue(v8 < v9, msg=msg)
        self.assertTrue(v9 < v10, msg=msg)
        self.assertTrue(v10 < v11, msg=msg)
        self.assertTrue(v11 < v12, msg=msg)

        self.assertTrue(v12 > v11, msg=msg)
        self.assertTrue(v11 > v10, msg=msg)
        self.assertTrue(v10 > v9, msg=msg)
        self.assertTrue(v9 > v8, msg=msg)
        self.assertTrue(v8 > v7, msg=msg)
        self.assertTrue(v7 > v6, msg=msg)
        self.assertTrue(v6 > v5, msg=msg)
        self.assertTrue(v5 > v4, msg=msg)
        self.assertTrue(v4 > v3, msg=msg)
        self.assertTrue(v3 > v2, msg=msg)
        self.assertTrue(v2 > v1, msg=msg)

        self.assertFalse(v1 > v2, msg=msg)
        self.assertFalse(v2 > v3, msg=msg)
        self.assertFalse(v3 > v4, msg=msg)
        self.assertFalse(v4 > v5, msg=msg)
        self.assertFalse(v5 > v6, msg=msg)
        self.assertFalse(v6 > v7, msg=msg)
        self.assertFalse(v7 > v8, msg=msg)
        self.assertFalse(v8 > v9, msg=msg)
        self.assertFalse(v9 > v10, msg=msg)
        self.assertFalse(v10 > v11, msg=msg)
        self.assertFalse(v11 > v12, msg=msg)

        self.assertFalse(v12 < v11, msg=msg)
        self.assertFalse(v11 < v10, msg=msg)
        self.assertFalse(v10 < v9, msg=msg)
        self.assertFalse(v9 < v8, msg=msg)
        self.assertFalse(v8 < v7, msg=msg)
        self.assertFalse(v7 < v6, msg=msg)
        self.assertFalse(v6 < v5, msg=msg)
        self.assertFalse(v5 < v4, msg=msg)
        self.assertFalse(v4 < v3, msg=msg)
        self.assertFalse(v3 < v2, msg=msg)
        self.assertFalse(v2 < v1, msg=msg)
        _logger.info("Completed")


if __name__ == '__main__':
    unittest.main()
