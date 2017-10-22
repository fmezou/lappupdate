"""
This module defines a test suite for testing the `cots.core` module.
"""

import logging
import os
import stat
import sys
import unittest
import tempfile

from cots import core
from support import progressbar

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "BaseProductLoadTestCase",
    "BaseProductNotImplementedTestCase",
    "BaseProductFetchTestCase",
    "RetrieveFileTestCase",
    "GetHandlerTestCase",
    "DownloadHandlerTestCase"
]

# Modules to be tested use the logging facility, so a minimal
# configuration is set. To avoid side effects with the `unittest`
# console output, log entries are written in a file.
logging.basicConfig(
    format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
    filename="test_core.log",
    filemode="a",
    level=logging.DEBUG)
_logger = logging.getLogger(__name__)


class BaseProductLoadTestCase(unittest.TestCase):
    """
    `BaseProduct.load` and `BaseProduct.dump` methods test case
    """
    def setUp(self):
        _logger.info(53*"-")
        # Attributes default value
        self.default_attrs = {
            "name": "lappupdate",
            "display_name": "lappupdate Display Name",
            "version": "0.2.1",
            "published": "2016-10-27T17:01:30",
            "target": "unified",
            "description": "Test Suite Short Description.",
            "editor": "Example. inc",
            "web_site_location": "https://fmezou.github.io/lappupdate/",
            "location":
                "https://github.com/fmezou/lappupdate/archive/0.2.1.zip",
            "icon": "pathname/iconfile",
            "announce_location":
                "https://github.com/fmezou/lappupdate/releases",
            "feed_location":
                "https://github.com/fmezou/lappupdate/releases.atom",
            "release_note_location": "http://www.example.com/release_note.txt",
            "change_summary": "<ul>"
                              "<li>version 1.0.0 published on 2016-02-02</li>"
                              "<ul>"
                              "<li>a dummy feature</li>"
                              "</ul>"
                              "</ul>",
            "installer": "../~store/app/lappupdate_v0.2.1.zip",
            "file_size": 278331,
            "secure_hash": ("sha1", "e945a9739ab9bb3bb9960f4e168f47e9ab401ea1"),
            "std_inst_args": "/option",
            "silent_inst_args": "/silent"
        }
        self.dir_name = "../~store/app"
        self.cots = core.BaseProduct()

    def tearDown(self):
        # Clean up
        try:
            os.remove(self.cots.installer)
        except FileNotFoundError:
            pass
        del self.cots
        _logger.info(50*"-")

    def test01_load(self):
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        _logger.info("Completed")

    def test02_dump(self):
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        attrs = self.cots.dump()
        self.assertIsInstance(attrs, dict)
        self.assertEqual(self.default_attrs, attrs)
        _logger.info("Completed")

    def test03_default(self):
        # Load with default parameters
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.load(dict())
        self.assertEqual(self.default_attrs, self.cots.dump())
        _logger.info("Completed")

    def test04_unknown(self):
        # Load with unknown or privates attributes
        unknown_attrs = {
            "unknown": "parrot",
            "__catalog_url": "http://www.example.com"
        }
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.load(unknown_attrs)
        self.assertEqual(self.default_attrs, self.cots.dump())
        _logger.info("Completed")

    def test05_bad_type(self):
        # Load with unexpected parameter type
        _logger.info("Starting...")
        with self.assertRaises(TypeError):
            self.cots.load(())
        _logger.info("Completed")


class BaseProductNotImplementedTestCase(unittest.TestCase):
    """
    BaseProduct NotImplemented method test case

    This class checks the method which will have to be implemented by
    subclasses.
    """
    def setUp(self):
        _logger.info(53 * "-")
        self.cots = core.BaseProduct()

    def tearDown(self):
        del self.cots
        _logger.info(50 * "-")

    def test01_get_origin(self):
        _logger.info("Starting...")
        with self.assertRaises(NotImplementedError):
            self.cots.get_origin()
        _logger.info("Completed")

    def test02_is_update(self):
        _logger.info("Starting...")
        with self.assertRaises(NotImplementedError):
            self.cots.is_update(core.BaseProduct())
        _logger.info("Completed")


