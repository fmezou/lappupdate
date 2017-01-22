"""
This module defines a test suite for testing the lapptrack module.
"""

import difflib
import json
import logging
import os
import sys
import unittest
import shutil


# Modules to be tested are located in another directory. So the Module Search
# Path is modified for including the root of theses modules.
pathname = os.path.join(os.path.dirname(__file__), os.pardir, "lapptrack")
sys.path.append(os.path.abspath(pathname))

import lapptrack

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "LAppTrackFirstStartTestCase",
    "LAppTrackPullNormalTestCase",
    "LAppTrackPullFailureTestCase",
    "LAppTrackFetchNormalTestCase",
    "LAppTrackFetchFailureTestCase",
    "LAppTrackApproveNormalTestCase",
    "LAppTrackMakeNormalTestCase",
    "LAppTrackDefaultConfigTestCase",
    "LAppTrackMissingSectionConfigTestCase",
    "LAppTrackMissingSetConfigTestCase"
]

# Modules to be tested use the logging facility, so a minimal
# configuration is set. To avoid side effects with the `unittest`
# console output, log entries are written in a file.
logging.basicConfig(
    format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
    filename="test_lapptrack.log",
    filemode="a",
    level=logging.DEBUG)
_logger = logging.getLogger(__name__)


class BaseTestCase(unittest.TestCase):
    """
    Common base class for unit testing

    This class implements additional control mechanism for the output file like
    the application catalog or applist files.

    """
    def __init__(self):
        super().__init__()
        #: str: The pathname of the configuration file.
        self.config_path = ""

        #: file object: The file object of the configuration file
        self.config_file = None

        #: LAppTrack: The main instance of the tested object.
        self.tracker = None

    def assert_catalog_equal(self, path):
        """
        An equality assertion for the product `catalog`.

        The function loads the two catalogs and compares the *products* objects.
        The others objects (catalog file metadata) are not relevant for the
        comparison. In case of inequality, the message is the delta in
        `difflib.Differ` style format.

        Args:
            path: The pathname of the reference catalog (left side)
        """
        self.assert_file_exist(path)
        self.assert_file_exist(self.tracker.catalog_path)

        with open(path) as file:
            catalog = json.load(file)
            products = catalog[lapptrack.lapptrack.CAT_PRODUCTS_KNAME]
            string = json.dumps(products, indent=2, sort_keys=True)
            left_lines = string.splitlines(keepends=True)

        with open(self.tracker.catalog_path) as file:
            catalog = json.load(file)
            products = catalog[lapptrack.lapptrack.CAT_PRODUCTS_KNAME]
            string = json.dumps(products, indent=2, sort_keys=True)
            right_lines = string.splitlines(keepends=True)

        diff = difflib.ndiff(left_lines, right_lines)
        r = []
        for line in diff:
            if not line.startswith("  "):
                r.append(line)
        if r:
            msg = "".join(r)
            raise self.failureException(msg)

    def assert_applist_equal(self, path1, path2):
        """
        An equality assertion for the `applist` file.

        The function loads the two files and compares the payload of the files
        (i.e. the comment lines are ignored). In case of inequality, the message
        is the delta in `difflib.Differ` style format.

        Args:
            path1 (str): The pathname of the reference *applist* file (left
                side)
            path2 (str): The pathname of the modified *applist* file (right
                side)
        """
        self.assert_file_exist(path1)
        self.assert_file_exist(path2)

        with open(path1) as file:
            left_lines = []
            for line in file.readlines():
                if line and not line.startswith("#"):
                    left_lines.append(line)

        with open(path2) as file:
            right_lines = []
            for line in file.readlines():
                if line and not line.startswith("#"):
                    right_lines.append(line)

        diff = difflib.ndiff(left_lines, right_lines)
        r = []
        for line in diff:
            if not line.startswith("  "):
                r.append(line)
        if r:
            msg = "".join(r)
            raise self.failureException(msg)

    def assert_file_exist(self, path):
        """
        An equality assertion for the existence of a regular file.

        Args:
            path (str): The pathname of the regular file
        """
        r = os.path.isfile(path)
        if not r:
            msg = "{}: not a regular file".format(path)
            raise self.failureException(msg)

    def assert_file_not_exist(self, path):
        """
        An equality assertion for the non existence of a regular file.

        Args:
            path (str): The pathname of the regular file
        """
        r = os.path.isfile(path)
        if r:
            msg = "{}: exist and is a regular file".format(path)
            raise self.failureException(msg)

    def setUp(self):
        _logger.info(53*"-")
        self.config_file = open(self.config_path)
        self.tracker = lapptrack.lapptrack.LAppTrack()
        r = self.tracker.load_config(self.config_file)
        self.assertTrue(r, "tracker.load_config()")
        self.assertTrue(self.tracker.config_checked, "tracker.config_checked")
        shutil.rmtree(self.tracker.store_path, ignore_errors=True)

    def tearDown(self):
        self.assertTrue(self.config_file.closed)
        _logger.info(50*"-")


