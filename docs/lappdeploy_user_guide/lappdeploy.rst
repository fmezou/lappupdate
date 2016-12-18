.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lappdeploy-userguide_lappdeploy-usage:

lappdeploy
==========
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

Synopsis
--------

``lappdeploy [set]``

Description
-----------
This script is a `public script <Public script>`. It launches the installer
package of the standard application.  See `about_usage-syntax`
for details about used syntax.

Command line options
^^^^^^^^^^^^^^^^^^^^

.. option:: set

    is the set name, the script use a file named :file:`applist-{set}.txt` which
    matching `applist file format <applist>`. ``all`` is the default value.

Exit code
^^^^^^^^^

==  ============================================================================
0   no error
1   an error occurred while filtering application
2   invalid argument. An argument of the command line isn't valid (see Usage).
==  ============================================================================

Environment variables
^^^^^^^^^^^^^^^^^^^^^

The following environment variables affect the execution:

===========================  ===========================
:envvar:`APP_STORE_DIR`      :envvar:`WARNING_LOGFILE`
:envvar:`TO_MAIL_ADDR`       :envvar:`SUMMARY_LOGFILE`
:envvar:`FROM_MAIL_ADDR`     :envvar:`ARCHIVE_LOGFILE`
:envvar:`SMTP_SERVER`        :envvar:`SILENT`
:envvar:`SMTP_SERVER_PORT`   :envvar:`LOGMAIL`
:envvar:`UPDATE_LOGFILE`     :envvar:`LOGLEVEL`
===========================  ===========================
