"""
appdownload - check and download applications' updates if any.


Synopsis
========

:synopsis: appdownload.py [-h] [-p|-f|-a [-y]|-m|-t] [-v] [-c FILE]


Description
===========
Pull update information from the editor information channel (web, rss..), fetch
the update and store it on the local server and generate an applist file for
deploying the application with the ``appdeploy`` script. A plug-in handles
information sources to determine if an update is published and fetch it.


======  =====================   ================================================
``-h``  ``--help``              show this help message and exit
``-p``  ``--pull``              pull the availability of updates
``-f``  ``--fetch``             fetch applications updates based on the last
                                build catalog (useful to recover a crashed
                                application storage)
``-a``  ``--approve``           approve the deployment of applications. With
                                the option –y, applications are approved without
                                any interaction. If the option ``–y`` isn't
                                present, each application will has to be
                                approved in interactive mode on the console
``-m``  ``--make``              make applist files based on the last build
                                catalog (useful to make applist files after a
                                configuration modification)
``-t``  ``--testconf``          check the configuration file for internal
                                correctness
``-y``  ``--yes``               force applications approval (see ``--approve``)
``-c``  ``--configfile FILE``   specifies the configuration file. It includes
                                the list of handled applications, the file
                                :file:`appdownload.example.ini` details
                                configuration topics. The default configuration
                                file name is 'appdownload.ini' located
                                in the current working directory.
``-v``  ``--version``           show program's version number and exit
======  =====================   ================================================


Exit code
=========

==  ============================================================================
0   no error
1   an error occurred (error messages are print on stderr stream console
    and write in a log file).
2   invalid argument. An argument of the command line isn't valid (see Usage).
==  ============================================================================


Catalog format
==============

The catalog is a file which is automatically generated, and **must not be
manually modified**. It contains the applications database and specifies the
following properties, for each application, using the JavaScript Object Notation
(JSON), specified by :rfc:`7159` and by `ECMA-404 <http://www.ecma-international
.org/publications/standards/Ecma-404.htm>`_. The ``appdownload.py`` script uses
this database to build the applist files used by the appdeploy script.

The constant :py:const:`_CATALOG_FNAME` specifies the file name of the catalog
(``catalog.json``) and it located in the `store` folder (see item ``store`` in
the configuration file).

The catalog contains several level of nested objects. The root level contains
the metadata of the database and the main object.

================    ============================================================
__version__         is the version number of the catalog scheme.
__warning__         is a warning message reminding that the content must be
                    modified.
modified            is the date of the latest modification in `ISO 8601
                    <https://en.wikipedia.org/wiki/ISO_8601>`_ format.
products            is an object specifying the list of handled application as
                    described in the configuration file (see ``--configfile``).
================    ============================================================

Each item of the products list is a 3-tuple specifying the deployment state of
the application.

================    ============================================================
pulled              indicate that the editor of the application has published an
                    update or a new major version.
fetched             indicate that an update or a new major version of the
                    application has been fetched. At this step, the system
                    administrator must approved the version before its
                    deployment (see ``--approve``)
approved            indicate that the system administrator approved the
                    deployment of the update or the new version. This version
                    will be added in the applist file (see ``--make``) to be
                    deployed.
================    ============================================================

Each item of the 3-tuple is an object containing the following attributes of the
application.

================    ============================================================
name                is the name of the product (used in a_report mail and log
                    file)
display_name        is the name of the product as it appears in the 'Programs
                    and Features' control panel (see `Uninstall Registry Key
                    <https://msdn.microsoft.com/en-us/library/aa372105%28v=vs.85
                    %29.aspx>`_)
version             is the current version of the product.
published           is the date of the installer’s publication (in `ISO 8601
                    <https://en.wikipedia.org/wiki/ISO_8601>`_ format, see also
                    :rfc:`3339`).
description         is a short description of the product (~250 characters)
editor              is the name of the editor of the product
url                 is the url of the current version of the installer
file_size           is the size of the product installer expressed in bytes
secure_hash         is the secure hash value of the product installer. It's a
                    tuple containing, in this order, the name of secure hash
                    algorithm (see :py:data:`hashlib.algorithms_guaranteed`)
                    and the secure hash value in hexadecimal notation.
icon                is the name of the icon file located in the same directory
                    than the installer.
target              is the target architecture type (the Windows’ one) for the
                    application. This argument must be one of the following
                    values: ``x86``, ``x64`` or ``unified``.

                    * ``x86``: the application works only on 32 bits
                      architecture
                    * ``x64``: the application works only on 64 bits
                      architecture
                    * ``unified``: the application or the installation program
                      work on both architectures

release_note        is the release note’s URL for the current version of the
                    application
installer           is the path of the installer.
std_inst_args       are the arguments of the installer command line to make an
                    standard installation (i.e. an interactive installation).
silent_inst_args    are the arguments of the installer command line to make
                    an silent installation (i.e. without any user's interaction,
                    typically while an automated deployment using ``appdeploy``
                    script).
================    ============================================================

example
-------

.. code-block:: json

    {
        "__version__": "0.2.0",
        "__warning__": "This file is automatically generated, and must not be
        manually modified. It contains the applications database and specifies
        for each application its properties. Appdownload script uses this
        database to build the applist files used by appdeploy script.",
        "modified": "2016-02-28T19:30:00",
        "products": {
            "dummy": {
                "approved": {
                    "description": "This dummy module is a trivial example of a
                    Product class implementation. ",
                    "display_name": "Dummy Product (1.0.1)",
                    "editor": "Example. inc",
                    "file_size": -1,
                    "icon": "",
                    "installer": "tempstore\\dummy\\Dummy Product_1.0.1.html",
                    "name": "Dummy Product",
                    "published": "2016-02-28T19:04:43",
                    "release_note": "http://www.example.com/release_note.txt",
                    "secure_hash": null,
                    "silent_inst_args": "/silent",
                    "std_inst_args": "",
                    "target": "unified",
                    "url": "http://www.example.com/index.html",
                    "version": "1.0.1"
                },
                "fetched": {},
                "pulled": {}
            },
            ....
        }
    }
"""
import io
import os.path
import datetime
import argparse
import configparser
import importlib
import logging
import logging.config
import json

