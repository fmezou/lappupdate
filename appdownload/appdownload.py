"""Check and download applications' updates if any.

Usage
appdownload.py [-h] [-c | -d | -t] [--version]

optional arguments:
  -h, --help            show this help message and exit
  -c, --checkonly       check and report if applications' updates are
                        available without download it
  -d, --download        download applications' updates based on the last build
                        catalog (useful to recover a crashed application
                        storage)
  -t, --testconf        check an appdownload.ini configuration file for
                        internal correctness
  --configfile CONFIGFILE
                        The file specified contains the configuration details.
                        The information in this file includes application
                        catalog. See appdownload.ini for more information.
                        The default configuration file name is 'appdownload.ini'
                        located in the current working directory.
  --version             show program's version number and exit

Exit code
  0: no error
  1: an error occurred (error messages are print on stderr stream console
     and write in a log file.
  2: invalid argument. An argument of the command line isn't valid (see Usage).

Environment variables
The following environment variables affect the execution of this script:
#TODO:
"""

import io
import os.path
import datetime
import argparse
import configparser
import importlib

# TODO: rename core in interface (separate core class from interface)
from cots import core


__author__ = "Frederic MEZOU"
__version__ = "0.3.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


# Section and value name used in the configuration file (see appdownload.ini)
_APPS_LIST_SECT_NAME = "applications"
_APP_INSTALL_KEY_NAME = "install"
_APP_MODULE_KEY_NAME = "module"

_CORE_SECT_NAME = "core"
_STORE_KEY_NAME = "store"
_CATALOG_FILE_NAME = "catalog.ini"

# Section and value name used in the catalog file (see catalog.ini)
_PROD_NAME_KEY_NAME = "name"
_PROD_VERSION_KEY_NAME = "version"
_PROD_PUBDATE_KEY_NAME = "published"
_PROD_TARGET_KEY_NAME = "target"
_PROD_TARGET_X86 = "x86"
_PROD_TARGET_X64 = "x64"
_PROD_TARGET_UNIFIED = "unified"
_PROD_REL_NOTE_URL_KEY_NAME = "release_note"
_PROD_INSTALLER_KEY_NAME = "installer"
_PROD_STD_INSTALL_ARGS_KEY_NAME = "std_inst_args"
_PROD_SILENT_INSTALL_ARGS_KEY_NAME = "silent_inst_args"


class Error(Exception):
    """Base class for AppDownload exceptions."""

    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return self.message


class MissingMandatorySectionError(Error):
    """Raised when a mandatory section is missing."""

    def __init__(self, section_name):
        """constructor.

        Parameters
            section_name: Name of the missing section.
        """
        msg = "Section '{0}' is missing."
        Error.__init__(self, msg.format(section_name))
        self.section_name = section_name


class MissingApplSectionError(Error):
    """ Raised when an application description section is missing."""

    def __init__(self, section_name):
        """constructor.

        Parameters
            section_name: Name of the missing section.
        """
        msg = "Application description section '{0}' is missing."
        Error.__init__(self, msg.format(section_name))
        self.section_name = section_name


class MissingKeyError(Error):
    """ Raised when a key section is missing in a section."""

    def __init__(self, section_name, key_name):
        """constructor.

        Parameters
            section_name: Name of the section containing the missing key.
            key_name: name of missing key.
        """
        msg = "Key '{1}' is missing in '{0}' application description."
        Error.__init__(self, msg.format(section_name, key_name))
        self.section_name = section_name
        self.key_name = key_name


