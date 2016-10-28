"""
This module defines a test suite for testing the semver module.

The `semantic versioning specification`_ 2.0.0. defines the rules on which
following tests are based.

.. _semantic versioning specification: http://semver.org/spec/v2.0.0.html
"""

import logging
import sys
import os
import unittest

# Modules to be tested are located in another directory. So the Module Search
# Path is modified for including the root of theses modules.
pathname = os.path.join(os.path.dirname(__file__), os.pardir, "lapptrack")
sys.path.append(os.path.abspath(pathname))

from support import semver

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

    def test_left_op(self):
        """Left operand testing"""
        msg = "Operation must have an semver. SemVer object as left operand"
        with self.assertRaises(TypeError, msg=msg):
            v = semver.SemVer("1.0.0")
            if v == 0:
                pass
            if v != 0:
                pass
            if v < 0:
                pass
            if v > 0:
                pass

    def test_positive_integer(self):
        """Rule #2 compliance"""
        msg = "Negative integers must be rejected"
        vers = ["-1.0.0", "0.-1.0", "0.0.-1"]
        for ver in vers:
            with self.subTest(version=ver):
                with self.assertRaises(ValueError, msg=msg):
                    v = semver.SemVer(ver)

    def test_major_zero(self):
        """Rule #4 compliance"""
        msg = "Major version zero (0.y.z) is for initial development."
        v = semver.SemVer("0.1.0")
        self.assertTrue(v.unstable, msg=msg)

    def test_pre_release(self):
        """Rule #9 compliance"""
        msg = "A pre-release version indicates that the version is unstable."
        v1 = semver.SemVer("1.0.0-alpha.1")
        self.assertTrue(v1.unstable, msg=msg)

    def test_pre_release_precedence1(self):
        """Rule #9 compliance"""
        msg = "Pre-release versions have a lower precedence than the " \
              "associated normal version"
        v1 = semver.SemVer("1.0.0-alpha.1")
        v2 = semver.SemVer("1.0.0")
        self.assertTrue(v1 < v2, msg=msg)
        self.assertTrue(v2 > v1, msg=msg)

    def test_metadata_precedence(self):
        """Rule #10 compliance"""
        msg = "Two versions that differ only in the build metadata, have the " \
              "same precedence"
        v1 = semver.SemVer("1.0.0-beta+exp.sha.5114f85")
        v2 = semver.SemVer("1.0.0-beta")
        self.assertTrue(v1 == v2, msg=msg)
        self.assertFalse(v1 != v2, msg=msg)

    def test_precedence(self):
        """Rule #11 compliance"""
        msg = "Precedence is determined by the first difference when " \
              "comparing each of these identifiers from left to right."
        v1 = semver.SemVer("1.0.0")
        v2 = semver.SemVer("2.0.0")
        v3 = semver.SemVer("2.1.0")
        v4 = semver.SemVer("2.1.1")
        self.assertTrue(v1 < v2 < v3 < v4, msg=msg)
        self.assertTrue(v4 > v3 > v2 > v1, msg=msg)

    def test_pre_release_precedence2(self):
        """Rule #11 compliance"""
        msg = "Precedence for two pre-release versions with the same major, " \
              "minor, and patch version MUST be determined by comparing each " \
              "dot separated identifier from left to right until a " \
              "difference is found."
        v1 = semver.SemVer("1.0.0-alpha")
        v2 = semver.SemVer("1.0.0-alpha.1")
        v3 = semver.SemVer("1.0.0-alpha.beta")
        v4 = semver.SemVer("1.0.0-beta")
        v5 = semver.SemVer("1.0.0-beta.2")
        v6 = semver.SemVer("1.0.0-beta.11")
        v7 = semver.SemVer("1.0.0-rc.1")
        v8 = semver.SemVer("1.0.0")
        self.assertTrue(v1 < v2 < v3 < v4 < v5 < v6 < v7 < v8, msg=msg)
        self.assertTrue(v8 > v7 > v6 > v5 > v4 > v3 > v2 > v1, msg=msg)


if __name__ == '__main__':
    unittest.main()