from cots import report


__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


# Sections and keys names used in the configuration file (see appdownload.ini)
_CORE_SNAME = "core"
_STORE_KNAME = "store"
_LOGGER_KNAME = "logger"
_PULL_REPORT_KNAME = "pulling_report"
_FETCH_REPORT_KNAME = "fetching_report"
_APPROVE_REPORT_KNAME = "approving_report"

_APPS_SNAME = "applications"
_INSTALL_KNAME = "install"
_QUALNAME_KNAME = "qualname"
_PACKAGE_NAME = "cots"
_PATH_KNAME = "path"
_SET_KNAME = "set"

_SETS_SNAME = "sets"

# Sections and keys names used in the catalog file (see catalog.json)
_CATALOG_FNAME = "catalog.json"
_CAT_WARNING_KNAME = "__warning__"
_CAT_WARNING = \
    "This file is automatically generated, and must not be manually modified. "\
    "It contains the applications database and specifies for each application "\
    "its properties. Appdownload script uses this database to build the "\
    "applist files used by appdeploy script."
_CAT_VERSION_KNAME = "__version__"
_CAT_VERSION = "0.2.0"
_CAT_MODIFIED_KNAME = "modified"
_CAT_PRODUCTS_KNAME = "products"
_CAT_PULLED_KNAME = "pulled"
_CAT_FETCHED_KNAME = "fetched"
_CAT_APPROVED_KNAME = "approved"

_PROD_NAME_KNAME = "name"
_PROD_VERSION_KNAME = "version"
_PROD_TARGET_KNAME = "target"
_PROD_INSTALLER_KNAME = "installer"
_PROD_SILENT_INSTALL_ARGS_KNAME = "silent_inst_args"