class BaseProductFetchTestCase(unittest.TestCase):
    """
    BaseProduct.fetch method test case
    """
    def setUp(self):
        _logger.info(53*"-")

        # Attributes default value
        self.default_attrs = {
            "name": "lorem",
            "display_name": "Lorem ipsum dolor sit",
            "version": "0.1.0",
            "published": "2016-10-27T17:01:30",
            "target": "unified",
            "description":
                "Lorem ipsum dolor sit amet, consectetuer adipiscing elit.",
            "editor": "Example. inc",
            "web_site_location": "http://localhost:53230",
            "location": "http://localhost:53230/lorem.txt",
            "icon": "pathname/iconfile",
            "announce_location": "http://www.example.com/news.txt",
            "feed_location": "http://www.example.com/news.atom",
            "release_note_location": "http://www.example.com/release_note.txt",
            "change_summary": "<ul>"
                              "<li>version 1.0.0 published on 2016-02-02</li>"
                              "<ul>"
                              "<li>a dummy feature</li>"
                              "</ul>"
                              "</ul>",
            "installer": "../~store/app/lorem_v0.1.0.txt",
            "file_size": 42961,
            "secure_hash": ("sha1", "c64566fa647e25d6c15644f3249657f2214b7ab0"),
            "std_inst_args": "/option",
            "silent_inst_args": "/silent"
        }
        self.dir_name = "../~store/app"
        self.cots = core.BaseProduct()

        # Clean up
        try:
            os.remove(self.default_attrs["installer"])
        except FileNotFoundError:
            pass

    def tearDown(self):
        # Clean up
        try:
            os.remove(self.cots.installer)
        except FileNotFoundError:
            pass
        del self.cots
        _logger.info(50*"-")

    def test0101_fetch(self):
        # Download a regular file
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        result = self.cots.fetch(self.dir_name)
        self.assertTrue(result)
        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        self.assertEqual(self.cots.secure_hash,
                         self.default_attrs["secure_hash"])
        self.assertEqual(self.cots.file_size,
                         self.default_attrs["file_size"])

        st = os.stat(self.default_attrs["installer"])
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.default_attrs["file_size"])
        d = core.get_file_hash(self.default_attrs["installer"],
                               self.default_attrs["secure_hash"][0])
        self.assertEqual(d.hexdigest(),
                         self.default_attrs["secure_hash"][1])
        _logger.info("Completed")

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test0201_read_only_path(self):
        # Download to a read only path
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.dir_name = "c:\windows"
        result = self.cots.fetch(self.dir_name)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")

    def test0301_unknown_length(self):
        # Download with an unknown length
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.file_size = 0
        result = self.cots.fetch(self.dir_name)
        self.assertTrue(result)
        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        self.assertEqual(self.cots.secure_hash,
                         self.default_attrs["secure_hash"])
        self.assertEqual(self.cots.file_size,
                         self.default_attrs["file_size"])

        st = os.stat(self.default_attrs["installer"])
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.default_attrs["file_size"])
        d = core.get_file_hash(self.default_attrs["installer"],
                               self.default_attrs["secure_hash"][0])
        self.assertEqual(d.hexdigest(),
                         self.default_attrs["secure_hash"][1])
        _logger.info("Completed")

    def test0302_too_high_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.file_size *= 2
        result = self.cots.fetch(self.dir_name)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")

    def test0303_too_small_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.file_size //= 2
        result = self.cots.fetch(self.dir_name)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")

    def test0304_server_too_high_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.location = "http://localhost:53230/increaselen"
        result = self.cots.fetch(self.dir_name)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")

    def test0305_server_too_small_length(self):
        # Download with a too small length
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.location = "http://localhost:53230/decreaselen"
        result = self.cots.fetch(self.dir_name)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")

    def test0401_with_no_hash(self):
        # Download with no hash
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.secure_hash = None
        result = self.cots.fetch(self.dir_name)
        self.assertTrue(result)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        self.assertEqual(self.cots.secure_hash,
                         self.default_attrs["secure_hash"])
        self.assertEqual(self.cots.file_size,
                         self.default_attrs["file_size"])

        st = os.stat(self.default_attrs["installer"])
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.default_attrs["file_size"])
        d = core.get_file_hash(self.default_attrs["installer"],
                               self.default_attrs["secure_hash"][0])
        self.assertEqual(d.hexdigest(),
                         self.default_attrs["secure_hash"][1])
        _logger.info("Completed")

    def test0402_with_unsupported_hash(self):
        # Download with a non supported hash algorithm
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.secure_hash = ("example", "")
        result = self.cots.fetch(self.dir_name)
        self.assertTrue(result)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        self.assertEqual(self.cots.secure_hash,
                         self.default_attrs["secure_hash"])
        self.assertEqual(self.cots.file_size,
                         self.default_attrs["file_size"])

        st = os.stat(self.default_attrs["installer"])
        self.assertTrue(stat.S_ISREG(st.st_mode))
        _logger.info("Completed")

    def test0403_bad_hash(self):
        # Download with an unexpected hash value
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.secure_hash = ("sha1",
                                 "0000000000000000000000000000000000000000")
        result = self.cots.fetch(self.dir_name)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")

    def test0404_error_type_hash(self):
        # Download with an unexpected hash value
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        hashes = [
            "dummy",
            ("sha1", "00", "00"),
            (None, ""),
            ("", None)
        ]
        for h in hashes:
            _logger.info("(hash=%s)", h)
            with self.subTest(hash=h):
                self.cots.secure_hash = h
                with self.assertRaises(TypeError):
                    result = self.cots.fetch(self.dir_name)
                    self.assertFalse(result)
                    self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")

    def test0501_with_bad_domain(self):
        # Download with an url having a bad domain name
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.location = "http://nolocalhost/nofile.bin"
        result = self.cots.fetch(self.dir_name)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")

    def test0502_non_existant_url(self):
        # Download with a non-existent URL
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.location = "http://localhost:53230/error?code=404"
        result = self.cots.fetch(self.dir_name)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")

    def test0503_forbidden_url(self):
        # Download with a forbidden URL
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.location = "http://localhost:53230/error?code=403"
        result = self.cots.fetch(self.dir_name)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.cots.installer))
        _logger.info("Completed")


