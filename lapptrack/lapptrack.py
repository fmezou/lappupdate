"""
This module is in charge of plug-in handling and operations scheduling.
It may use as a module by a third party offering a new GUI for
example, or as a script with the command line interface::

    python -m lapptrack

The `user manual`_ details use cases and the configuration files.


Synopsis
--------

``lapptrack.py [-h] [-p | -f | -a [-y]| -m | -t] [-v] [-c FILE]``


Description
-----------
Pull update information from the editor information channel (web, rss..), fetch
the update, store it on the local server and generate an applist file for
deploying the application with the :command:`lappdeploy` script. A plug-in
handles information sources to determine if an update has been published, and to
fetch it.

All information about a handled :term:`product` are stored in a :term:`catalog`
file (see `background_catalog-format` section for a detailed description)


Command line options
^^^^^^^^^^^^^^^^^^^^

.. program:: lapptrack

.. option:: -h, --help

    show this help message and exit

.. option:: -p, --pull

    pull the availability of updates

.. option:: -f, --fetch

    fetch applications updates based on the last build catalog (useful to
    recover a crashed application storage)

.. option:: -a, --approve

    approve the deployment of applications

.. option:: -m, --make

    make applist files based on the last build catalog (useful to make applist
    files after a configuration modification)

.. option:: -t, --testconf

    check the configuration file for internal correctness

.. option:: -y, --yes

    force applications approval (see :option:`--approve`). With this flag,
    applications are approved without any interaction else each application
    will has to be approved in interactive mode on the console

.. option:: -c, --configfile FILE

    specifies the configuration file. It includes the list of handled
    applications, the `lapptrack.example.ini` details configuration topics. The
    default configuration file name is :file:`lapptrack.ini` located in the
    current working directory

.. option:: -v, --version

    show program's version number and exit


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
`LAppTrack`                          ..
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
import logging
import logging.config
import json
import sys
import smtplib
import locale

import colorama

from support import report
from cots import core


__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "LAppTrack",
    "main",
    "notify_start",
    "notify_end",
    "notify_info",
    "notify_error",
    "notify_warning",
    "CATALOG_FNAME",
    "CAT_WARNING_KNAME",
    "CAT_VERSION_KNAME",
    "CAT_VERSION",
    "CAT_MODIFIED_KNAME",
    "CAT_PRODUCTS_KNAME",
    "CAT_PULLED_KNAME",
    "CAT_FETCHED_KNAME",
    "CAT_APPROVED_KNAME",
    "Error",
    "ConfigurationError"
]

# Script display name: use in logger and the console UI
_DISPLAY_NAME = "lapptrack ({})".format(__version__)

# Sections and keys names used in the configuration file (see lapptrack.ini)
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
    "applist files used by lappdeploy script."

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
_PROD_DNAME_KNAME = "display_name"
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
# docs.python.org/3/howto/logging.html# configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Error(Exception):
    """
    Base class for LAppTrack exceptions.

    Args:
        message (str): (optional) Human readable string describing the
            exception.

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
        solution (str): (optional) Human readable string providing a
            recommendation to solve the error.

    Attributes:
        filename (str): The path name (full or partial) of the configuration
            file.
        message (str): Human readable string describing the exception.
        solution (str): (optional) Human readable string providing a
            recommendation to solve the error.
    """
    def __init__(self, filename, message, solution=""):
        msg = "Configuration error in '{}': {} {}"
        Error.__init__(self, msg.format(filename, message, solution))
        self.filename = filename
        self.message = message
        self.solution = solution


class LAppTrack:
    """
    Schedule products updates retrieving operations.

    **Attributes**
        This class has a number of public attributes listed below in
        alphabetical order.

        .. hlist::
            * :attr:`catalog`
            * :attr:`catalog_path`
            * :attr:`config`
            * :attr:`config_checked`

    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `approve`                            `pull`
        `fetch`                              `run`
        `load_config`                        `test_config`
        `make`                               ..
        ===================================  ===================================


    **Using LAppTrack...**
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

    **Inside LAppTrack...**
        This class manages the properties of a `COST` and use a `catalog` (the
        section `background_catalog-format` details the catalog file structure)
        to permanently store theses properties. The figure below is the
        activity diagram of the life cycle of a particular version of a COST.

        .. digraph:: tracking
            :caption: life cycle of a particular version of a COST
            :align: center

            node [fontsize="10", fontname="Bell MT", margin="0.038,0.019",
            height="0.13"];
            edge [fontsize="10", fontname="Bell MT"];

            start [
                shape="rectangle",
                style="rounded"
            ];
            end [
                shape="rectangle",
                style="rounded"
            ];
            pull_opt [
                label="--pull",
                shape="parallelogram",
                fontname="Consolas",
                fontsize="8"
            ];
            fetch_opt [
                label="--fetch",
                shape="parallelogram",
                fontname="Consolas",
                fontsize="8"
            ];
            approve_opt [
                label="--approve",
                shape="parallelogram",
                fontname="Consolas",
                fontsize="8"
            ];
            { rank = "same"; pull_opt; fetch_opt; approve_opt; }
            get_origin [
                label="Get latest\\nversion information",
                shape="rectangle"
            ];
            is_update [label="latest\\n!=\\napproved", shape="diamond"];
            store_pulled [
                label="Store latest\\nin 'pulled' attribute",
                shape="rectangle"
            ];
            fetch [
                label="Get version installer\\nfrom 'pulled' attribute",
                shape="rectange"
            ];
            store_fetched [
                label="Move object\\nfrom 'pulled'\\nto 'fetched' attribute",
                shape="rectangle"
            ];
            store_approved [
                label="Move object\\nfrom 'fetched'\\nto 'approved' attribute",
                shape="rectange"
            ];

            start -> pull_opt;
            pull_opt -> get_origin;
            get_origin -> is_update:n;
            is_update:w -> pull_opt:w [label="False"];
            is_update:s -> store_pulled [label="True"];
            store_pulled:e -> fetch_opt:w;
            fetch_opt -> fetch;
            fetch -> store_fetched;
            store_fetched:e -> approve_opt:w;
            approve_opt -> store_approved;
            store_approved -> end;
    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        # initialise the configuration based on ConfigParser module.
        #: configparser.ConfigParser: The configuration of the module, the
        #: `lapptrack-userguide_lapptrack-ini-content` section details each
        #: configuration parameters
        self.config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())
        #: bool: `True` if the configuration file have been loaded and contains no
        #: error
        self.config_checked = False

        #: str: The path name of the *store* directory (see
        #: `lapptrack-userguide_lapptrack-ini-core-section`)
        self.store_path = ""
        #: str: The path name of the product :term:`catalog`, it is a
        #: concatenation of the *store* path name (see
        #: `lapptrack-userguide_lapptrack-ini-core-section`) and the
        #: `CATALOG_FNAME` constant
        self.catalog_path = ""
        #: dict: The current product :term:`catalog`, the
        #: `background_catalog-format` section details the catalog file
        #: structure
        self.catalog = {}

        self._pulling_report = report.Report()
        self._fetching_report = report.Report()
        self._approving_report = report.Report()
        self._report = ""

        msg = "<<< ()=None"
        _logger.debug(msg)

    def run(self):
        """
        Run the LAppTrack application.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        notify_start("run")
        result = self._read_catalog()
        if result:
            # Fetch error are ignored to allow a complete cycle. All errors
            # are logged and notified to the user.
            self._pull_update()
            self._fetch_update()
            self._approve_update(True)
            result = self._write_catalog()
            if result:
                result = self._write_applist()
        notify_end("run", result)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def pull(self):
        """
        Pull the availability of updates.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        notify_start("pull")
        result = self._read_catalog()
        if result:
            # Fetch errors are ignored to allow a complete cycle. In case of
            # error the underlying functions guarantee a consistency catalog.
            # All errors are logged and notified to the user.
            r = self._pull_update()
            if not r:
                result = False
            r = self._write_catalog()
            if not r:
                result = False
        notify_end("pull", result)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def fetch(self):
        """
        Fetch application updates based on the last build catalog.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        notify_start("fetch")
        result = self._read_catalog()
        if result:
            # Fetch error are ignored to allow a complete cycle. All errors
            # are logged and notified to the user.
            r = self._fetch_update()
            if not r:
                result = False
            r = self._write_catalog()
            if not r:
                result = False
        notify_end("fetch", result)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def approve(self, force=False):
        """
        Approve the deployment of applications.

        Args:
            force (optional[bool]): `False` to indicates if the user must approved
                each deployment in a interactive session. `True` to indicates that
                updates are all approved without prompt.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        notify_start("approve force={}".format(force))
        result = self._read_catalog()
        if result:
            self._approve_update(force)
            result = self._write_catalog()
        notify_end("approve force={}".format(force), result)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def make(self):
        """
        Make `applist` files based on the last build catalog

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        notify_start("make")
        result = self._read_catalog()
        if result:
            result = self._write_applist()
        notify_end("make", result)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def test_config(self, config_file):
        """
        Check the configuration file for internal correctness.

        Args:
            config_file (file object): The `file object` of the configuration
                file opened for reading in text mode (see `open` for details
                about opening mode).

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        # The logging configuration may be not valid, events are only print on
        # the console with print(). Furthermore, the use case of this method is
        # typically in interactive mode.
        msg = "Starting task: testconf configfile={}".format(config_file.name)
        print(msg)
        result = self.load_config(config_file)
        if result:
            msg = "Task successfully completed : testconf configfile={}". \
                format(config_file.name)
        else:
            msg = "TASK FAILED : TESTCONF configfile={}". \
                format(config_file.name)
        print(msg)
        return result

    def _pull_update(self):
        """
        Pull the availability of updates.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        assert self.config_checked

        error = True
        apps_num = len(self.config[_APPS_SNAME])
        for i, app_id in enumerate(self.config[_APPS_SNAME]):
            result = True
            if self.config[_APPS_SNAME].getboolean(app_id):
                qn = self.config[app_id][_QUALNAME_KNAME]
                try:
                    app = core.get_handler(qn)
                    origin_app = core.get_handler(qn)
                except ImportError as err:
                    msg = "Erroneous config: {}".format(str(err))
                    notify_error(msg)
                    result = False
                except TypeError as err:
                    msg = "Internal error: {}".format(str(err))
                    notify_error(msg)
                    result = False
                else:
                    msg = "Fetching update information for '{}' (id: {})" \
                          " - {}/{}".format(app.name, app_id, i+1, apps_num)
                    notify_info(msg)

                if result:
                    if app_id in self.catalog[CAT_PRODUCTS_KNAME]:
                        app_entry = self.catalog[CAT_PRODUCTS_KNAME][app_id]
                        # Load deployed product
                        if app_entry[CAT_APPROVED_KNAME]:
                            app.load(app_entry[CAT_APPROVED_KNAME])
                            origin_app.load(app_entry[CAT_APPROVED_KNAME])

                    else:
                        # Do not exist in catalog, a new one will be created
                        self.catalog[CAT_PRODUCTS_KNAME][app_id] = {
                            CAT_PULLED_KNAME: {},
                            CAT_FETCHED_KNAME: {},
                            CAT_APPROVED_KNAME: {}
                        }
                        app_entry = self.catalog[CAT_PRODUCTS_KNAME][app_id]

                    try:
                        result = origin_app.get_origin()
                        if not result:
                            msg = "Fetch update information for '{}' " \
                                  "failed".format(app.name)
                            notify_error(msg)
                            result = False
                    except Exception as err:
                        msg = "Internal error: {}".format(str(err))
                        notify_error(msg)
                        result = False

                    if result:
                        if origin_app.is_update(app):
                            app_entry[CAT_PULLED_KNAME] = origin_app.dump()
                            msg = "A new version of '{}' exist ({}) published" \
                                  " on {}.".format(origin_app.name,
                                                   origin_app.version,
                                                   origin_app.published)
                            notify_info(msg)
                            self._pulling_report.add_section(origin_app.dump())
                        else:
                            msg = "No newer version of '{0}' " \
                                  "exist.".format(app.name)
                            notify_info(msg)
                del app
                del origin_app
            else:
                msg = "Tracking deactivated (id: {}) " \
                      "- {}/{}".format(app_id, i+1, apps_num)
                notify_info(msg)
            # Store the error to raise it without interrupt the loop
            if not result:
                error = False

        try:
            self._pulling_report.publish()
        except (smtplib.SMTPException, OSError) as err:
            # The failure to send the report is simply notified, but it
            # is not a critical error.
            msg = "Failed to send or write the report: {}".format(str(err))
            notify_error(msg)

        msg = "<<< ()={}"
        _logger.debug(msg.format(error))
        return error

    def _fetch_update(self):
        """
        Fetch applications updates based on the last build catalog.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        assert self.config_checked is True
        error = True
        apps_num = len(self.config[_APPS_SNAME])
        for i, app_id in enumerate(self.config[_APPS_SNAME]):
            result = True
            if self.config[_APPS_SNAME].getboolean(app_id):
                qn = self.config[app_id][_QUALNAME_KNAME]
                try:
                    app = core.get_handler(qn)
                except ImportError as err:
                    msg = "Erroneous config: {}".format(str(err))
                    notify_error(msg)
                    result = False
                except TypeError as err:
                    msg = "Internal error: {}".format(str(err))
                    notify_error(msg)
                    result = False
                else:
                    msg = "Fetching installer for '{}' (id: {})" \
                          " - {}/{}".format(app.name, app_id, i+1, apps_num)
                    notify_info(msg)

                if result:
                    if app_id in self.catalog[CAT_PRODUCTS_KNAME]:
                        app_entry = self.catalog[CAT_PRODUCTS_KNAME][app_id]
                        if app_entry[CAT_PULLED_KNAME]:
                            app.load(app_entry[CAT_PULLED_KNAME])
                            try:
                                path = self.config[app_id][_PATH_KNAME]
                                path = os.path.normpath(path)
                                result = app.fetch(path)
                                if not result:
                                    msg = "Fetch installer for '{}' " \
                                          "failed".format(app.name)
                                    notify_error(msg)
                                    result = False
                            except Exception as err:
                                msg = "Internal error: {}".format(str(err))
                                notify_error(msg)
                                result = False

                            if result:
                                # replace the fetched product by the newest.
                                app_entry[CAT_FETCHED_KNAME] = app.dump()
                                app_entry[CAT_PULLED_KNAME] = {}
                                msg = "Installer of '{0}' fetched. saved as" \
                                      " '{1}'.".format(app.name, app.installer)
                                notify_info(msg)
                                self._fetching_report.add_section(app.dump())
                    else:
                        # The product do not exist in the catalog. It's a
                        # product newly added and the update information have
                        # not been fetched.
                        msg = "'{}' Not found in the catalog".format(app.name)
                        notify_warning(msg)
                    del app
            else:
                msg = "Tracking deactivated (id: {}) " \
                      "- {}/{}".format(app_id, i+1, apps_num)
                notify_info(msg)
            # Store the error to raise it without interrupt the loop
            if not result:
                error = False

        try:
            self._fetching_report.publish()
        except (smtplib.SMTPException, OSError) as err:
            # The failure to send the report is simply notified, but it
            # is not a critical error.
            msg = "Failed to send or write the report: {}".format(str(err))
            notify_error(msg)

        msg = "<<< ()={}"
        _logger.debug(msg.format(error))
        return error

    def _approve_update(self, force):
        """
        Approve the deployment of applications.

        Args:
            force (bool): (optional): `False` to indicates if the user must
                approved each deployment in a interactive session. `True` to
                indicates that updates are all approved without prompt.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> (force={})"
        _logger.debug(msg.format(force))
        # check parameters type
        if not isinstance(force, bool):
            msg = "force argument must be a class 'bool'. " \
                  "not {0}"
            msg = msg.format(force.__class__)
            raise TypeError(msg)

        assert self.config_checked is True
        # The expected response to the approval
        expected_resp = {
            "Y": True,
            "": False,
            "N": False,
        }

        apps_num = len(self.config[_APPS_SNAME])
        for i, app_id in enumerate(self.config[_APPS_SNAME]):
            if self.config[_APPS_SNAME].getboolean(app_id):
                if app_id in self.catalog[CAT_PRODUCTS_KNAME]:
                    app_entry = self.catalog[CAT_PRODUCTS_KNAME][app_id]
                    if app_entry[CAT_FETCHED_KNAME]:
                        app = app_entry[CAT_FETCHED_KNAME]
                        msg = "Approving the deployment of '{}' (id: {})" \
                              " - {}/{}".format(app[_PROD_NAME_KNAME], app_id,
                                                i+1, apps_num)
                        notify_info(msg)
                        approved = False
                        if not force:
                            prompt = "Approve {} ({}) (y/n) [n]:".format(
                                app[_PROD_NAME_KNAME], app[_PROD_VERSION_KNAME]
                            )
                            while True:
                                resp = input(prompt)
                                if resp.upper() in expected_resp:
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
                            msg = "Deployment of '{0}' " \
                                  "approved.".format(app[_PROD_NAME_KNAME])
                            notify_info(msg)
                        else:
                            # The disapproval is simply log (it is an user
                            # action)
                            msg = "Deployment of '{0}' " \
                                  "disapproved.".format(app[_PROD_NAME_KNAME])
                            notify_info(msg)
                    else:
                        msg = "No fetched version exist (id: {}) " \
                              " - {}/{}".format(app_id, i+1, apps_num)
                        notify_warning(msg)
                else:
                    # The product do not exist in the catalog. It's a
                    # product newly added and the update information have
                    # not been fetched.
                    msg = "Not found in the catalog (id: {}) " \
                          "- {}/{}".format(app_id, i+1, apps_num)
                    notify_warning(msg)
            else:
                msg = "Tracking deactivated (id: {}) " \
                      "- {}/{}".format(app_id, i+1, apps_num)
                notify_info(msg)

        try:
            self._approving_report.publish()
        except (smtplib.SMTPException, OSError) as err:
            # The failure to send the report is simply notified, but it
            # is not a critical error.
            msg = "Failed to send or write the report: {}".format(str(err))
            notify_error(msg)

        msg = "<<< ()=None"
        _logger.debug(msg)

    def load_config(self, config_file):
        """
        Load the configuration details from the configuration file.

        Args:
            config_file (file object): The `file object` of the configuration
                file opened for reading in text mode (see `open` for details
                about opening mode).

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        # check parameters type
        if not isinstance(config_file, io.TextIOBase):
            msg = "config_file argument must be a class 'io.TextIOBase'. " \
                  "not {0}"
            msg = msg.format(config_file.__class__)
            raise TypeError(msg)

        result = True
        # Load the configuration, and set the logging configuration from it.
        # I'am still using the fileConfig() method instead of dictConfig() to
        # keep the configuration in a ini file, which is easy to write and to
        # read for a human.
        try:
            self.config.read_file(config_file)
        except configparser.Error as err:
            msg = "Failed to parse the logger configuration" \
                  " file: {}".format(str(err))
            notify_error(msg)
            result = False

        if result:
            # Check the core section
            if _CORE_SNAME in self.config.sections():
                section = self.config[_CORE_SNAME]
                # 'store' key is mandatory
                if _STORE_KNAME in section:
                    # Set the catalog pathname.
                    path = self.config[_CORE_SNAME][_STORE_KNAME]
                    self.store_path = os.path.normpath(path)
                    try:
                        os.makedirs(self.store_path, exist_ok=True)
                        self.catalog_path = os.path.join(self.store_path,
                                                         CATALOG_FNAME)
                    except OSError as err:
                        msg = "Failed to create the store directory - " \
                              "OS error: {}".format(str(err))
                        notify_error(msg)
                        result = False
                else:
                    msg = "Missing mandatory key in {} section: " \
                          "'{}'".format(_STORE_KNAME, _CORE_SNAME)
                    notify_error(msg)
                    result = False

                # 'logger' key is optional
                if _LOGGER_KNAME in section:
                    filename = self.config[_CORE_SNAME][_LOGGER_KNAME]
                    if os.path.isfile(filename):
                        try:
                            logging.config.fileConfig(
                                filename, disable_existing_loggers=False
                            )
                        except Exception as err:
                            msg = "Failed to parse the logger configuration" \
                                  " file: {}".format(str(err))
                            notify_error(msg)
                            result = False
                    else:
                        msg = "Configuration file specified in '{}' key " \
                              "do not exist (see section " \
                              "'{}')".format(_LOGGER_KNAME, _CORE_SNAME)
                        notify_error(msg)
                        result = False

                # 'pulling_report' key is optional
                if _PULL_REPORT_KNAME in section:
                    filename = self.config[_CORE_SNAME][_PULL_REPORT_KNAME]
                    if os.path.isfile(filename):
                        try:
                            config = _load_config(filename)
                            self._pulling_report.load_config(config, False)
                        except configparser.Error as err:
                            msg = "Failed to parse the pulling report" \
                                  " configuration file: {}".format(str(err))
                            notify_error(msg)
                            result = False
                        except OSError as err:
                            msg = "Failed to read the pulling report" \
                                  " configuration file - OS Error:" \
                                  " {}".format(str(err))
                            notify_error(msg)
                            result = False
                    else:
                        msg = "Configuration file specified in '{}' key " \
                              "do not exist (see section " \
                              "'{}')".format(_PULL_REPORT_KNAME, _CORE_SNAME)
                        notify_error(msg)
                        result = False

                # 'fetching_report' key is optional
                if _FETCH_REPORT_KNAME in section:
                    filename = self.config[_CORE_SNAME][_FETCH_REPORT_KNAME]
                    if os.path.isfile(filename):
                        try:
                            config = _load_config(filename)
                            self._fetching_report.load_config(config, False)
                        except configparser.Error as err:
                            msg = "Failed to parse the fetching report" \
                                  " configuration file: {}".format(str(err))
                            notify_error(msg)
                            result = False
                        except OSError as err:
                            msg = "Failed to read the fetching report" \
                                  " configuration file - OS Error:" \
                                  " {}".format(str(err))
                            notify_error(msg)
                            result = False
                    else:
                        msg = "Configuration file specified in '{}' key " \
                              "do not exist (see section " \
                              "'{}')".format(_FETCH_REPORT_KNAME, _CORE_SNAME)
                        notify_error(msg)
                        result = False

                # 'approving_report' key is optional
                if _APPROVE_REPORT_KNAME in section:
                    filename = self.config[_CORE_SNAME][_APPROVE_REPORT_KNAME]
                    if os.path.isfile(filename):
                        try:
                            config = _load_config(filename)
                            self._approving_report.load_config(config, False)
                        except configparser.Error as err:
                            msg = "Failed to parse the approving report" \
                                  " configuration file: {}".format(str(err))
                            notify_error(msg)
                            result = False
                        except OSError as err:
                            msg = "Failed to read the approving report" \
                                  " configuration file - OS Error:" \
                                  " {}".format(str(err))
                            notify_error(msg)
                            result = False
                    else:
                        msg = "Configuration file specified in '{}' key " \
                              "do not exist (see section " \
                              "'{}')".format(_APPROVE_REPORT_KNAME, _CORE_SNAME)
                        notify_error(msg)
                        result = False
            else:
                msg = "the section '{}' is missing.".format(_CORE_SNAME)
                notify_error(msg)
                result = False

            # Check the sets section
            if _SETS_SNAME in self.config.sections():
                sets = self.config[_SETS_SNAME]
            else:
                sets = {}
                msg = "the section '{}' is missing.".format(_SETS_SNAME)
                notify_error(msg)
                result = False

            # Check the applications section
            if _APPS_SNAME in self.config.sections():
                for app_name in self.config[_APPS_SNAME]:
                    # FIXME (fmezou) catch exception (use case mock = any vs mock = on)
                    # extend to all excepted value in config file.
                    if self.config[_APPS_SNAME].getboolean(app_name):
                        # Pre compute default value for the Application section
                        app_qualname = "{}.{}.{}Handler".format(
                            _PACKAGE_NAME, app_name, app_name.capitalize()
                        )
                        app_path = os.path.join(self.store_path, app_name)
                        app_set = "__all__"

                        # Checks the item in the application section
                        # If a section or a key is missing, it is added in the
                        # config object, so this object will contain a complete
                        # configuration
                        if app_name in self.config.sections():
                            app_desc = self.config[app_name]
                            if _QUALNAME_KNAME not in app_desc:
                                app_desc[_QUALNAME_KNAME] = app_qualname
                            if _PATH_KNAME not in app_desc:
                                app_desc[_PATH_KNAME] = app_path
                            # 'set' key must be declared in the sets section
                            # if it exist.
                            if _SET_KNAME in app_desc:
                                if app_desc[_SET_KNAME] in sets:
                                    pass
                                else:
                                    msg = "'set' value '{}' is not declared " \
                                          "in 'sets' section (see {} "\
                                          "application)"
                                    msg = msg.format(app_desc[_SET_KNAME],
                                                     app_name)
                                    notify_error(msg)
                                    result = False
                            else:
                                app_desc[_SET_KNAME] = app_set
                        else:
                            # Set the default value
                            self.config[app_name] = {}
                            app_desc = self.config[app_name]
                            app_desc[_QUALNAME_KNAME] = app_qualname
                            app_desc[_PATH_KNAME] = app_path
                            app_desc[_SET_KNAME] = app_set
            else:
                msg = "the section '{}' is missing.".format(_APPS_SNAME)
                notify_error(msg)
                result = False

            # Checked
            self.config_checked = result
            if result:
                msg = "Configuration loaded from '{}'".format(config_file.name)
                notify_info(msg)

        config_file.close()
        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _read_catalog(self):
        """
        Load the product's catalog.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        result = True
        try:
            with open(self.catalog_path, "r+t") as file:
                self.catalog = json.load(file)
                # force the version number.
                # at time, there is non need to have a update function
                self.catalog[CAT_VERSION_KNAME] = CAT_VERSION
        except FileNotFoundError:
            # the catalog may be not exist
            notify_warning("The product's catalog don't exist, a new one will"
                           " be created")
            self.catalog = {
                CAT_WARNING_KNAME: _CAT_WARNING,
                CAT_VERSION_KNAME: CAT_VERSION,
                CAT_MODIFIED_KNAME: None,
                CAT_PRODUCTS_KNAME: {}
            }
        except json.JSONDecodeError as err:
            msg = "Failed to parse the catalog: {}".format(str(err))
            notify_error(msg)
            result = False
        except OSError as err:
            msg = "Failed to read the catalog - OS error: {}".format(str(err))
            notify_error(msg)
            result = False
        else:
            msg = "Products' catalog loaded from" \
                  " '{}'".format(self.catalog_path)
            notify_info(msg)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _write_catalog(self):
        """
        Write the catalog products file.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        msg = "Write the products' catalog ({0})."
        _logger.info(msg.format(self.catalog_path))
        result = True
        try:
            with open(self.catalog_path, "w+t") as file:
                # write the warning header with a naive time representation.
                dt = (datetime.datetime.now()).replace(microsecond=0)
                self.catalog[CAT_MODIFIED_KNAME] = dt.isoformat()
                json.dump(self.catalog, file, indent=4, sort_keys=True)
        except OSError as err:
            msg = "Failed to write the catalog - OS error: {}".format(str(err))
            notify_error(msg)
            result = False
        else:
            msg = "Products' catalog saved to " \
                  " '{}'".format(self.catalog_path)
            notify_info(msg)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _write_applist(self):
        """
        Write the `applist` files from the catalog.

        Returns:
            bool: `True` if the execution went well. In case of failure, an error
            log is written.
        """
        msg = ">>> ()"
        _logger.debug(msg)
        _logger.info("Write the applist files from the catalog.")
        result = True
        set_file = {}

        header = \
            "# --------------------------------------------------------------" \
            "----------------\n"\
            "# This applist file generated on {0} for '{1}'.\n"\
            "# This file is automatically generated, and must not be " \
            "manually modified.\n"\
            "# Please modify the configuration file instead (lapptrack.ini " \
            "by default).\n"\
            "# -------------------------------------------------------------" \
            "-----------------\n"

        # Clean up the obsolete applist files
        for entry in os.scandir(self.store_path):
            if entry.name.startswith(_APPLIST_PREFIX) \
                    and entry.name.endswith(_APPLIST_EXT) \
                    and entry.is_file():
                msg = "Deleting obsolete applist file : '{}'."
                _logger.debug(msg.format(entry.name))
                os.unlink(entry.path)
        notify_info("Applist files cleaned up.")

        # Create the new applist files based on the 'sets' section of the
        # configuration file. All the applist files is going to be created
        # and should be empty.
        msg = "Building applist file"
        notify_info(msg)
        for k, v in self.config[_SETS_SNAME].items():
            for name in v.split(","):
                name = name.strip()
                if name:
                    path = _APPLIST_PREFIX + name + _APPLIST_EXT
                    path = os.path.join(self.store_path, path)
                    if name not in set_file:
                        try:
                            file = open(path, "w+t")
                        except OSError as err:
                            msg = "Failed to create the applist file {} - " \
                                  "OS error: {}".format(path, str(err))
                            notify_error(msg)
                            result = False
                        else:
                            set_file[name] = file
                            try:
                                dt = (datetime.datetime.now()).replace(
                                    microsecond=0)
                                file.write(header.format(dt.isoformat(), name))
                            except OSError as err:
                                msg = "Failed to write the applist file {} - " \
                                      "OS error: {}".format(path, str(err))
                                notify_error(msg)
                                result = False
                else:
                    msg = "Set '{}' contains no names or an empty " \
                          "one ('{}')".format(k, v)
                    notify_warning(msg)

        if result:
            apps_num = len(self.config[_APPS_SNAME])
            for i, app_id in enumerate(self.config[_APPS_SNAME]):
                if self.config[_APPS_SNAME].getboolean(app_id):
                    if app_id in self.catalog[CAT_PRODUCTS_KNAME]:
                        app_entry = self.catalog[CAT_PRODUCTS_KNAME][app_id]
                        if app_entry[CAT_APPROVED_KNAME]:
                            app = app_entry[CAT_APPROVED_KNAME]
                            msg = "Adding '{}' (id: {}) - " \
                                  "{}/{}".format(app[_PROD_DNAME_KNAME],
                                                 app_id, i+1, apps_num)
                            notify_info(msg)
                            app_line = \
                                app[_PROD_TARGET_KNAME] + _APPLIST_SEP + \
                                app[_PROD_DNAME_KNAME] + _APPLIST_SEP + \
                                app[_PROD_VERSION_KNAME] + _APPLIST_SEP + \
                                app[_PROD_INSTALLER_KNAME] + _APPLIST_SEP + \
                                app[_PROD_SILENT_INSTALL_ARGS_KNAME]

                            app_set_name = self.config[app_id][_SET_KNAME]
                            comps = self.config[_SETS_SNAME][app_set_name]
                            for name in comps.split(","):
                                name = name.strip()
                                try:
                                    set_file[name].write(app_line + "\n")
                                except OSError as err:
                                    msg = "Failed to write the applist file " \
                                          "{} - OS error: {}".format(name,
                                                                     str(err))
                                    notify_error(msg)
                                    result = False
                    else:
                        # The product do not exist in the catalog. It's a
                        # product newly added and the update information have
                        # not been fetched.
                        msg = "Not found in the catalog (id: {}) " \
                              "- {}/{}".format(app_id, i+1, apps_num)
                        notify_warning(msg)
                else:
                    msg = "Tracking deactivated (id: {}) " \
                          "- {}/{}".format(app_id, i+1, apps_num)
                    notify_info(msg)

        # Terminate by closing the files
        for name, file in set_file.items():
            try:
                file.close()
            except OSError:
                pass

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


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