# APPLIST files
_APPLIST_SEP = ";"
_APPLIST_PREFIX = "applist-"
_APPLIST_EXT = ".txt"

# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Error(Exception):
    """Base class for AppDownload exceptions."""
    def __init__(self, message=""):
        """
        Constructor.

        :param message: is the message explaining the reason of the
            exception raise.
        """
        self.message = message

    def __str__(self):
        return self.message


class ConfigurationError(Error):
    """
    Raised when a key or a value is erroneous in a configuration file.
    """
    def __init__(self, filename, message, solution=""):
        """
        Constructor.

        :param filename: is the path name (full or partial) of the configuration
            file.
        :param message: is a string detailing the error.
        :param solution: is a recommendation to solve the error.
        """
        msg = "Configuration error in '{}': {} {}"
        Error.__init__(self, msg.format(filename, message, solution))
        self.filename = filename
        self.message = message
        self.solution = solution


class AppDownload:
    """
    Application class.

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
        """
        Constructor.

        :param config_file: is the name of the configuration file. It may
            be a partial or a full path.
        """
        # check parameters type
        if not isinstance(config_file, io.TextIOBase):
            msg = "config_file argument must be a class 'io.TextIOBase'. " \
                  "not {0}"
            msg = msg.format(config_file.__class__)
            raise TypeError(msg)

        # initialise the configuration based on ConfigParser module.
        self._config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())
        self._checked_config = False
        self._config_file = config_file
        self._pulling_report = None
        self._fetching_report = None
        self._approving_report = None

        # initialise the application catalog.
        self._catalog_filename = ""
        self._catalog = None

        # a_report
        self._report = ""

        msg = "Instance of {} created <- {}"
        _logger.debug(msg.format(self.__class__, config_file))

    def run(self):
        """
        Run the AppDownload application.
        """
        self._load_config()
        _logger.info("Starting Appdownload (%s)", __version__)
        self._read_catalog()
        self._pull_update()
        self._fetch_update()
        self._write_catalog()
        self._write_applist()
        _logger.info("Appdownload (%s) completed.", __version__)

    def pull(self):
        """
        Pull the availability of updates.
        """
        self._load_config()
        _logger.info("Starting Appdownload (%s), pull the availability of "
                     "updates.", __version__)
        self._read_catalog()
        self._pull_update()
        self._write_catalog()
        _logger.info("Appdownload (%s) completed.", __version__)

    def fetch(self):
        """
        Fetch applications updates based on the last build catalog.
        """
        self._load_config()
        _logger.info("Starting Appdownload (%s), Fetch applications updates "
                     "based on the last build catalog.", __version__)
        self._read_catalog()
        self._fetch_update()
        self._write_catalog()
        _logger.info("Appdownload (%s) completed.", __version__)

    def approve(self, force=False):
        """
        Approve the deployment of applications.

        :param force: is a boolean indicates if the user (sysadmin) must
            approved each deployment in a interactive session.
        """
        self._load_config()
        _logger.info("Starting Appdownload (%s), approve applications updates "
                     "based on the last build catalog.", __version__)
        self._read_catalog()
        self._approve_update(force)
        self._write_catalog()
        self._write_applist()
        _logger.info("Appdownload (%s) completed.", __version__)

    def make(self):
        """
        Make applist files based on the last build catalog
        """
        self._load_config()
        _logger.info("Starting Appdownload (%s), make applist files based "
                     "on the last build catalog.", __version__)
        self._read_catalog()
        self._write_applist()
        _logger.info("Appdownload (%s) completed.", __version__)

    def test_config(self):
        """
        Check the configuration file for internal correctness.
        """
        # The logging configuration may be not valid, events are only print on
        # the console with print(). Furthermore, the use case of this method is
        # typically in interactive mode.
        print("Starting Appdownload ({0}), check the configuration file for "
              "internal correctness.".format(__version__))
        print("Configuration details are loaded from '{0}'."
              .format(self._config_file.name))
        self._load_config()
        if self._checked_config:
            print("Configuration details are validated.")
        print("Appdownload ({0}) completed.".format(__version__))

    def _pull_update(self):
        """
        Pull the availability of updates.
        """
        assert self._checked_config is True
        _logger.info("Pull the availability of updates.")

        for app_id in self._config[_APPS_SNAME]:
            if self._config[_APPS_SNAME].getboolean(app_id):
                _logger.debug(
                    "Load and set the '{0}' module.".format(app_id)
                )
                qualname = self._config[app_id][_QUALNAME_KNAME]
                app_mod = importlib.import_module(qualname)
                app = app_mod.Product()
                if app_id in self._catalog[_CAT_PRODUCTS_KNAME]:
                    app_entry = self._catalog[_CAT_PRODUCTS_KNAME][app_id]
                    if len(app_entry[_CAT_APPROVED_KNAME]) != 0:
                        app.load(app_entry[_CAT_APPROVED_KNAME])
                        _logger.debug("Check if an update is available")
                        origin_app = app_mod.Product()
                        origin_app.get_origin(app.version)
                        if origin_app.is_update(app):
                            msg = "A new version of '{0}' exist ({1}) " \
                                  "published on {2}."
                            _logger.info(msg.format(app_id,
                                                    origin_app.version,
                                                    origin_app.published))
                            app_entry[_CAT_PULLED_KNAME] = origin_app.dump()
                            self._pulling_report.add_section(origin_app.dump())
                    else:
                        msg = "The product '{0}' isn't deployed.".format(app_id)
                        _logger.info(msg.format(app_id))
                        origin_app = app_mod.Product()
                        origin_app.get_origin()
                        msg = "A version of '{0}' exist ({1}) " \
                              "published on {2}."
                        _logger.info(msg.format(app_id,
                                                origin_app.version,
                                                origin_app.published))
                        app_entry[_CAT_PULLED_KNAME] = origin_app.dump()
                        self._pulling_report.add_section(origin_app.dump())
                else:
                    msg = "The product '{0}' don't exist. A new one will " \
                          "be created.".format(app_id)
                    _logger.warning(msg)
                    self._catalog[_CAT_PRODUCTS_KNAME][app_id] = {
                        _CAT_PULLED_KNAME: {},
                        _CAT_FETCHED_KNAME: {},
                        _CAT_APPROVED_KNAME: {}
                    }
                    _logger.debug("Check if an update is available")
                    origin_app = app_mod.Product()
                    origin_app.get_origin()
                    msg = "A version of '{0}' exist ({1}) " \
                          "published on {2}."
                    _logger.info(msg.format(app_id,
                                            origin_app.version,
                                            origin_app.published))
                    app_entry = self._catalog[_CAT_PRODUCTS_KNAME][app_id]
                    app_entry[_CAT_PULLED_KNAME] = origin_app.dump()
                    self._pulling_report.add_section(origin_app.dump())

                del app
                del origin_app
                del app_mod
                _logger.debug("'{0}' checked.".format(app_id))
            else:
                _logger.info("'{0}' ignored.".format(app_id))

        self._pulling_report.publish()

    def _fetch_update(self):
        """
        Fetch applications updates based on the last build catalog.
        """
        assert self._checked_config is True

        _logger.info("Fetch applications updates based on the last build "
                     "catalog.")
        for app_id in self._config[_APPS_SNAME]:
            if self._config[_APPS_SNAME].getboolean(app_id):
                _logger.debug(
                    "Load and set the '{0}' module.".format(app_id)
                )
                mod_name = self._config[app_id][_QUALNAME_KNAME]
                app_mod = importlib.import_module(mod_name)
                app = app_mod.Product()
                if app_id in self._catalog[_CAT_PRODUCTS_KNAME]:
                    app_entry = self._catalog[_CAT_PRODUCTS_KNAME][app_id]
                    if len(app_entry[_CAT_PULLED_KNAME]) != 0:
                        app.load(app_entry[_CAT_PULLED_KNAME])
                        _logger.debug("Fetch the update.")
                        app.fetch(self._config[app_id][_PATH_KNAME])
                        msg = "New version of '{0}' fetched. saved as '{1}'."
                        _logger.info(msg.format(app_id, app.installer))

                        # replace the fetched product by the newest.
                        app_entry[_CAT_FETCHED_KNAME] = app.dump()
                        app_entry[_CAT_PULLED_KNAME] = {}
                        self._fetching_report.add_section(app.dump())
                    else:
                        msg = "No update for product '{0}'."
                        _logger.info(msg.format(app_id))
                else:
                    msg = "The product '{0}' don't exist. Request ignored."
                    _logger.warning(msg.format(app_id))

                del app
                del app_mod
            else:
                _logger.info("'{0}' ignored.".format(app_id))

        self._fetching_report.publish()

    def _approve_update(self, force):
        """
        Approve the deployment of applications.

        :param force: is a boolean indicates if the user (sysadmin) must
            approved each deployment in a interactive session.
        """
        # check parameters type
        if not isinstance(force, bool):
            msg = "force argument must be a class 'bool'. " \
                  "not {0}"
            msg = msg.format(force.__class__)
            raise TypeError(msg)

        assert self._checked_config is True

        # The expected response to the approval
        expected_resp = {
            "Y": True,
            "y": True,
            "": False,
            "N": False,
            "n": False
        }

        _logger.info("Approve the deployment of applications.")
        for app_id in self._config[_APPS_SNAME]:
            if self._config[_APPS_SNAME].getboolean(app_id):
                if app_id in self._catalog[_CAT_PRODUCTS_KNAME]:
                    app_entry = self._catalog[_CAT_PRODUCTS_KNAME][app_id]
                    if len(app_entry[_CAT_FETCHED_KNAME]) != 0:
                        app = app_entry[_CAT_FETCHED_KNAME]
                        approved = False
                        if not force:
                            prompt = "Approve {} ({}) (y/n) [n]:".format(
                                app[_PROD_NAME_KNAME], app[_PROD_VERSION_KNAME]
                            )
                            while True:
                                resp = input(prompt)
                                if resp in expected_resp:
                                    approved = expected_resp[resp]
                                    break
                                else:
                                    msg = "Unexpected response : only y or n," \
                                          " n is the default value."
                                    print(msg)
                        else:
                            approved = True

                        if approved:
                            # replace the approved product by the newest.
                            app = app_entry[_CAT_FETCHED_KNAME]
                            app_entry[_CAT_APPROVED_KNAME] = app
                            app_entry[_CAT_FETCHED_KNAME] = {}
                            self._approving_report.add_section(app)
                            msg = "The product '{0}' approved."
                            _logger.info(msg.format(app_id))
                        else:
                            msg = "The product '{0}' not approved."
                            _logger.info(msg.format(app_id))
                else:
                    msg = "The product '{0}' don't exist. Request ignored."
                    _logger.warning(msg.format(app_id))
            else:
                _logger.info("'{0}' ignored.".format(app_id))

        self._approving_report.publish()

    def _load_config(self):
        """
        Load the configuration details from the configuration file.
        """
        # Load the configuration, and set the logging configuration from it.
        # I'am still using the fileConfig() method instead of dictConfig() to
        # keep the configuration in a ini file, which is easy to write and to
        # read for a human.
        self._config.read_file(self._config_file)

        # Check the core section
        if _CORE_SNAME in self._config.sections():
            section = self._config[_CORE_SNAME]
            # 'store' key is mandatory
            if _STORE_KNAME in section:
                # Set the catalog filename (absolute path).
                os.makedirs(
                    self._config[_CORE_SNAME][_STORE_KNAME],
                    exist_ok=True
                )
                self._catalog_filename = os.path.join(
                    self._config[_CORE_SNAME][_STORE_KNAME],
                    _CATALOG_FNAME
                )
                self._catalog_filename = os.path.abspath(self._catalog_filename)
            else:
                msg = "the key '{}' is missing in section '{}'."
                msg = msg.format(_STORE_KNAME, _CORE_SNAME)
                raise ConfigurationError(self._config_file.name, msg)

            # 'logger' key is optional
            if _LOGGER_KNAME in section:
                filename = self._config[_CORE_SNAME][_LOGGER_KNAME]
                if os.path.isfile(filename):
                    logging.config.fileConfig(filename,
                                              disable_existing_loggers=False)
                else:
                    msg = "configuration file specified in '{}' key doesn't" \
                          "exist (see section '{}')."
                    msg = msg.format(_LOGGER_KNAME, _CORE_SNAME)
                    raise ConfigurationError(self._config_file.name, msg)

            # 'pulling_report' key is optional
            if _PULL_REPORT_KNAME in section:
                filename = self._config[_CORE_SNAME][_PULL_REPORT_KNAME]
                if os.path.isfile(filename):
                    self._pulling_report = report.Report()
                    config = _load_config(filename)
                    self._pulling_report.load_config(config, False)
                else:
                    msg = "configuration file specified in '{}' key doesn't" \
                          "exist (see section '{}')."
                    msg = msg.format(_PULL_REPORT_KNAME, _CORE_SNAME)
                    raise ConfigurationError(self._config_file.name, msg)

            # 'fetching_report' key is optional
            if _FETCH_REPORT_KNAME in section:
                filename = self._config[_CORE_SNAME][_FETCH_REPORT_KNAME]
                if os.path.isfile(filename):
                    self._fetching_report = report.Report()
                    config = _load_config(filename)
                    self._fetching_report.load_config(config, False)
                else:
                    msg = "configuration file specified in '{}' key doesn't" \
                          "exist (see section '{}')."
                    msg = msg.format(_FETCH_REPORT_KNAME, _CORE_SNAME)
                    raise ConfigurationError(self._config_file.name, msg)

            # 'approving_report' key is optional
            if _APPROVE_REPORT_KNAME in section:
                filename = self._config[_CORE_SNAME][_APPROVE_REPORT_KNAME]
                if os.path.isfile(filename):
                    self._approving_report = report.Report()
                    config = _load_config(filename)
                    self._approving_report.load_config(config, False)
                else:
                    msg = "configuration file specified in '{}' key doesn't" \
                          "exist (see section '{}')."
                    msg = msg.format(_APPROVE_REPORT_KNAME, _CORE_SNAME)
                    raise ConfigurationError(self._config_file.name, msg)
        else:
            msg = "the section '{}' is missing.".format(_CORE_SNAME)
            raise ConfigurationError(self._config_file.name, msg)

        # Check the sets section
        if _SETS_SNAME in self._config.sections():
            sets = self._config[_SETS_SNAME]
        else:
            msg = "the section '{}' is missing.".format(_SETS_SNAME)
            raise ConfigurationError(self._config_file.name, msg)

        # Check the applications section
        if _APPS_SNAME in self._config.sections():
            for app_name in self._config[_APPS_SNAME]:
                if self._config[_APPS_SNAME].getboolean(app_name):
                    # Pre compute default value for the Application section
                    app_module = ".".join((_PACKAGE_NAME, app_name))
                    store_path = self._config[_CORE_SNAME][_STORE_KNAME]
                    app_path = os.path.join(store_path, app_name)
                    app_set = "__all__"

                    # Checks the item in the application section
                    # If a section or a key is missing, it is added in the
                    # config object, so this object will contain a complete
                    # configuration
                    if app_name in self._config.sections():
                        app_desc = self._config[app_name]
                        if _QUALNAME_KNAME not in app_desc:
                            app_desc[_QUALNAME_KNAME] = app_module
                        if _PATH_KNAME not in app_desc:
                            app_desc[_PATH_KNAME] = app_path
                        # 'set' key must be declared in the sets section if it
                        # exist.
                        if _SET_KNAME in app_desc:
                            if app_desc[_SET_KNAME] in sets:
                                pass
                            else:
                                msg = "'set' value '{}' is not declared in " \
                                      "'sets' section (see {} application)"
                                msg = msg.format(app_desc[_SET_KNAME], app_name)
                                raise ConfigurationError(self._config_file.name,
                                                         msg)
                        else:
                            app_desc[_SET_KNAME] = app_set
                    else:
                        # Set the default value
                        self._config[app_name] = {}
                        app_desc = self._config[app_name]
                        app_desc[_QUALNAME_KNAME] = app_module
                        app_desc[_PATH_KNAME] = app_path
                        app_desc[_SET_KNAME] = app_set
        else:
            msg = "the section '{}' is missing.".format(_APPS_SNAME)
            raise ConfigurationError(self._config_file.name, msg)

        # Checked
        self._checked_config = True
        self._config_file.close()
        self._config_file = None

    def _read_catalog(self):
        """
        Load the product's catalog.
        """
        msg = "Load the products' catalog ({0}).".format(self._catalog_filename)
        _logger.info(msg)
        try:
            with open(self._catalog_filename, "r+t") as file:
                self._catalog = json.load(file)
                # force the version number.
                # at time, there is non need to have a update function
                self._catalog[_CAT_VERSION_KNAME] = _CAT_VERSION
        except FileNotFoundError:
            # the catalog may be not exist
            _logger.warning("The product's catalog don't exist. A new one "
                            "will be created.")
            self._catalog = {
                _CAT_WARNING_KNAME: _CAT_WARNING,
                _CAT_VERSION_KNAME: _CAT_VERSION,
                _CAT_MODIFIED_KNAME: None,
                _CAT_PRODUCTS_KNAME: {}
            }
        else:
            msg = "Products' catalog loaded."
            _logger.info(msg)

    def _write_catalog(self):
        """
        Write the catalog product file.
        """
        msg = "Write the products' catalog ({0})."
        _logger.info(msg.format(self._catalog_filename))

        with open(self._catalog_filename, "w+t") as file:
            # write the warning header with a naive time representation.
            dt = (datetime.datetime.now()).replace(microsecond=0)
            self._catalog[_CAT_MODIFIED_KNAME] = dt.isoformat()
            json.dump(self._catalog, file, indent=4, sort_keys=True)
        msg = "Products' catalog saved"
        _logger.info(msg)

    def _write_applist(self):
        """
        Write the applist files from the catalog.
        """
        _logger.info("Write the applist files from the catalog.")
        app_set_file = {}

        header = \
            "# --------------------------------------------------------------" \
            "----------------\n"\
            "# This applist file generated on {0} for '{1}'.\n"\
            "# This file is automatically generated, and must not be " \
            "manually modified.\n"\
            "# Please modify the configuration file instead (appdowload.ini " \
            "by default).\n"\
            "# -------------------------------------------------------------" \
            "-----------------\n"

        for app_id in self._config[_APPS_SNAME]:
            if self._config[_APPS_SNAME].getboolean(app_id):
                if app_id in self._catalog[_CAT_PRODUCTS_KNAME]:
                    app_entry = self._catalog[_CAT_PRODUCTS_KNAME][app_id]
                    if len(app_entry[_CAT_APPROVED_KNAME]) != 0:
                        app = app_entry[_CAT_APPROVED_KNAME]
                        # build the catalog line
                        app_line = \
                            app[_PROD_TARGET_KNAME] + _APPLIST_SEP + \
                            app[_PROD_NAME_KNAME] + _APPLIST_SEP + \
                            app[_PROD_VERSION_KNAME] + _APPLIST_SEP + \
                            app[_PROD_INSTALLER_KNAME] + _APPLIST_SEP + \
                            app[_PROD_SILENT_INSTALL_ARGS_KNAME]

                        store_path = self._config[_CORE_SNAME][_STORE_KNAME]
                        app_set_name = self._config[app_id][_SET_KNAME]
                        comps = self._config[_SETS_SNAME][app_set_name]
                        comp_set = comps.split(",")
                        for comp_name in comp_set:
                            comp_name = comp_name.strip()
                            filename = _APPLIST_PREFIX + comp_name + _APPLIST_EXT
                            filename = os.path.join(store_path, filename)
                            if comp_name not in app_set_file:
                                file = open(filename, "w+t")
                                app_set_file[comp_name] = file
                                _logger.info(
                                    "'{0}' applist file created -> '{1}'.".format(
                                        comp_name, filename
                                    )
                                )
                                dt = (datetime.datetime.now()).replace(microsecond=0)
                                file.write(header.format(dt.isoformat(), comp_name))
                            else:
                                file = app_set_file[comp_name]
                            file.write(app_line + "\n")
                    else:
                        msg = "The product '{0}' is not approved."
                        _logger.info(msg.format(app_id))
                else:
                    msg = "The product '{0}' don't exist. Request ignored."
                    _logger.warning(msg.format(app_id))
            else:
                _logger.info("'{0}' ignored.".format(app_id))

        # Terminate by closing the files
        for comp_name, file in app_set_file.items():
            file.close()


def _load_config(filename):
    """
    Load the configuration from a configuration file (see [`config.parser`]
    (https://docs.python.org/3/library/configparser.html#module-configparser)

    The configuration is stored in a dictionary with the same structure as the
    configuration file.

    :param filename: is the full path name of the configuration file.
    :return: a dictionary containing the configuration.
    """
    config = configparser.ConfigParser()
    with open(filename) as file:
        config.read_file(file)

    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            config_dict[section][option] = config.get(section, option)

    return config_dict

if __name__ == "__main__":
    # Entry point
    # Build the command line parser
    parser = argparse.ArgumentParser(
        description="Check and download applications\' updates if any.")
    general = parser.add_mutually_exclusive_group()
    general.add_argument("-p", "--pull", action="store_true",
                         help="pull the availability of updates")
    general.add_argument("-f", "--fetch", action="store_true",
                         help="fetch applications updates based on the last "
                              "build catalog (useful to recover a crashed "
                              "application storage)")
    general.add_argument("-a", "--approve", action="store_true",
                         help="approve the deployment of applications. With "
                              "the option -y, applications are approved "
                              "without any interaction. If the option -y isn't "
                              "present, each application will has to be "
                              "approved in interactive mode on the console.")
    general.add_argument("-m", "--make", action="store_true",
                         help="make applist files based on the last build "
                              "catalog (useful to make applist files after a "
                              "configuration modification)")
    general.add_argument("-t", "--testconf", action="store_true",
                         help="check an appdownload.ini configuration file for "
                              "internal correctness")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="force applications approval (see --approve)")
    parser.add_argument("-c", "--configfile", default="appdownload.ini",
                        type=argparse.FileType(mode='r'),
                        help="The file specified contains the configuration "
                             "details. Information in this file includes "
                             "application catalog. The file 'appdownload."
                             "example.ini' details configuration topics. The "
                             "default configuration file name is "
                             "'appdownload.ini' located in the current working "
                             "directory.")
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s version " + __version__)

    # Parse and run.
    args = parser.parse_args()
    main_task = AppDownload(args.configfile)
    if args.pull:
        main_task.pull()
    elif args.fetch:
        main_task.fetch()
    elif args.approve:
        main_task.approve(args.yes)
    elif args.make:
        main_task.make()
    elif args.testconf:
        main_task.test_config()
    else:
        main_task.run()
