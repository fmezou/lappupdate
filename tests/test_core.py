"""
This module defines a test suite for testing the core module.
"""

import logging
import os
import sys
import unittest

# Modules to be tested are located in another directory. So the Module Search
# Path is modified for including the root of theses modules.
pathname = os.path.join(os.path.dirname(__file__), os.pardir, "lapptrack")
sys.path.append(os.path.abspath(pathname))

from cots import core

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


class TestSemVer(unittest.TestCase):
    def setUp(self):
        # Modules to be testes use the logging facility, so a minimal
        # configuration is set.
        logging.basicConfig(
            format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
            level=logging.ERROR)
        logger = logging.getLogger(__name__)

        # non variant
        self.url = "https://addons.cdn.mozilla.net/user-media/addons/1865/" \
                   "adblock_plus-2.7-fx+sm+tb+an.xpi"
        self.dir_name = "../~store/app"

    def tearDown(self):
        pass

    def test_retrieve_file_ex(self):
        ctype = "application/x-xpinstall"
        clength = 989188
        chash = (
            "sha256",
            "c1ef9d41e122ceb242facab8755219a8ffa9b8a15321c352d0e95e1ac9994c2a"
        )
        core.retrieve_file(self.url, self.dir_name,
                           content_type=ctype,
                           content_length=clength,
                           content_hash=chash)

    def test_retrieve_file(self):
        filename = core.retrieve_file(self.url, self.dir_name)

    def test_unsupported_hash(self):
        chash = ("md6", "")
        core.retrieve_file(self.url, self.dir_name, content_hash=chash)

    def test_bad_hash(self):
        chash = (
            "sha256",
            "c1ef9d41e122ceb242facab8755219a8ffa9b8a15321c352d0e95e1ac9994c2b"
        )
        msg = "Bad hash must be rejected"
        with self.assertRaises(core.UnexpectedContentError, msg=msg):
            core.retrieve_file(self.url, self.dir_name, content_hash=chash)

    def test_bad_content_lenght(self):
        clength = 9891
        msg = "Bad content length must be rejected"
        with self.assertRaises(core.UnexpectedContentLengthError, msg=msg):
            core.retrieve_file(self.url, self.dir_name, content_length=clength)

    def test_bad_content_type(self):
        ctype = "unknown/vnd"
        msg = "Bad content type must be rejectedd"
        with self.assertRaises(core.UnexpectedContentTypeError, msg=msg):
            core.retrieve_file(self.url, self.dir_name, content_type=ctype)

# TODO: add unknown content length (no header) and unknow url
if __name__ == '__main__':
    unittest.main()