class GetHandlerTestCase(unittest.TestCase):
    """
    get_handler function test case
    """
    def setUp(self):
        _logger.info(53*"-")
        # Attributes default value

    def tearDown(self):
        _logger.info(50*"-")

    def test01_get_handler(self):
        # Regular use case
        _logger.info("Starting...")
        handler = core.get_handler("cots.dummy.DummyHandler")
        self.assertIsInstance(handler, core.BaseProduct)

        handler = core.get_handler("cots.mock.MockHandler")
        self.assertIsInstance(handler, core.BaseProduct)
        _logger.info("Completed")

    def test02_unexpected_type(self):
        # Unexpected type for get_handler parameters
        _logger.info("Starting...")
        with self.assertRaises(TypeError):
            core.get_handler(1)
        _logger.info("Completed")

    def test03_unknown_handler(self):
        # Unknown handler module or class
        qualnames = [
            "cots.dummy.NotKnown",
            "cots.notknown.DummyHandler",
            "NotKnown"
        ]
        _logger.info("Starting...")
        for qualname in qualnames:
            _logger.info("(qualname=%s)", qualname)
            with self.subTest(qualname=qualname):
                with self.assertRaises(ImportError):
                    core.get_handler(qualname)
        _logger.info("Completed")

    def test04_unexpected_class(self):
        # Unexpected handler class
        _logger.info("Starting...")
        with self.assertRaises(TypeError):
            core.get_handler("support.semver.SemVer")
        _logger.info("Completed")


