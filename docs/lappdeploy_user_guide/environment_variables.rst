.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lappdeploy-userguide_envvars:

*********************
Environment Variables
*********************
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

The following topics details environment variables used by lAppDeploy scripts.

.. envvar:: APP_STORE_DIR

    Contain the path for installation package and the :term:`applist` files.

    Since :doc:`lappdeploy` script may be use from removable media (e.g. DVD, USB
    Stick). It is recommended to use a relative path (e.g. :file:`..\appstore`)
    rather than an absolute one.

    Default value: ``..\appstore``

.. envvar:: APPLIST

    Contain the full pathname of the `applist` file.

    Default value: none

.. envvar:: APPLIST_TO_INSTALL

    Contain the full pathname of the :doc:`appfilter` output file. This file
    matches a subset of `applist` syntax by containing only :dfn:`appName`,
    :dfn:`appVersion`, :dfn:`appPackage`, and :dfn:`appArgs` columns.

    Default value: none

.. envvar:: ARCHIVE_LOGFILE

    Contain the full path name of the persistent log file. All messages for the
    current update transaction are write in this file.

    Default value: ``%SystemRoot%\lappdeploy.log``

.. envvar:: FROM_MAIL_ADDR

    Contain the mail address of the mail sender (typically machine mail address)

    Default value: none

.. envvar:: LOGLEVEL

    Specify the maximum level of log entries written in log files (see
    `UPDATE_LOGFILE` and `WARNING_LOGFILE`).

    The value is one of:

    =============  =============================================================
    ``ERROR``      only the Error entries are logged
    ``WARNING``    only the Error or Warning entries are logged
    ``INFO``       only the Error, Warning or Informational entries are logged
    ``DEBUG``      all entries are logged
    =============  =============================================================

    Default value: ``INFO``

.. envvar:: LOGMAIL

    Specify if a mail containing the current lappdeploy log messages will be
    sent (see :doc:`log2mail` script).

    The value is one of:

    =======  ===================================================================
    ``0``    No mail is sent
    ``1``    A mail with the content of the log files is sent to `TO_MAIL_ADDR`
    =======  ===================================================================

    Default value: ``0``

.. envvar:: SILENT

    Specify the scripts logging mode.

    The value is one of:

    =======  ===================================================================
    ``0``    Messages are written in a log file and on the standard output
    ``1``    Messages are only written in the log file specified by
             `ARCHIVE_LOGFILE`
    =======  ===================================================================

    Default value: ``1``

.. envvar:: SMTP_SERVER

    Contain the fully qualified name of the SMTP server to use

    Default value: none

.. envvar:: SMTP_SERVER_PORT

    Contain the SMTP server’s port number to use

    Default value: ``25``

.. envvar:: SUMMARY_LOGFILE

    Contain the full path name of the current summary log file. All summary
    messages for the current update transaction are write in this file.

    Default value: ``%TEMP%\appdeploy_summary_today.log``

.. envvar:: TO_MAIL_ADDR

    Contain the mail address of the mail recipient (typically a system administrator)

    Default value: none

.. envvar:: UPDATE_LOGFILE

    Contain the full path name of the current log file. All log entries for the current update transaction are write in this file.

    Default value: ``%TEMP%\appdeploy_today.log``

.. envvar:: WARNING_LOGFILE

    Contain the full path name of the current warning log file. All warning messages for the current update transaction are write in this file.

    Default value: ``%TEMP%\appdeploy_warn_today.log``