class AppDownload:
    """Application class.

    Public instance variables
        None

    Public methods
        None

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None
    """

    def __init__(self, config_file):
        """constructor.

        Parameters
            config_file: Name of the configuration file. The name may be a
            partial one or a full path one.
        """
        # check parameters type
        # TODO: use assert or raise a TypeError
        assert isinstance(config_file, io.TextIOBase), \
            "config_file argument must be a class 'io.TextIOBase'. not {0}"\
            .format(config_file.__class__)
        self._config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())
        self._checked_config = False
        self._config_file = config_file

        self._catalog_filename = None
        self._catalog = configparser.ConfigParser()

    def run(self):
        """run the AppDownload application.

        Parameters
            None
        """
        self.test_config()
        self.check()
        self.download()

    def check(self):
        """check and report if applications' updates are available without
         download it.

        Parameters
            None
        """
        self._load_config()
        self._read_catalog()
        for app_id in self._config[_APPS_LIST_SECT_NAME]:
            if self._config[_APPS_LIST_SECT_NAME].getboolean(app_id):
                print("Checking '{0}' product.".format(app_id))
                app_desc = self._config[app_id]
                app_mod = importlib.import_module(app_desc[_APP_MODULE_KEY_NAME])
                app = app_mod.Product()
                self._load_product(app_id, app)
                app.check_update()
                app.fetch_update()
                self._dump_product(app_id, app)
                del app
                del app_mod
                print("'{0}' product checked.".format(app_id))
            else:
                print("'{0}' product ignored.".format(app_id))

        self._write_catalog()

    def download(self):
        """download applications' updates based on the last build catalog.

        Parameters
            None
        """
        assert self._checked_config is True
        raise NotImplementedError

    def test_config(self):
        """check the configuration file for internal correctness.

        Parameters
            None
        """
        # raise NotImplementedError
        assert self._config_file is not None
        print("Checking the configuration details loaded from '{0}'."
              .format(self._config_file.name))
        self._load_config()
        if self._checked_config:
            print("Configuration details are validated.")
        else:
            print("Configuration details contain errors. see above for details")

    def _load_config(self):
        """load the configuration details from the configuration file.

        Parameters
            None
        """
        assert self._config_file is not None
        self._config.read_file(self._config_file)
        # Check the core section
        if _CORE_SECT_NAME in self._config.sections():
            core_section = self._config[_CORE_SECT_NAME]
            if _STORE_KEY_NAME in core_section:
                # Set the catalog filename (absolute path).
                self._catalog_filename = os.path.join(
                    self._config[_CORE_SECT_NAME][_STORE_KEY_NAME],
                    _CATALOG_FILE_NAME
                )
                self._catalog_filename = os.path.abspath(self._catalog_filename)
                print("DEBUG (_load_config) : catalog_fname =", self._catalog_filename)
            else:
                raise MissingKeyError(_STORE_KEY_NAME, _CORE_SECT_NAME)
        else:
            raise MissingMandatorySectionError(_CORE_SECT_NAME)

        # Check the applications section
        if _APPS_LIST_SECT_NAME in self._config.sections():
            for app_name in self._config[_APPS_LIST_SECT_NAME]:
                if self._config[_APPS_LIST_SECT_NAME].getboolean(app_name):
                    if app_name in self._config.sections():
                        app_desc = self._config[app_name]
                        if _APP_MODULE_KEY_NAME in app_desc:
                            pass
                        else:
                            raise MissingKeyError(app_name, _APP_MODULE_KEY_NAME)
                    else:
                        raise MissingApplSectionError(app_name)
        else:
            raise MissingMandatorySectionError(_APPS_LIST_SECT_NAME)
        # Checked
        self._checked_config = True
        self._config_file.close()
        self._config_file = None

    def _read_catalog(self):
        """load the product's catalog.

        Parameters
            None
        """
        try:
            with open(self._catalog_filename, "r+t") as file:
                self._catalog.read_file(file)
                for i,v in enumerate(self._catalog.sections()):
                    print("DEBUG (_read_catalog) : #{0} - v: {1}".format(i, v))
        except FileNotFoundError as err:
            print("_read_catalog", err)

    def _write_catalog(self):
        """write the catalog product file.

        Parameters
            None
        """
        header = \
            "# ------------------------------------------------------------------------------\n"\
            "# This file is automatically generated at {0},\n"\
            "# and must not be manually modified.\n"\
            "# It contains the applications database and specifies for each application the\n"\
            "# following properties. Appdownload script uses this database to build the\n"\
            "# applist files used by appdeploy script.\n"\
            "# ------------------------------------------------------------------------------\n"
        with open(self._catalog_filename, "w+t") as file:
            # write the warning header
            dt = (datetime.datetime.now()).replace(microsecond=0)
            file.write(header.format(dt.isoformat()))
            self._catalog.write(file)

    def _load_product(self, section_name, product):
        """Load a product class from the catalog.

        Parameters
            section_name: is the name of the product used as a section name is
              the application catalog.
            product: is the Product class to load

        If the section don't exist, the method do nothing and leave the default
        value of class properties.

        """
        # check parameters type
        # TODO: use assert or raise a TypeError
        assert isinstance(product, core.BaseProduct), \
            "product argument must be a class 'core.BaseProduct'. not {0}"\
                .format(product.__class__)
        assert isinstance(section_name, str), \
            "name argument must be a class 'str'. not {0}"\
                .format(section_name.__class__)

        if section_name in self._catalog.sections():
            app_properties = self._catalog[section_name]
            product.id = section_name
            if _PROD_NAME_KEY_NAME in app_properties:
                product.name = app_properties[_PROD_NAME_KEY_NAME]
            if _PROD_VERSION_KEY_NAME in app_properties:
                product.version = app_properties[_PROD_VERSION_KEY_NAME]
            if _PROD_PUBDATE_KEY_NAME in app_properties:
                product.published = app_properties[_PROD_PUBDATE_KEY_NAME]
            if _PROD_TARGET_KEY_NAME in app_properties:
                product.target = app_properties[_PROD_TARGET_KEY_NAME]
            if _PROD_REL_NOTE_URL_KEY_NAME in app_properties:
                product.release_note = app_properties[_PROD_REL_NOTE_URL_KEY_NAME]
            if _PROD_INSTALLER_KEY_NAME in app_properties:
                product.installer = app_properties[_PROD_INSTALLER_KEY_NAME]
            if _PROD_STD_INSTALL_ARGS_KEY_NAME in app_properties:
                product.std_inst_args = app_properties[_PROD_STD_INSTALL_ARGS_KEY_NAME]
            if _PROD_SILENT_INSTALL_ARGS_KEY_NAME in app_properties:
                product.silent_inst_arg = app_properties[_PROD_SILENT_INSTALL_ARGS_KEY_NAME]

    def _dump_product(self, section_name, product):
        """Dump a product class.

        Parameters
            section_name: is the name of the product used as a section name is
              the application catalog.
            product: is the Product class to dump
        """
        # check parameters type
        # TODO: use assert or raise a TypeError
        assert isinstance(product, core.BaseProduct), \
            "product argument must be a class 'core.BaseProduct'. not {0}"\
                .format(product.__class__)
        assert isinstance(section_name, str), \
            "name argument must be a class 'str'. not {0}"\
                .format(section_name.__class__)

        if section_name not in self._catalog.sections():
            self._catalog.add_section(section_name)
        else:
            # reset the section to delete any obsolete keys
            self._catalog.remove_section(section_name)
            self._catalog.add_section(section_name)
        app_properties = self._catalog[section_name]
        app_properties[_PROD_NAME_KEY_NAME] = product.name
        app_properties[_PROD_VERSION_KEY_NAME] = product.version
        app_properties[_PROD_PUBDATE_KEY_NAME] = product.published
        app_properties[_PROD_TARGET_KEY_NAME] = product.target
        app_properties[_PROD_REL_NOTE_URL_KEY_NAME] = product.release_note
        app_properties[_PROD_INSTALLER_KEY_NAME] = product.installer
        app_properties[_PROD_STD_INSTALL_ARGS_KEY_NAME] = product.std_inst_args
        app_properties[_PROD_SILENT_INSTALL_ARGS_KEY_NAME] = product.silent_inst_arg


