.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _applist:

Applist Format
==============
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

applist file describes a list of application packages which will be deployed on
a workstation or a server.

These files are `text file`_ complying with the `Windows standard`_. Since these
files are used by scripts written in `Command shell`_ or `Windows Script Host`_,
so it must use `ASCII printable characters`_ (i.e. no national or accented
characters).

This list matches the following format::

    appArch; appName; appVersion; appPackage; appArgs

Blank lines and comments introduced by a '#' sign are ignored.

===============  ===============================================================
``appArch``      is the target architecture type (the Windows’ one) for the
                 application. This argument may be empty or contain one of the
                 following values: ``x86`` or ``x64``.

                 * ``x86``: the application works only on 32 bits architecture

                 * ``x64``: the application works only on 64 bits architecture

                 * ``""``: the application or the installation program work on
                   both architectures
``appName``      is the name of the application as it appears in the
                 Program Control Panel.
``appVersion``   is the version number of the application as it appears in the
                 Program Control Panel.
``appPackage``   is the path name (full or relative) of executable file, command
                 or MSI package, without argument, to launch for installing or
                 upgrading the application. The ``appPackage`` may be prefixed
                 with the :envvar:`APP_STORE_DIR` environment variable
                 (e.g. ``%APP_STORE_DIR%\dummy.exe``)

``appArgs``      are arguments to use when launching ``appPackage``
===============  ===============================================================

example
-------

.. literalinclude:: applist.example.txt
   :language: text
   :name: applist.example.txt


.. _text file: http://en.wikipedia.org/wiki/Text_file
.. _Windows standard: http://en.wikipedia.org/wiki/Text_file
   #Standard_Windows_.txt_files
.. _Command shell: https://technet.microsoft.com/en-us/library/cc754340.aspx
   #BKMK_OVR]]
.. _Windows Script Host: https://msdn.microsoft.com/library/d1wf56tt.aspx
.. _ASCII printable characters: http://en.wikipedia.org/wiki/ASCII
   #ASCII_printable_characters