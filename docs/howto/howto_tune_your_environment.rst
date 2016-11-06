.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _howto_tune_your_environment:

How to tune your environment
============================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

By default, you have nothing to tune. The default values of 
`environment_variables` allows a working with the following features:

*   all action, expect debug one, are only logged in a text file named
    :file:`lappdeploy.log` in the :envvar:`%SystemRoot%` directory (typically
    ":file:`C:\Windows\lappdeploy.log`".

*   the `applist` files (at least ":file:`applist-all.txt`") are stored in the
    :file:`appstore` directory located at the same level that the directory
    containing the `lappdeploy` script.

If these features do not comply with your need, you must consider tuning the 
`environment_variables`. The most efficient way to do that is to use `__init__` 
and `__exit__` hook scripts. See :file:`__init__.cmd.example` and 
:file:`__exit__.cmd.example` located in the directory containing the 
`lappdeploy` script to have examples.

*   To change the location of `applist` files and installers packages, you must
    tune the :envvar:`APP_STORE_DIR` environment variable.

*   To change the level of messages logged, you must tune the :envvar:`LOGLEVEL`
    environment variable.

*   To receive an email with a summary and detailed informations on actions done
    by lAppUpdate, you must tune the :envvar:`LOGMAIL` environment variable,
    and specifies your account mail configuration in :envvar:`SMTP_SERVER`
    (eventually :envvar:`SMTP_SERVER_PORT`), :envvar:`FROM_MAIL_ADDR` and
    :envvar:`TO_MAIL_ADDR` environment variables.

*   To run the script in an interactive mode (i.e. following installation
    actions in real time through the command shell), you must tune the
    :envvar:`SILENT` environment variable.