if __name__ == "__main__":
    # Entry point
    # Build the command line parser
    parser = argparse.ArgumentParser(
        description="Check and download applications\' updates if any.")
    general = parser.add_mutually_exclusive_group()
    general.add_argument("-c", "--checkonly", action="store_true",
                         help="check and report if applications' updates are "
                              "available without download it")
    general.add_argument("-d", "--download", action="store_true",
                         help="download applications' updates based on the "
                              "last build catalog (useful to recover a crashed "
                              "application storage)")
    general.add_argument("-t", "--testconf", action="store_true",
                         help="check an appdownload.ini configuration file for "
                              "internal correctness")
    parser.add_argument("--configfile", default="appdownload.ini",
                        type=argparse.FileType(mode='r'),
                        help="The file specified contains the configuration "
                             "details. The information in this file includes "
                             "application catalog. See appdownload.ini for "
                             "more information. The default configuration file "
                             "name is 'appdownload.ini' located in the current "
                             "working directory.")
    parser.add_argument("--version", action="version",
                        version="%(prog)s version " + __version__)

    # Parse and run.
    args = parser.parse_args()
    main_task = AppDownload(args.configfile)
    if args.checkonly:
        main_task.check()
    elif args.download:
        main_task.download()
    elif args.testconf:
        main_task.test_config()
    else:
        main_task.run()