def notify_start(verb):
    """
    Notify the user of the task starting.

    The notification is displayed line on the console and in the log file. The
    line displayed on the console uses `ANSI escape code
    <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ to control the text face
    or the foreground color.

    Args:
        verb (str): The action verb of the task
    """
    foreground = "\x1b[1m" # set face text (bold)
    reset = "\x1b[0m" # reset text attribute
    msg = "**** Starting task: {} ****".format(verb)
    print(foreground, msg, reset, sep="")
    _logger.info(msg)


def notify_end(verb, result):
    """
    Notify the user of the task completing.

    The notification is displayed line on the console and in the log file. The
    line displayed on the console uses `ANSI escape code
    <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ to control the text face
    or the foreground color.

    Args:
        verb (str): The action verb of the task
        result (bool): `True` if the execution went well.
    """
    if result:
        foreground = "\x1b[1m"  # set face text (bold)
        msg = "**** Task successfully completed : {} ****".format(verb)
    else:
        foreground = "\x1b[1m\x1b[31m"  # set foreground text color (bold red)
        msg = "TASK FAILED : {}".format(verb.upper())
    reset = "\x1b[39m"  # reset text color
    print(foreground, msg, reset, sep="")
    _logger.info(msg)


def notify_info(msg):
    """
    Notify the user of the progress of the task.

    The notification is displayed line on the console and in the log file. The
    line displayed on the console uses `ANSI escape code
    <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ to control the text face
    or the foreground color.

    Args:
        msg (str): The information message
    """
    foreground = "\x1b[37m" # set foreground text color (white)
    reset = "\x1b[39m" # reset text color
    print(foreground, msg, reset, sep="")
    _logger.info(msg)