class DownloadHandlerTestCase(unittest.TestCase):
    """
    DownloadHandler test case
    """

    def setUp(self):
        _logger.info(53 * "-")

        # Attributes default value
        self.store_path = "../~store/app"
        self.url = "http://localhost:53230/lorem.txt"
        self.filename = "../~store/app/lorem.txt"
        self.type = "text/plain"
        self.length = 42961
        self.hash = ("sha1", "c64566fa647e25d6c15644f3249657f2214b7ab0")
        self.remote = None
        self.progress = progressbar.TextProgressBar

        # Clean up
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def tearDown(self):
        # Clean up
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass
        del self.remote
        _logger.info(50 * "-")

    def test0101_fetch(self):
        # Download a regular file
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertTrue(result)

        self.assertEqual(os.path.abspath(self.remote.filename),
                         os.path.abspath(self.filename))

        h = (self.remote.hash.name, self.remote.hash.hexdigest())
        self.assertEqual(h, self.hash)
        d = core.get_file_hash(self.remote.filename, self.hash[0])
        self.assertEqual(d.hexdigest(), self.hash[1])

        st = os.stat(self.filename)
        self.assertEqual(self.remote.length, self.length)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.length)

        self.assertEqual(self.type, self.remote.type)

        _logger.info("Completed")

    def test0102_fetch_temporary(self):
        # Download a temporary file
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path=None,
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertTrue(result)

        h = (self.remote.hash.name, self.remote.hash.hexdigest())
        self.assertEqual(h, self.hash)
        d = core.get_file_hash(self.remote.filename, self.hash[0])
        self.assertEqual(d.hexdigest(), self.hash[1])

        st = os.stat(self.remote.filename)
        self.assertEqual(self.remote.length, self.length)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.length)

        self.assertEqual(self.type, self.remote.type)

        _logger.info("Completed")

    def test0103_fetch_unknown_length(self):
        # Download a regular file whose length is unknown
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path=self.store_path,
                                           type=self.type,
                                           length=None,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertTrue(result)

        self.assertEqual(os.path.abspath(self.remote.filename),
                         os.path.abspath(self.filename))

        h = (self.remote.hash.name, self.remote.hash.hexdigest())
        self.assertEqual(h, self.hash)
        d = core.get_file_hash(self.remote.filename, self.hash[0])
        self.assertEqual(d.hexdigest(), self.hash[1])

        st = os.stat(self.remote.filename)
        self.assertEqual(self.remote.length, self.length)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.length)

        self.assertEqual(self.type, self.remote.type)

        _logger.info("Completed")

    def test0104_fetch_unknown_hash(self):
        # Download a regular file whose secure hash is unknown
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=None,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertTrue(result)

        self.assertEqual(os.path.abspath(self.remote.filename),
                         os.path.abspath(self.filename))

        h = (self.remote.hash.name, self.remote.hash.hexdigest())
        self.assertEqual(h, self.hash)
        d = core.get_file_hash(self.remote.filename, self.hash[0])
        self.assertEqual(d.hexdigest(), self.hash[1])

        st = os.stat(self.remote.filename)
        self.assertEqual(self.remote.length, self.length)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.length)

        self.assertEqual(self.type, self.remote.type)

        _logger.info("Completed")

    def test0105_fetch_unknown_type(self):
        # Download a regular file whose mime type is unknown
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path=self.store_path,
                                           type=None,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertTrue(result)

        self.assertEqual(os.path.abspath(self.remote.filename),
                         os.path.abspath(self.filename))

        h = (self.remote.hash.name, self.remote.hash.hexdigest())
        self.assertEqual(h, self.hash)
        d = core.get_file_hash(self.remote.filename, self.hash[0])
        self.assertEqual(d.hexdigest(), self.hash[1])

        st = os.stat(self.remote.filename)
        self.assertEqual(self.remote.length, self.length)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.length)

        self.assertEqual(self.type, self.remote.type)

        _logger.info("Completed")

    def test0106_fetch_redirect(self):
        # Download a regular file with a redirected URL
        _logger.info("Starting...")
        url = "http://localhost:53230/redirect"
        self.remote = core.DownloadHandler(url,
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertTrue(result)

        self.assertEqual(os.path.abspath(self.remote.filename),
                         os.path.abspath(self.filename))

        h = (self.remote.hash.name, self.remote.hash.hexdigest())
        self.assertEqual(h, self.hash)
        d = core.get_file_hash(self.remote.filename, self.hash[0])
        self.assertEqual(d.hexdigest(), self.hash[1])

        st = os.stat(self.remote.filename)
        self.assertEqual(self.remote.length, self.length)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.length)

        self.assertEqual(self.type, self.remote.type)

        _logger.info("Completed")

    def test0107_fetch_disposition(self):
        # Download a regular file with a Content-Disposition header
        _logger.info("Starting...")
        url = "http://localhost:53230/disposition"
        self.remote = core.DownloadHandler(url,
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertTrue(result)

        self.assertEqual(os.path.abspath(self.remote.filename),
                         os.path.abspath(self.filename))

        h = (self.remote.hash.name, self.remote.hash.hexdigest())
        self.assertEqual(h, self.hash)
        d = core.get_file_hash(self.remote.filename, self.hash[0])
        self.assertEqual(d.hexdigest(), self.hash[1])

        st = os.stat(self.remote.filename)
        self.assertEqual(self.remote.length, self.length)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.length)

        self.assertEqual(self.type, self.remote.type)

        _logger.info("Completed")

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test0201_read_only_path(self):
        # Download to a read only path
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path="c:\windows",
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")

    def test0301_too_high_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length+1,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")

    def test0302_too_small_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length-1,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")

    def test0303_server_too_high_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        self.remote = core.DownloadHandler("http://localhost:53230/increaselen",
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")

    def test0304_server_too_small_length(self):
        # Download with a too small length
        _logger.info("Starting...")
        self.remote = core.DownloadHandler("http://localhost:53230/decreaselen",
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")

    def test0401_with_unsupported_hash(self):
        # Download with a non supported hash algorithm
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=("example", ""),
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertTrue(result)

        self.assertEqual(os.path.abspath(self.remote.filename),
                         os.path.abspath(self.filename))
        h = (self.remote.hash.name, self.remote.hash.hexdigest())
        self.assertEqual(h, self.hash)
        self.assertEqual(self.remote.length, self.length)

        st = os.stat(self.remote.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        _logger.info("Completed")

    def test0402_bad_hash(self):
        # Download with an unexpected hash value
        _logger.info("Starting...")
        h = ("sha1","0000000000000000000000000000000000000000")
        self.remote = core.DownloadHandler(self.url,
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=h,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")

    def test0403_error_type_hash(self):
        # Download with an unexpected hash value
        _logger.info("Starting...")
        hashes = [
            "dummy",
            ("sha1", "00", "00"),
            (None, ""),
            ("", None)
        ]
        for h in hashes:
            _logger.info("(hash=%s)", h)
            with self.subTest(hash=h):
                with self.assertRaises(TypeError):
                    self.remote = core.DownloadHandler(self.url,
                                                       path=self.store_path,
                                                       type=self.type,
                                                       length=self.length,
                                                       hash=h,
                                                       progress=self.progress)
                    result = self.remote.fetch()
                    self.assertFalse(result)
                    self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")

    def test0501_unexpected_mimetype(self):
        # Download with an unexpected mime type
        _logger.info("Starting...")
        self.remote = core.DownloadHandler(self.url,
                                           path=self.store_path,
                                           type="x-app/x-bin",
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")


    def test0601_with_bad_domain(self):
        # Download with an url having a bad domain name
        _logger.info("Starting...")
        self.remote = core.DownloadHandler("http://nolocalhost/nofile.bin",
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")

    def test0602_non_existant_url(self):
        # Download with a non-existent URL
        _logger.info("Starting...")
        self.remote = core.DownloadHandler("http://localhost:53230/error?code=404",
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")

    def test0603_forbidden_url(self):
        # Download with a forbidden URL
        _logger.info("Starting...")
        self.remote = core.DownloadHandler("http://localhost:53230/error?code=403",
                                           path=self.store_path,
                                           type=self.type,
                                           length=self.length,
                                           hash=self.hash,
                                           progress=self.progress)
        result = self.remote.fetch()
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.remote.filename))
        _logger.info("Completed")


if __name__ == '__main__':
    unittest.main()