class LAppTrackFirstStartTestCase(BaseTestCase):
    """
    First start test case

    This class launch tasks one by one (pull, fetch, approve, make) with no
    catalog as a first start. The other options being a combination of the
    latter, this test case covers all use cases.

    The test case uses the `mock` module.
    """
    def setUp(self):
        self.config_path = "dataset\\1st_start.ini"
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_config(self):
        _logger.info("Starting...")
        self.assertEqual(self.tracker.store_path, "..\\~store\\app")
        self.assertEqual(self.tracker.catalog_path,
                         "..\\~store\\app\\catalog.json")
        _logger.info("Completed")

    def test_pull(self):
        _logger.info("Starting...")
        r = self.tracker.pull()
        self.assertTrue(r, "tracker.pull()")
        # Check output files
        self.assert_catalog_equal("dataset\\1rt_start_pull_final.json")
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-manual.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-all.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-mock.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-altmock.txt")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "pull.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "fetch.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "approve.html")
        )
        _logger.info("Completed")

    def test_fetch(self):
        _logger.info("Starting...")
        r = self.tracker.fetch()
        self.assertTrue(r, "tracker.fetch()")
        # Check output files
        self.assert_catalog_equal("dataset\\1rt_start_fetch_final.json")
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-manual.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-all.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-mock.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-altmock.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "pull.html")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "fetch.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "approve.html")
        )
        _logger.info("Completed")

    def test_approve(self):
        _logger.info("Starting...")
        r = self.tracker.approve()
        self.assertTrue(r, "tracker.approve()")
        # Check output files
        self.assert_catalog_equal("dataset\\1rt_start_approve_final.json")
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-manual.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-all.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-mock.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-altmock.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "pull.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "fetch.html")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "approve.html")
        )
        _logger.info("Completed")

    def test_make(self):
        _logger.info("Starting...")
        r = self.tracker.make()
        self.assertTrue(r, "tracker.make()")
        # Check output files
        self.assert_catalog_equal("dataset\\1rt_start_approve_final.json")
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-manual.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-all.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-mock.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-altmock.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "pull.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "fetch.html")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "approve.html")
        )
        _logger.info("Completed")


class LAppTrackPullNormalTestCase(BaseTestCase):
    """
    Normal test case for the pull task

    This class launch a pull task with an exiting catalog as usual.

    The test case uses the `mock` module.
    """
    def setUp(self):
        self.config_path = "dataset\\pull_normal.ini"
        shutil.copy("dataset\\pull_initial.json", self.tracker.catalog_path)
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_pull(self):
        _logger.info("Starting...")
        r = self.tracker.pull()
        self.assertTrue(r, "tracker.pull()")
        # Check output files
        self.assert_catalog_equal("dataset\\pull_final_normal.json")
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-manual.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-all.txt")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "pull.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "fetch.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "approve.html")
        )
        _logger.info("Completed")


class LAppTrackPullFailureTestCase(BaseTestCase):
        """
        Failure test case for the pull task

        This class launch a pull task with an exiting catalog as usual.

        The test case uses the `mock` module.
        """
        def setUp(self):
            self.config_path = "dataset\\pull_failure.ini"
            shutil.copy("dataset\\pull_initial.json", self.tracker.catalog_path)
            super().setUp()

        def tearDown(self):
            super().tearDown()

        def test_pull(self):
            _logger.info("Starting...")
            r = self.tracker.pull()
            self.assertFalse(r, "tracker.pull()")
            # Check output files
            # no change in the catalog
            self.assert_catalog_equal("dataset\\pull_initial.json")
            self.assert_file_not_exist(
                os.path.join(self.tracker.store_path, "applist-manual.txt")
            )
            self.assert_file_not_exist(
                os.path.join(self.tracker.store_path, "applist-all.txt")
            )
            self.assert_file_exist(
                os.path.join(self.tracker.store_path, "pull.html")
            )
            self.assert_file_not_exist(
                os.path.join(self.tracker.store_path, "fetch.html")
            )
            self.assert_file_not_exist(
                os.path.join(self.tracker.store_path, "approve.html")
            )
            _logger.info("Completed")


class LAppTrackFetchNormalTestCase(BaseTestCase):
    """
    Normal test case for the fetch task

    This class launch a fetch task with an exiting catalog as usual.

    The test case uses the `mock` module.
    """
    def setUp(self):
        self.config_path = "dataset\\fetch_normal.ini"
        shutil.copy("dataset\\fetch_initial.json", self.tracker.catalog_path)
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_fetch(self):
        _logger.info("Starting...")
        r = self.tracker.fetch()
        self.assertTrue(r, "tracker.fetch()")
        # Check output files
        self.assert_catalog_equal("dataset\\fetch_final_normal.json")
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-manual.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-all.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "pull.html")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "fetch.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "approve.html")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "mock-2/Mocker_v1.0.0.txt")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "mock-3/Mocker_v1.0.0.txt")
        )
        _logger.info("Completed")


