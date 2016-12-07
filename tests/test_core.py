"""
This module defines a test suite for testing the core module.
"""

import logging
import os
import stat
import sys
import unittest
import urllib.error

# Modules to be tested are located in another directory. So the Module Search
# Path is modified for including the root of theses modules.
_pathname = os.path.join(os.path.dirname(__file__), os.pardir, "lapptrack")
sys.path.append(os.path.abspath(_pathname))

from cots import core

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"

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
    BaseProduct.load and BaseProduct.dump method test case
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
            "icon" : "pathname/iconfile",
            "announce_location" :
                "https://github.com/fmezou/lappupdate/releases",
            "feed_location" :
                "https://github.com/fmezou/lappupdate/releases.atom",
            "release_note_location": "http://www.example.com/release_note.txt",
            "change_summary": "<ul>"
                              "<li>version 1.0.0 published on 2016-02-02</li>"
                              "<ul>"
                              "<li>a dummy feature</li>"
                              "</ul>"
                              "</ul>",
            "installer" : "../~store/app/lappupdate_0.2.1.zip",
            "file_size" : 278331,
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

    This class checks the method witch will have to be implemented by
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
            "icon" : "pathname/iconfile",
            "announce_location" :
                "https://github.com/fmezou/lappupdate/releases",
            "feed_location" :
                "https://github.com/fmezou/lappupdate/releases.atom",
            "release_note_location": "http://www.example.com/release_note.txt",
            "change_summary": "<ul>"
                              "<li>version 1.0.0 published on 2016-02-02</li>"
                              "<ul>"
                              "<li>a dummy feature</li>"
                              "</ul>"
                              "</ul>",
            "installer" : "../~store/app/lappupdate_0.2.1.zip",
            "file_size" : 278331,
            "secure_hash": ("sha1", "e945a9739ab9bb3bb9960f4e168f47e9ab401ea1"),
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

    def test01_fetch(self):
        # Download a regular file
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.fetch(self.dir_name)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        st = os.stat(self.default_attrs["installer"])
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.default_attrs["file_size"])
        d = core.get_file_hash(self.default_attrs["installer"],
                               self.default_attrs["secure_hash"][0])
        self.assertEqual(d.hexdigest(),
                         self.default_attrs["secure_hash"][1])
        _logger.info("Completed")

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test02_read_only_path(self):
        # Download to a read only path
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.dir_name = "c:\windows"
        with self.assertRaises(PermissionError) as cm:
            self.cots.fetch(self.dir_name)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.default_attrs["installer"])
        _logger.info("Completed")

    def test03_unknown_length(self):
        # Download with an unknown length
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.file_size = -1
        self.cots.fetch(self.dir_name)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        st = os.stat(self.default_attrs["installer"])
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.default_attrs["file_size"])
        d = core.get_file_hash(self.default_attrs["installer"],
                               self.default_attrs["secure_hash"][0])
        self.assertEqual(d.hexdigest(),
                         self.default_attrs["secure_hash"][1])
        _logger.info("Completed")

    def test04_too_high_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.file_size *= 2
        with self.assertRaises(core.UnexpectedContentLengthError):
            self.cots.fetch(self.dir_name)

        # TODO (fmezou): check result when raise an exception (cleanup)
        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.default_attrs["installer"])
        _logger.info("Completed")

    def test05_too_small_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.file_size //= 2
        with self.assertRaises(core.UnexpectedContentLengthError):
            self.cots.fetch(self.dir_name)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.default_attrs["installer"])
        _logger.info("Completed")

    def test06_with_no_hash(self):
        # Download with no hash
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.secure_hash = None
        self.cots.fetch(self.dir_name)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        st = os.stat(self.default_attrs["installer"])
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.default_attrs["file_size"])
        d = core.get_file_hash(self.default_attrs["installer"],
                               self.default_attrs["secure_hash"][0])
        self.assertEqual(d.hexdigest(),
                         self.default_attrs["secure_hash"][1])
        _logger.info("Completed")

    def test07_with_unsupported_hash(self):
        # Download with a non supported hash algorithm
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.secure_hash = ("example", "")
        self.cots.fetch(self.dir_name)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        st = os.stat(self.default_attrs["installer"])
        self.assertTrue(stat.S_ISREG(st.st_mode))
        _logger.info("Completed")

    def test08_unexpected_hash(self):
        # Download with an unexpected hash value
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.secure_hash = ("sha1", "0000000000000000000000000000000000000000")
        with self.assertRaises(core.UnexpectedContentError):
            self.cots.fetch(self.dir_name)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.default_attrs["installer"])
            self.assertFalse(stat.S_ISREG(st.st_mode))
        _logger.info("Completed")

    def test09_with_bad_domain(self):
        # Download with an url having a bad domain name
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.location = "https://nodomain.fr/nofile.bin"
        with self.assertRaises(urllib.error.URLError):
            self.cots.fetch(self.dir_name)

        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.default_attrs["installer"])
        _logger.info("Completed")

    def test10_non_existant_url(self):
        # Download with a non-existent URL
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.location = "https://github.com/fmezou/lappupdate/archive/0.0.0.zip"
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.cots.fetch(self.dir_name)

        self.assertEqual(cm.exception.code, 404)
        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.default_attrs["installer"])
        _logger.info("Completed")

    def test11_forbidden_url(self):
        # Download with a forbidden URL
        _logger.info("Starting...")
        self.cots.load(self.default_attrs)
        self.cots.location = "http://ftp.free.fr/lost%2bfound/"
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.cots.fetch(self.dir_name)

        self.assertEqual(cm.exception.code, 403)
        self.assertEqual(os.path.abspath(self.cots.installer),
                         os.path.abspath(self.default_attrs["installer"]))
        self.assertEqual(self.cots.installer, self.default_attrs["installer"])
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.default_attrs["installer"])
        _logger.info("Completed")


