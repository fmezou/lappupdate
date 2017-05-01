"""
This module defines a test suite for testing the `support.semver` module.

The `semantic versioning specification`_ 2.0.0. defines the rules on which
following tests are based.
"""

import logging
import unittest

from cots import core

__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "MakeMKVHandlerTestCase",
    "FirefoxWinHandlerHandlerTestCase",
    "FirefoxWin64HandlerHandlerTestCase",
    "ThunderbirdWinHandlerHandlerTestCase"
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


class BaseHandlerTestCase(unittest.TestCase):
    """
    Common base class for unit testing

    This class implements additional mechanism.

    """
    def repr_app(self, handler):
        """
        Print the product attributes.

        Args:
            handler (BaseProduct): The product to print.  

        Returns:
            str: a human readable string with the handler attribute.
        """
        if not isinstance(handler, core.BaseProduct):
            msg = "Unexpected handler: must be a class 'BaseProduct'. " \
                  "not {0}".format(handler.__class__)
            raise self.failureException(msg)

        l = list()
        l.append("Product attributes")
        l.append("- General --------------------------------------------------")
        l.append("  Name:         {}".format(handler.name))
        l.append("  Display name: {}".format(handler.display_name))
        l.append("  Version:      {}".format(handler.version))
        l.append("  Published:    {}".format(handler.published))
        l.append("------------------------------------------------------------")
        l.append("- Details --------------------------------------------------")
        l.append("  Target:       {}".format(handler.target))
        l.append("  Description:  {}".format(handler.description))
        l.append("  Editor:       {}".format(handler.editor))
        l.append("  Web site:     {}".format(handler.web_site_location))
        l.append("  Icon:         {}".format(handler.icon))
        l.append("  Announce:     {}".format(handler.announce_location))
        l.append("  Feed:         {}".format(handler.feed_location))
        l.append("  Release Note: {}".format(handler.release_note_location))
        l.append("------------------------------------------------------------")
        l.append("- Change summary -------------------------------------------")
        l.append(handler.change_summary)
        l.append("------------------------------------------------------------")
        l.append("- Installer ------------------------------------------------")
        l.append("  URL:          {}".format(handler.location))
        l.append("  Location:     {}".format(handler.installer))
        l.append("  Size:         {} bytes".format(handler.file_size))
        if handler.secure_hash is not None:
            hn, hv = handler.secure_hash
        else:
            hn, hv = ["", ""]
        l.append("  Hash:         {} ({})".format(hv, hn))
        l.append("  Command line option")
        l.append("    Silent mode:   {}".format(handler.silent_inst_args))
        l.append("    Standard mode: {}".format(handler.std_inst_args))
        l.append("------------------------------------------------------------")
        return "\n".join(l)


class MakeMKVHandlerTestCase(BaseHandlerTestCase):
    """
    MakeMKV handler test suite
    """
    def setUp(self):
        _logger.info(53*"-")
        self.qualname = "cots.makemkv.MakeMKVHandler"
        self.previous_version = "1.10.0"
        self.handler = core.get_handler(self.qualname)

    def tearDown(self):
        _logger.info(50*"-")
        # Clean up
        del self.handler

    def test_get_origin(self):
        # Get product information from the remote repository.
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")

    def test_fetch(self, ):
        # Download the product installer..
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)
        result = self.handler.fetch("../~store/app")
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")

    def test_is_update(self, ):
        # Check if the remote version is an update.
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)

        # The current version is not an update of itself.
        result = self.handler.is_update(self.handler)
        self.assertFalse(result)

        previous = core.get_handler(self.qualname)
        previous.version = self.previous_version
        result = self.handler.is_update(previous)
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")


class FirefoxWinHandlerHandlerTestCase(BaseHandlerTestCase):
    """
    Firefox (windows version) handler test suite
    """
    def repr_app(self, handler):
        """
        Print the product attributes.

        Args:
            handler (BaseProduct): The product to print.  

        Returns:
            str: a human readable string with the handler attribute.
        """
        super().repr_app(handler)

        l = list()
        l.append(super().repr_app(handler))
        l.append("- Mozilla --------------------------------------------------")
        l.append("  Build ID:         {}".format(handler.build_id))
        l.append("  Locale:           {}".format(handler.locale))
        l.append("- Mozilla --------------------------------------------------")
        return "\n".join(l)

    def setUp(self):
        _logger.info(53*"-")
        self.qualname = "cots.mozilla.FirefoxWinHandler"
        self.previous_version = "1.0"
        self.handler = core.get_handler(self.qualname)

    def tearDown(self):
        _logger.info(50*"-")
        # Clean up
        del self.handler

    def test_get_origin(self):
        # Get product information from the remote repository.
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")

    def test_get_origin2(self):
        # Get product information from the remote repository.
        _logger.info("Starting...")
        result = self.handler.get_origin()
        while result:
            v = self.handler.version
            print("{} published on {}".format(self.handler.display_name,
                                              self.handler.published))
            result = self.handler.get_origin()
            if result:
                if self.handler.version == v:
                    result = False

        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")


    def test_fetch(self, ):
        # Download the product installer..
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)
        result = self.handler.fetch("../~store/app")
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")

    def test_is_update(self, ):
        # Check if the remote version is an update.
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)

        # The current version is not an update of itself.
        result = self.handler.is_update(self.handler)
        self.assertFalse(result)

        previous = core.get_handler(self.qualname)
        previous.version = self.previous_version
        result = self.handler.is_update(previous)
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")


class FirefoxWin64HandlerHandlerTestCase(BaseHandlerTestCase):
    """
    Firefox (windows version) handler test suite
    """
    def setUp(self):
        _logger.info(53*"-")
        self.qualname = "cots.mozilla.FirefoxWin64Handler"
        self.previous_version = "42.0"
        self.handler = core.get_handler(self.qualname)

    def tearDown(self):
        _logger.info(50*"-")
        # Clean up
        del self.handler

    def test_get_origin(self):
        # Get product information from the remote repository.
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")

    def test_fetch(self, ):
        # Download the product installer..
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)
        result = self.handler.fetch("../~store/app")
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")

    def test_is_update(self, ):
        # Check if the remote version is an update.
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)

        # The current version is not an update of itself.
        result = self.handler.is_update(self.handler)
        self.assertFalse(result)

        previous = core.get_handler(self.qualname)
        previous.version = self.previous_version
        result = self.handler.is_update(previous)
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")


class ThunderbirdWinHandlerHandlerTestCase(BaseHandlerTestCase):
    """
    Firefox (windows version) handler test suite
    """
    def setUp(self):
        _logger.info(53*"-")
        self.qualname = "cots.mozilla.ThunderbirdWinHandler"
        self.previous_version = "1.0"
        self.handler = core.get_handler(self.qualname)

    def tearDown(self):
        _logger.info(50*"-")
        # Clean up
        del self.handler

    def test_get_origin(self):
        # Get product information from the remote repository.
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")

    def test_fetch(self, ):
        # Download the product installer..
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)
        result = self.handler.fetch("../~store/app")
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")

    def test_is_update(self, ):
        # Check if the remote version is an update.
        _logger.info("Starting...")
        result = self.handler.get_origin(version=self.previous_version)
        self.assertTrue(result)

        # The current version is not an update of itself.
        result = self.handler.is_update(self.handler)
        self.assertFalse(result)

        previous = core.get_handler(self.qualname)
        previous.version = self.previous_version
        result = self.handler.is_update(previous)
        self.assertTrue(result)
        _logger.info(self.repr_app(self.handler))
        _logger.info("Completed")


if __name__ == '__main__':
    unittest.main()
