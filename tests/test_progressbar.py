"""
This module defines a test suite for testing the `support.progressbar` module.
"""

import logging
import sys
import os
import unittest

# Modules to be tested are located in another directory. So the Module Search
# Path is modified for including the root of theses modules.
pathname = os.path.join(os.path.dirname(__file__), os.pardir, "lapptrack")
sys.path.append(os.path.abspath(pathname))

from support import progressbar

__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "ProgressBarTestCase"
]

# Modules to be tested use the logging facility, so a minimal
# configuration is set. To avoid side effects with the `unittest`
# console output, log entries are written in a file.
logging.basicConfig(
    format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
    filename="test_progressbar.log",
    filemode="a",
    level=logging.INFO)
_logger = logging.getLogger(__name__)


class ProgressBarTestCase(unittest.TestCase):
    def setUp(self):
        _logger.info(53*"-")

    def tearDown(self):
        _logger.info(50*"-")

    def test0101_use_case(self):
        # Regular use case
        _logger.info("Starting...")
        max_lengths = [-1, 1000000]
        for max_len in max_lengths:
            with self.subTest(max_len=max_len):
                progress_bar = progressbar.TextProgressBar(max_len)
                for i in range(0, max(max_lengths)):
                    progress_bar.compute(i, max_len)
                progress_bar.finish()
        _logger.info("Completed")

    def test0201_init_unexpected_type(self):
        # Unexpected type for parameters in the constructor
        _logger.info("Starting...")
        with self.assertRaises(TypeError):
            progressbar.TextProgressBar("")
        _logger.info("Completed")

    def test0202_compute_unexpected_type(self):
        # Unexpected type for parameters in the compute method
        _logger.info("Starting...")
        values = [(1, ""), ("", -1)]
        progress_bar = progressbar.TextProgressBar(-1)
        for l, m in values:
            with self.subTest(len=l, max_lex=m):
                with self.assertRaises(TypeError):
                    progress_bar.compute(l, m)
        _logger.info("Completed")


if __name__ == '__main__':
    unittest.main()