class LAppTrackFetchFailureTestCase(BaseTestCase):
    """
    Failure test case for the fetch task

    This class launch a fetch task with an exiting catalog as usual.

    The test case uses the `mock` module.
    """
    def setUp(self):
        self.config_path = "dataset\\fetch_failure.ini"
        shutil.copy("dataset\\fetch_initial.json", self.tracker.catalog_path)
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_fetch(self):
        _logger.info("Starting...")
        r = self.tracker.fetch()
        self.assertFalse(r, "tracker.fetch()")
        # Check output files
        # no change in the catalog
        self.assert_catalog_equal("dataset\\fetch_initial.json")
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-manual.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-all.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "pull.html")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "fetch.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "approve.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "mock-2/Mocker_v1.0.0.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "mock-3/Mocker_v1.0.0.txt")
        )
        _logger.info("Completed")


class LAppTrackApproveNormalTestCase(BaseTestCase):
    """
    Normal test case for the approve task

    This class launch a approve task with an exiting catalog as usual.

    The test case uses the `mock` module.
    """
    def setUp(self):
        self.config_path = "dataset\\approve_normal.ini"
        shutil.copy("dataset\\approve_initial.json", self.tracker.catalog_path)
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_approve(self):
        _logger.info("Starting...")
        r = self.tracker.approve()
        self.assertTrue(r, "tracker.approve()")
        # Check output files
        self.assert_catalog_equal("dataset\\approve_final_normal.json")
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-manual.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "applist-all.txt")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "pull.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "fetch.html")
        )
        self.assert_file_exist(
            os.path.join(self.tracker.store_path, "approve.html")
        )
        _logger.info("Completed")


class LAppTrackMakeNormalTestCase(BaseTestCase):
    """
    Normal test case for the make task

    This class launch a make task with an exiting catalog as usual.

    The test case uses the `mock` module.
    """
    def setUp(self):
        self.config_path = "dataset\\make_normal.ini"
        shutil.copy("dataset\\make_initial.json", self.tracker.catalog_path)
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_make(self):
        _logger.info("Starting...")
        r = self.tracker.make()
        self.assertTrue(r, "tracker.make()")
        # Check output files
        self.assert_catalog_equal("dataset\\make_initial.json")
        self.assert_applist_equal(
            os.path.join(self.tracker.store_path, "applist-all.txt"),
            "dataset\\make_final_normal_applist-all.txt"
        )
        self.assert_applist_equal(
            os.path.join(self.tracker.store_path, "applist-manual.txt"),
            "dataset\\make_final_normal_applist-manual.txt"
        )
        self.assert_applist_equal(
            os.path.join(self.tracker.store_path, "applist-compmock1.txt"),
            "dataset\\make_final_normal_applist-compmock1.txt"
        )
        self.assert_applist_equal(
            os.path.join(self.tracker.store_path, "applist-compmock2.txt"),
            "dataset\\make_final_normal_applist-compmock2.txt"
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "pull.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "fetch.html")
        )
        self.assert_file_not_exist(
            os.path.join(self.tracker.store_path, "approve.html")
        )
        _logger.info("Completed")


class LAppTrackDefaultConfigTestCase(BaseTestCase):
    """
    Default value test case for the run task

    This class launch a run task with a minimal configuration file

    The test case uses the `mock` module.
    """
    def setUp(self):
        self.config_path = "dataset\\default.ini"
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_run(self):
        _logger.info("Starting...")
        r = self.tracker.run()
        self.assertTrue(r, "tracker.run()")
        self.assert_catalog_equal("dataset\\default_final.json")
        self.assert_applist_equal(
            os.path.join(self.tracker.store_path, "applist-all.txt"),
            "dataset\\default_final_applist-all.txt"
        )
        _logger.info("Completed")


class LAppTrackMissingSectionConfigTestCase(BaseTestCase):
    """
    Missing section in the configuration test case

    This class load a empty configuration file

    The test case uses the `mock` module.
    """
    def setUp(self):
        _logger.info(53*"-")
        self.config_path = "dataset\\missing_sections.ini"
        self.config_file = open(self.config_path)
        self.tracker = lapptrack.lapptrack.LAppTrack()

    def tearDown(self):
        super().tearDown()

    def test_load_config(self):
        _logger.info("Starting...")
        r = self.tracker.load_config(self.config_file)
        self.assertFalse(r, "tracker.load_config()")
        self.assertFalse(self.tracker.config_checked, "tracker.config_checked")
        _logger.info("Completed")


class LAppTrackMissingSetConfigTestCase(BaseTestCase):
    """
    Missing set section in the configuration test case

    This class load a configuration file with a not declared set.

    The test case uses the `mock` module.
    """
    def setUp(self):
        _logger.info(53*"-")
        self.config_path = "dataset\\missing_set.ini"
        self.config_file = open(self.config_path)
        self.tracker = lapptrack.lapptrack.LAppTrack()

    def tearDown(self):
        super().tearDown()

    def test_load_config(self):
        _logger.info("Starting...")
        r = self.tracker.load_config(self.config_file)
        self.assertFalse(r, "tracker.load_config()")
        self.assertFalse(self.tracker.config_checked, "tracker.config_checked")
        _logger.info("Completed")


if __name__ == '__main__':
    unittest.main()