class RetrieveFileTestCase(unittest.TestCase):
    """
    retrieve_file function test case
    """
    def setUp(self):
        _logger.info(53 * "-")

        # Attributes default value
        self.url = "https://github.com/fmezou/lappupdate/archive/0.2.1.zip"
        self.content_type = "application/zip"
        self.content_lenght = 278331
        self.content_hash = ("sha1", "e945a9739ab9bb3bb9960f4e168f47e9ab401ea1")
        self.dir_name = "../~store/app"
        self.filename = os.path.join(self.dir_name, "0.2.1.zip")

    def tearDown(self):
        # Clean up
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass
        _logger.info(50 * "-")

    def test01_retrieve_file(self):
        # Download a regular file
        _logger.info("Starting...")
        filename = core.retrieve_file(self.url,
                                      self.dir_name,
                                      content_type=self.content_type,
                                      content_length=self.content_lenght,
                                      content_hash=self.content_hash)

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test02_read_only_path(self):
        # Download to a read only path
        _logger.info("Starting...")
        self.dir_name = "c:\windows"
        self.filename = os.path.join(self.dir_name, "0.2.1.zip")
        filename = ""
        with self.assertRaises(PermissionError) as cm:
            filename = core.retrieve_file(self.url, self.dir_name)

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test03_unknown_length(self):
        # Download with an unknown length
        _logger.info("Starting...")
        filename = core.retrieve_file(self.url,
                                      self.dir_name,
                                      content_type=self.content_type,
                                      content_hash=self.content_hash)

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    def test04_too_high_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        filename = ""
        with self.assertRaises(core.UnexpectedContentLengthError):
            filename = core.retrieve_file(self.url,
                                          self.dir_name,
                                          content_type=self.content_type,
                                          content_length=self.content_lenght*2,
                                          content_hash=self.content_hash)

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test05_too_small_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        filename = ""
        with self.assertRaises(core.UnexpectedContentLengthError):
            filename = core.retrieve_file(self.url,
                                          self.dir_name,
                                          content_type=self.content_type,
                                          content_length=self.content_lenght//2,
                                          content_hash=self.content_hash)

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test06_no_hash(self):
        # Download with no hash
        _logger.info("Starting...")
        filename = core.retrieve_file(self.url,
                                      self.dir_name,
                                      content_type=self.content_type)

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    def test07_unsupported_hash(self):
        # Download with a non supported hash algorithm
        _logger.info("Starting...")
        filename = core.retrieve_file(self.url,
                                      self.dir_name,
                                      content_type=self.content_type,
                                      content_hash=("example", ""))

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    def test08_unexpected_hash(self):
        # Download with an unexpected hash value
        _logger.info("Starting...")
        secure_hash = ("sha1", "0000000000000000000000000000000000000000")
        filename = ""
        with self.assertRaises(core.UnexpectedContentError):
            filename = core.retrieve_file(self.url,
                                          self.dir_name,
                                          content_type=self.content_type,
                                          content_hash=secure_hash)

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test09_no_mimetype(self):
        # Download with no hash
        _logger.info("Starting...")
        filename = core.retrieve_file(self.url, self.dir_name)

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    def test10_unexpected_mimetype(self):
        # Download with an unexpected hash value
        _logger.info("Starting...")
        filename = ""
        with self.assertRaises(core.UnexpectedContentTypeError):
            filename = core.retrieve_file(self.url,
                                          self.dir_name,
                                          content_type="text/plain")

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test11_bad_domain(self):
        # Download with an url having a bad domain name
        _logger.info("Starting...")
        url = "https://nodomain.fr/nofile.bin"
        filename = ""
        with self.assertRaises(urllib.error.URLError):
            filename = core.retrieve_file(url, self.dir_name)

        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test12_non_existant_url(self):
        # Download with a non-existent URL
        _logger.info("Starting...")
        url = "https://github.com/fmezou/lappupdate/archive/0.0.0.zip"
        filename = ""
        with self.assertRaises(urllib.error.HTTPError) as cm:
            filename = core.retrieve_file(url, self.dir_name)

        self.assertEqual(cm.exception.code, 404)
        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test13_forbidden_url(self):
        # Download with a forbidden URL
        _logger.info("Starting...")
        url = "http://ftp.free.fr/lost%2bfound/"
        filename = ""
        with self.assertRaises(urllib.error.HTTPError) as cm:
            filename = core.retrieve_file(self.url, self.dir_name)

        self.assertEqual(cm.exception.code, 403)
        self.assertEqual(os.path.abspath(filename),
                         os.path.abspath(self.filename))
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")


