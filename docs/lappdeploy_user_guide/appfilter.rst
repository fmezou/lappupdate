.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lappdeploy-userguide_appfilter-usage:

_appfilter
==========
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

Synopsis
--------

``_appfilter.vbs [{x86|x64}]``

Description
-----------
This script is a `non-public script <Non-public script>`. It filters an
`applist` file by verifying which applications were installed and if it needed
to be updated. See `about_usage-syntax` for details about used syntax.

This script is a `Windows Script`_ one. Thus, it must be launched with
`cscript`_ command. (e.g. :command:`cscript.exe _appfilter.vbs x64`)

Command line options
^^^^^^^^^^^^^^^^^^^^

.. option:: x86

    specifies that the target architecture is a 32 bits one, therefore only 32
    bits installation packages taken into account. This is the default value.

.. option:: x64

    specifies that the target architecture is a 64 bits one, therefore only 64
    bits installation packages taken into account.

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

=============================  =============================
:envvar:`APPLIST`              :envvar:`WARNING_LOGFILE`
:envvar:`APPLIST_TO_INSTALL`   :envvar:`SUMMARY_LOGFILE`
=============================  =============================