def notify_error(msg):
    """
    Notify the user of an error.

    The notification is displayed line on the console and in the log file. The
    line displayed on the console uses `ANSI escape code
    <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ to control the text face
    or the foreground color.

    Args:
        msg (str): The error message
    """
    foreground = "\x1b[31m" # set foreground text color (red)
    reset = "\x1b[39m" # reset text color
    print(foreground, "ERROR! - ", msg.upper(), reset, sep="")
    _logger.error(msg)


def notify_warning(msg):
    """
    Notify the user of a warning.

    The notification is displayed line on the console and in the log file. The
    line displayed on the console uses `ANSI escape code
    <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ to control the text face
    or the foreground color.

    Args:
        msg (str): The error message
    """
    foreground = "\x1b[33m" # set foreground text color (yellow)
    reset = "\x1b[39m" # reset text color
    print(foreground, "warning! - ", msg, reset, sep="")
    _logger.warning(msg)


def main():
    """
    Entry point

    This function call the sys.exit with the appropriate exit code (see
    the section *Exit Code* in :mod:`lapptrack`)
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
                         help="check an lapptrack.ini configuration file for "
                              "internal correctness")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="force applications approval (see --approve)")
    parser.add_argument("-c", "--configfile", default="lapptrack.ini",
                        type=argparse.FileType(mode='r'),
                        help="The file specified contains the configuration "
                             "details. Information in this file includes "
                             "application catalog. The file 'lapptrack."
                             "example.ini' details configuration topics. The "
                             "default configuration file name is "
                             "'lapptrack.ini' located in the current working "
                             "directory.")
    parser.add_argument("-v", "--version", action="version",
                        version="%(prog)s version " + __version__)

    # Parse and run.
    result = False
    args = parser.parse_args()  # the arg_parse call sys.exit in case of failure
    tracker = LAppTrack()
    if args.testconf:
        result = tracker.test_config(args.configfile)
    else:
        dt = datetime.datetime.now()
        print("Starting {} on {:%c}".format(_DISPLAY_NAME, dt))
        result = tracker.load_config(args.configfile)
        if result:
            if args.pull:
                result = tracker.pull()
            elif args.fetch:
                result = tracker.fetch()
            elif args.approve:
                result = tracker.approve(args.yes)
            elif args.make:
                result = tracker.make()
            else:
                result = tracker.run()
        dt = datetime.datetime.now()
        print("{} completed on {:%c}".format(_DISPLAY_NAME, dt))

    if not result:
        sys.exit(1)


if __name__ == "__main__":
    colorama.init()
    locale.setlocale(locale.LC_ALL, "")
    main()
