.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lappdeploy-userguide_log2mail-usage:

_log2mail
=========
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

Synopsis
--------

``_log2mail.vbs``

Description
-----------
This script is a `non-public script <Non-public script>`. It sends a mail
containing the current `lappdeploy` log messages.
See `about_usage-syntax` for details about used syntax.

This script is a `Windows Script`_ one. Thus, it must be used launch with
`cscript`_  command. (e.g. :command:`cscript.exe _log2mail.vbs`)

This script use `Microsoft Collaboration Data Objects for Windows 2000`_  and is
inspired from the `VBScript To Send Email Using CDO`_ from `Paul Sadowski
<http://www.paulsadowski.com/>`_.

Command line options
^^^^^^^^^^^^^^^^^^^^

none

Exit code
^^^^^^^^^

==  ============================================================================
0   no error
1   the summary log doesn’t exist
2   the server name is empty or not defined (fix :envvar:`SMTP_SERVER`
    environment variable)
3   the recipient mail address is empty or not defined (fix
    :envvar:`TO_MAIL_ADDR` environment variable)
==  ============================================================================

Environment variables
^^^^^^^^^^^^^^^^^^^^^^
The following environment variables affect the execution:

===========================  ===========================
:envvar:`TO_MAIL_ADDR`       :envvar:`WARNING_LOGFILE`
:envvar:`FROM_MAIL_ADDR`     :envvar:`SUMMARY_LOGFILE`
:envvar:`SMTP_SERVER`        :envvar:`UPDATE_LOGFILE`
:envvar:`SMTP_SERVER_PORT`
===========================  ===========================

.. _Microsoft Collaboration Data Objects for Windows 2000: https://msdn.
   microsoft.com/en-us/library/ms527568%28v=exchg.10%29.aspx
.. _VBScript To Send Email Using CDO: http://www.paulsadowski.com/wsh/cdo.htm
