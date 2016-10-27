"""
This module is in charge of plug-in handling and operations scheduling.
It may use as a module by a third party offering a new GUI for
example, or as a script with the command line interface::

    python -m appdownload

The `user manual`_ details use cases and the configuration files.


Synopsis
--------

appdownload.py [-h] [-p | -f | -a [-y]| -m | -t] [-v] [-c FILE]


Description
-----------
Pull update information from the editor information channel (web, rss..), fetch
the update, store it on the local server and generate an applist file for
deploying the application with the ``appdeploy`` script. A plug-in handles
information sources to determine if an update has been published, and to fetch
it.

All information about a handled :term:`product` are stored in a :term:`catalog`
file (see `catalog_format` section for a detailed description)


Command line options
^^^^^^^^^^^^^^^^^^^^

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
                                the list of handled applications, the
                                `appdownload.example.ini` details configuration
                                topics. The default configuration file name is
                                'appdownload.ini' located in the current working
                                directory.
``-v``  ``--version``           show program's version number and exit
======  =====================   ================================================


Exit code
^^^^^^^^^

==  ============================================================================
0   no error
1   an error occurred (error messages are print on stderr stream console
    and write in a log file).
2   invalid argument. An argument of the command line isn't valid (see Usage).
==  ============================================================================


Public Classes
--------------
This module has only one public class.

===================================  ===================================
`AppDownload`                        ..
===================================  ===================================


Public data
-----------
This module has a number of public global data, including both variables and
values used as 'defined constants' listed below in alphabetical order.

===================================  ===================================
`CATALOG_FNAME`                      `CAT_PULLED_KNAME`
`CAT_APPROVED_KNAME`                 `CAT_VERSION_KNAME`
`CAT_FETCHED_KNAME`                  `CAT_VERSION`
`CAT_MODIFIED_KNAME`                 `CAT_WARNING_KNAME`
`CAT_PRODUCTS_KNAME`                 ..
===================================  ===================================


Public Exceptions
-----------------
This module has only one exception.

===================================  ===================================
`ConfigurationError`                 ..
===================================  ===================================


.. _user manual: http://fmezou.github.io/lappupdate/lappupdate_wiki.html
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
import sys

import report


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
CATALOG_FNAME = "catalog.json"
"""Contain the file name of the catalog."""

CAT_WARNING_KNAME = "__warning__"
"""Contain the key name of the warning string of the catalog."""

_CAT_WARNING = \
    "This file is automatically generated, and must not be manually modified. "\
    "It contains the applications database and specifies for each application "\
    "its properties. Appdownload script uses this database to build the "\
    "applist files used by appdeploy script."

CAT_VERSION_KNAME = "__version__"
"""Contain the key name of the version string of the catalog."""

CAT_VERSION = "0.2.0"
"""Specify the current version of the catalog scheme."""

CAT_MODIFIED_KNAME = "modified"
"""Contain the key name of the latest modification date of the catalog."""

CAT_PRODUCTS_KNAME = "products"
"""Contain the key name of the list of handled application."""

CAT_PULLED_KNAME = "pulled"
"""Contain the key name of the object indicating the latest version of the
product available on the web site of the editor."""

CAT_FETCHED_KNAME = "fetched"
"""Contain the key name of the object indicating the latest fetched version of
the product."""

CAT_APPROVED_KNAME = "approved"
"""Contain the key name of the object indicating the latest approved version of
the product."""

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
    """
    Base class for AppDownload exceptions.

    Args:
        message (str, optional): Human readable string describing the exception.

    Attributes:
        message (str): Human readable string describing the exception.
    """
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return self.message


class ConfigurationError(Error):
    """
    Raised when a key or a value is erroneous in the configuration file.

    Args:
        filename (str): The path name (full or partial) of the configuration
            file.
        message (str): Human readable string describing the exception.
        solution (str, optional): Human readable string providing a
            recommendation to solve the error.

    Attributes:
        filename (str): The path name (full or partial) of the configuration
            file.
        message (str): Human readable string describing the exception.
        solution (str, optional): Human readable string providing a
            recommendation to solve the error.
    """
    def __init__(self, filename, message, solution=""):
        msg = "Configuration error in '{}': {} {}"
        Error.__init__(self, msg.format(filename, message, solution))
        self.filename = filename
        self.message = message
        self.solution = solution


class AppDownload:
    """
    Schedule products updates retrieving operations.


    Args:
        config_file (str): The name of the configuration file. It may
            be a partial or a full pathname.


    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `approve`                            `pull`
        `fetch`                              `run`
        `make`                               `test_config`
        ===================================  ===================================


    **Using AppDownload...**
        This class is the scheduler and handles elementary operations to
        complete the expected task.

        The easiest way of using this class is to call the `run` method. This
        all-in-one method retrieve information from the web site editor, fetch
        possible updates, and generate the `applist` files without any user
        action.

        To have more control, you must call individually each method. A typical
        use case is to fetch the possible update by calling the `pull` method
        then the `fetch` method, and approve each update by calling the
        `approve` method, and then generate the `applist` file with the `make`
        method.
    """

    def __init__(self, config_file):
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
        self._approve_update(True)
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
        Fetch application updates based on the last build catalog.
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

        Args:
            force (bool, optional): False to indicates if the user must approved
                each deployment in a interactive session. True to indicates that
                updates are all approved without prompt.
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
        Make `applist` files based on the last build catalog
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
                if app_id in self._catalog[CAT_PRODUCTS_KNAME]:
                    app_entry = self._catalog[CAT_PRODUCTS_KNAME][app_id]
                    if len(app_entry[CAT_APPROVED_KNAME]) != 0:
                        app.load(app_entry[CAT_APPROVED_KNAME])
                        _logger.debug("Check if an update is available")
                        origin_app = app_mod.Product()
                        origin_app.get_origin(app.version)
                        if origin_app.is_update(app):
                            msg = "A new version of '{0}' exist ({1}) " \
                                  "published on {2}."
                            _logger.info(msg.format(app_id,
                                                    origin_app.version,
                                                    origin_app.published))
                            app_entry[CAT_PULLED_KNAME] = origin_app.dump()
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
                        app_entry[CAT_PULLED_KNAME] = origin_app.dump()
                        self._pulling_report.add_section(origin_app.dump())
                else:
                    msg = "The product '{0}' don't exist. A new one will " \
                          "be created.".format(app_id)
                    _logger.warning(msg)
                    self._catalog[CAT_PRODUCTS_KNAME][app_id] = {
                        CAT_PULLED_KNAME: {},
                        CAT_FETCHED_KNAME: {},
                        CAT_APPROVED_KNAME: {}
                    }
                    _logger.debug("Check if an update is available")
                    origin_app = app_mod.Product()
                    origin_app.get_origin()
                    msg = "A version of '{0}' exist ({1}) " \
                          "published on {2}."
                    _logger.info(msg.format(app_id,
                                            origin_app.version,
                                            origin_app.published))
                    app_entry = self._catalog[CAT_PRODUCTS_KNAME][app_id]
                    app_entry[CAT_PULLED_KNAME] = origin_app.dump()
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
                if app_id in self._catalog[CAT_PRODUCTS_KNAME]:
                    app_entry = self._catalog[CAT_PRODUCTS_KNAME][app_id]
                    if len(app_entry[CAT_PULLED_KNAME]) != 0:
                        app.load(app_entry[CAT_PULLED_KNAME])
                        _logger.debug("Fetch the update.")
                        app.fetch(self._config[app_id][_PATH_KNAME])
                        msg = "New version of '{0}' fetched. saved as '{1}'."
                        _logger.info(msg.format(app_id, app.installer))

                        # replace the fetched product by the newest.
                        app_entry[CAT_FETCHED_KNAME] = app.dump()
                        app_entry[CAT_PULLED_KNAME] = {}
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

        Args:
            force (bool, optional): False to indicates if the user must approved
                each deployment in a interactive session. True to indicates
                that updates are all approved without prompt.
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
                if app_id in self._catalog[CAT_PRODUCTS_KNAME]:
                    app_entry = self._catalog[CAT_PRODUCTS_KNAME][app_id]
                    if len(app_entry[CAT_FETCHED_KNAME]) != 0:
                        app = app_entry[CAT_FETCHED_KNAME]
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
                            app = app_entry[CAT_FETCHED_KNAME]
                            app_entry[CAT_APPROVED_KNAME] = app
                            app_entry[CAT_FETCHED_KNAME] = {}
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
                    CATALOG_FNAME
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
                self._catalog[CAT_VERSION_KNAME] = CAT_VERSION
        except FileNotFoundError:
            # the catalog may be not exist
            _logger.warning("The product's catalog don't exist. A new one "
                            "will be created.")
            self._catalog = {
                CAT_WARNING_KNAME: _CAT_WARNING,
                CAT_VERSION_KNAME: CAT_VERSION,
                CAT_MODIFIED_KNAME: None,
                CAT_PRODUCTS_KNAME: {}
            }
        else:
            msg = "Products' catalog loaded."
            _logger.info(msg)

    def _write_catalog(self):
        """
        Write the catalog products file.
        """
        msg = "Write the products' catalog ({0})."
        _logger.info(msg.format(self._catalog_filename))

        with open(self._catalog_filename, "w+t") as file:
            # write the warning header with a naive time representation.
            dt = (datetime.datetime.now()).replace(microsecond=0)
            self._catalog[CAT_MODIFIED_KNAME] = dt.isoformat()
            json.dump(self._catalog, file, indent=4, sort_keys=True)
        msg = "Products' catalog saved"
        _logger.info(msg)

    def _write_applist(self):
        """
        Write the `applist` files from the catalog.
        """
        _logger.info("Write the applist files from the catalog.")
        app_set_file = {}

        header = \
            "# --------------------------------------------------------------" \
            "----------------\n"\
            "# This applist file generated on {0} for '{1}'.\n"\
            "# This file is automatically generated, and must not be " \
            "manually modified.\n"\
            "# Please modify the configuration file instead (appdownload.ini " \
            "by default).\n"\
            "# -------------------------------------------------------------" \
            "-----------------\n"

        # Clean up the obsolete applist files
        store_path = self._config[_CORE_SNAME][_STORE_KNAME]
        for entry in os.scandir(store_path):
            if entry.name.startswith(_APPLIST_PREFIX) \
                    and entry.name.endswith(_APPLIST_EXT) \
                    and entry.is_file():
                msg = "Deleting obsolete applist file : '{}'."
                _logger.debug(msg.format(entry.name))
                os.unlink(entry.path)
        _logger.info("Applist files cleaned up.")

        # Create the new applist files based on the 'sets' section of the
        # configuration file. All the applist files is going to be created
        # and should be empty.
        for named_set in self._config[_SETS_SNAME]:
            comps = self._config[_SETS_SNAME][named_set]
            for comp_name in comps.split(","):
                comp_name = comp_name.strip()
                if comp_name:
                    filename = _APPLIST_PREFIX + comp_name + _APPLIST_EXT
                    filename = os.path.join(store_path, filename)
                    if comp_name not in app_set_file:
                        file = open(filename, "w+t")
                        app_set_file[comp_name] = file
                        msg = "'{0}' applist file created -> '{1}'."
                        _logger.debug(msg.format(comp_name, filename))
                        dt = (datetime.datetime.now()).replace(microsecond=0)
                        file.write(header.format(dt.isoformat(), comp_name))
                    else:
                        msg = "'{}' applist file already exist."
                        _logger.debug(msg.format(comp_name))
                else:
                    msg = "Set '{}' contains no names or an empty one."
                    _logger.warning(msg.format(named_set))

        for app_id in self._config[_APPS_SNAME]:
            if self._config[_APPS_SNAME].getboolean(app_id):
                if app_id in self._catalog[CAT_PRODUCTS_KNAME]:
                    app_entry = self._catalog[CAT_PRODUCTS_KNAME][app_id]
                    if len(app_entry[CAT_APPROVED_KNAME]) != 0:
                        app = app_entry[CAT_APPROVED_KNAME]
                        # build the catalog line
                        app_line = \
                            app[_PROD_TARGET_KNAME] + _APPLIST_SEP + \
                            app[_PROD_NAME_KNAME] + _APPLIST_SEP + \
                            app[_PROD_VERSION_KNAME] + _APPLIST_SEP + \
                            app[_PROD_INSTALLER_KNAME] + _APPLIST_SEP + \
                            app[_PROD_SILENT_INSTALL_ARGS_KNAME]

                        app_set_name = self._config[app_id][_SET_KNAME]
                        comps = self._config[_SETS_SNAME][app_set_name]
                        for comp_name in comps.split(","):
                            comp_name = comp_name.strip()
                            app_set_file[comp_name].write(app_line + "\n")
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
    Load the configuration from a configuration file. (see `config.parser`)

    The configuration is stored in a dictionary with the same structure as the
    configuration file.

    Args:
        filename (str): The full path name of the configuration file.

    Returns:
        dict: Contains the configuration.
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


def main():
    """
    Entry point

    Returns:

    """
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


if __name__ == "__main__":
    sys.exit(main())