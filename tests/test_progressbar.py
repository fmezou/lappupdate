"""
This module defines a test suite for testing progress bar widgets.
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


class TestSemVer(unittest.TestCase):
    def setUp(self):
        # Modules to be testes use the logging facility, so a minimal
        # configuration is set.
        logging.basicConfig(
            format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
            level=logging.ERROR)

    def tearDown(self):
        pass

    def test_use_case(self):
        """Regular use case"""
        max_lengths = [-1, 10000000]
        for max_len in max_lengths:
            with self.subTest(max_len=max_len):
                progress_bar = progressbar.TextProgressBar(max_len)
                for i in range(0, max(max_lengths)):
                    progress_bar.compute(i, max_len)
                progress_bar.finish()

    def test_init_unexpected_type(self):
        """Unexpected type for parameters in the constructor"""
        with self.assertRaises(TypeError):
            progressbar.TextProgressBar("")

    def test_compute_unexpected_type(self):
        """Unexpected type for parameters in the compute method"""
        values = [(1, ""), ("", -1)]
        progress_bar = progressbar.TextProgressBar(-1)
        for l, m in values:
            with self.subTest(len=l, max_lex=m):
                with self.assertRaises(TypeError):
                    progress_bar.compute(l, m)


if __name__ == '__main__':
    unittest.main()