class RetrieveTempFileTestCase(unittest.TestCase):
    """
    retrieve_file function test case
    """
    def setUp(self):
        _logger.info(53 * "-")

        # Attributes default value
        self.url = "https://github.com/fmezou/lappupdate/archive/0.2.1.zip"
        self.content_type = "application/zip"
        self.content_lenght = 278331
        self.content_hash = (
        "sha1", "e945a9739ab9bb3bb9960f4e168f47e9ab401ea1")
        self.dir_name = "../~store/app"
        self.filename = ""

    def tearDown(self):
        # Clean up
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass
        _logger.info(50 * "-")

    def test01_retrieve_file(self):
        # Download a regular file
        _logger.info("Starting...")
        self.filename = core.retrieve_tempfile(self.url,
                                               content_type=self.content_type,
                                               content_length=self.content_lenght,
                                               content_hash=self.content_hash)
        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    def test02_unknown_length(self):
        # Download with an unknown length
        _logger.info("Starting...")
        self.filename = core.retrieve_tempfile(self.url,
                                               content_type=self.content_type,
                                               content_hash=self.content_hash)
        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    def test03_too_high_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        with self.assertRaises(core.UnexpectedContentLengthError):
            self.filename = core.retrieve_tempfile(self.url,
                                                   content_type=self.content_type,
                                                   content_length=self.content_lenght * 2,
                                                   content_hash=self.content_hash)
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test04_too_small_length(self):
        # Download with a too high length
        _logger.info("Starting...")
        with self.assertRaises(core.UnexpectedContentLengthError):
            self.filename = core.retrieve_tempfile(self.url,
                                                   content_type=self.content_type,
                                                   content_length=self.content_lenght // 2,
                                                   content_hash=self.content_hash)
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test05_no_hash(self):
        # Download with no hash
        _logger.info("Starting...")
        self.filename = core.retrieve_tempfile(self.url,
                                               content_type=self.content_type)
        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    def test06_unsupported_hash(self):
        # Download with a non supported hash algorithm
        _logger.info("Starting...")
        self.filename = core.retrieve_tempfile(self.url,
                                               content_type=self.content_type,
                                               content_hash=("example", ""))

        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    def test07_unexpected_hash(self):
        # Download with an unexpected hash value
        _logger.info("Starting...")
        secure_hash = ("sha1", "0000000000000000000000000000000000000000")
        with self.assertRaises(core.UnexpectedContentError):
            self.filename = core.retrieve_tempfile(self.url,
                                                   content_type=self.content_type,
                                                   content_hash=secure_hash)
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test08_no_mimetype(self):
        # Download with no hash
        _logger.info("Starting...")
        self.filename = core.retrieve_tempfile(self.url)
        st = os.stat(self.filename)
        self.assertTrue(stat.S_ISREG(st.st_mode))
        self.assertEqual(st.st_size, self.content_lenght)
        d = core.get_file_hash(self.filename,
                               self.content_hash[0])
        self.assertEqual(d.hexdigest(),
                         self.content_hash[1])
        _logger.info("Completed")

    def test09_unexpected_mimetype(self):
        # Download with an unexpected hash value
        _logger.info("Starting...")
        with self.assertRaises(core.UnexpectedContentTypeError):
            self.filename = core.retrieve_tempfile(self.url,
                                                   content_type="text/plain")
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test10_bad_domain(self):
        # Download with an url having a bad domain name
        _logger.info("Starting...")
        url = "https://nodomain.fr/nofile.bin"
        with self.assertRaises(urllib.error.URLError):
            self.filename = core.retrieve_tempfile(url)

        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test11_non_existant_url(self):
        # Download with a non-existent URL
        _logger.info("Starting...")
        url = "https://github.com/fmezou/lappupdate/archive/0.0.0.zip"
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.filename = core.retrieve_tempfile(url)

        self.assertEqual(cm.exception.code, 404)
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")

    def test12_forbidden_url(self):
        # Download with a forbidden URL
        _logger.info("Starting...")
        url = "http://ftp.free.fr/lost%2bfound/"
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.filename = core.retrieve_tempfile(self.url)

        self.assertEqual(cm.exception.code, 403)
        with self.assertRaises(FileNotFoundError):
            st = os.stat(self.filename)
        _logger.info("Completed")


#TODO (fmu): même test avec lenght à -1 (test core.py - line 619)
# import http.server
# a = http.server.SimpleHTTPRequestHandler()
# creation de son propre serveur web basé sur BaseHTTPRequestHandler
# avec une retour spécifique sur une URL
# code erreor (401, 301...)
# header spécifique : content-lengh : absent par exemple
# import pydoc
# pydoc.doc()

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
        handler=core.get_handler("cots.dummy.DummyHandler")
        self.assertIsInstance(handler, core.BaseProduct)

        handler=core.get_handler("cots.mock.MockHandler")
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
            _logger.info("(qualname=%s)",qualname)
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

if __name__ == '__main__':
    unittest.main()

