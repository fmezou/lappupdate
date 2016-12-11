"""
This module defines a test suite for testing the lapptrack module.
"""

import logging
import os
import sys
import unittest

# Modules to be tested are located in another directory. So the Module Search
# Path is modified for including the root of theses modules.
pathname = os.path.join(os.path.dirname(__file__), os.pardir, "lapptrack")
sys.path.append(os.path.abspath(pathname))

import lapptrack
from cots import mock

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


class TestlAppTrack(unittest.TestCase):
    def setUp(self):
        # Modules to be tested use the logging facility, so a minimal
        # configuration is set.
        logging.basicConfig(
            format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
            level=logging.ERROR)
        logger = logging.getLogger(__name__)

        self.file = open("./test_lapptrack.ini")
        self.main = lapptrack.LAppTrack(self.file)

    def tearDown(self):
        self.file.close()

    def test_run(self):
        self.main.run()
        # que doit t'on tester

    def test_pull(self):
        self.main.pull()
        # que doit t'on tester

    def test_fetch(self):
        self.main.fetch()
        # que doit t'on tester

    def test_approve(self):
        self.main.approve(False)
        # que doit t'on tester

    def test_make(self):
        self.main.make()
        # que doit t'on tester

    def test_config(self):
        self.main.test_config()
        # que doit t'on tester

# TODO (fmu): prevoir des test avec les configuration par defaut des .ini
# absence des fichier de reporting pa exemple.


class TestlAppTrackNull(TestlAppTrack):
    def setUp(self):
        # Modules to be tested use the logging facility, so a minimal
        # configuration is set.
        logging.basicConfig(
            format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
            level=logging.ERROR)
        logger = logging.getLogger(__name__)

        self.file = open("./test_lapptrack-null.ini")
        self.main = lapptrack.LAppTrack(self.file)

if __name__ == '__main__':
    unittest.main()
