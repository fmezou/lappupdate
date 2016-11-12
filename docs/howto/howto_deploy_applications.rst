.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _howto_deploy-apps:

**************************
How to deploy applications
**************************
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

.. sidebar:: Be simple

    If you manage a unique PC connected to Internet, the easiest way is to let
    each application managing its own upgrades (automatically or manual way).

To deploy application, there are two main use cases. The first one is based on a
share network, the second is based on a DVD distribution. These cases have their
own constraints and answer to specific needs. The main advantage to have a
centralised application deploying system is to allow to a system administrator
to have a consistency application park.

The use of a network share implies that the pc is connected to a local network,
with an available file server. This use case is recommended for SOHO application
deploying (less than 10 pc) and allows silent installation of patches or new
applications.

The use of a DVD is attractive for use in a standalone and non connected
environment (e.g. Industrial PC or access control management console).

But, these two use cases comply with the following steps:

#.  :ref:`howto-deploy_tune-your-environment`

#.  :ref:`howto-deploy_build-applist`

#.  :ref:`howto-deploy_build-medium`

#.  Deploy applications from a :ref:`DVD <howto-deploy_deploy-from-dvd>` or
    :ref:`Network share <howto-deploy_deploy-through-network>`

.. _howto-deploy_tune-your-environment:

Tune your environment
=====================
By default, you have nothing to tune. The default values of
`lappdeploy-userguide_envvars` allows a working with the following features:

*   all action, expect debug one, are only logged in a text file named
    :file:`lappdeploy.log` in the :envvar:`SystemRoot` directory (typically
    ":file:`C:\Windows\lappdeploy.log`".

*   the `applist` files (at least ":file:`applist-all.txt`") are stored in the
    :file:`appstore` directory located at the same level that the directory
    containing the :command:`lappdeploy` script.

If these features do not comply with your need, you must consider tuning the
`lappdeploy-userguide_envvars`. The most efficient way to do that is to use
:command:`__init__` and :command:`__exit__` `hook scripts <hook script>`. See
:file:`__init__.cmd.example` and :file:`__exit__.cmd.example` located in the
directory containing the :command:`lappdeploy` script to have examples.

*   To change the location of :dfn:`applist` files and installers packages, you
    must tune the :envvar:`APP_STORE_DIR` environment variable.

*   To change the level of messages logged, you must tune the :envvar:`LOGLEVEL`
    environment variable.

*   To receive an email with a summary and detailed information on action done
    by lAppUpdate, you must tune the :envvar:`LOGMAIL` environment variable,
    and specifies your account mail configuration in :envvar:`SMTP_SERVER`
    (eventually :envvar:`SMTP_SERVER_PORT`), :envvar:`FROM_MAIL_ADDR` and
    :envvar:`TO_MAIL_ADDR` environment variables.

*   To run the script in an interactive mode (i.e. following installation
    actions in real time through the command shell), you must tune the
    :envvar:`SILENT` environment variable.

.. _howto-deploy_build-applist:

Build the application list
==========================
The :command:`lappdeploy` script uses two `applist` files to verify which
applications were installed and if it needs to be updated: the first one is
named :file:`applist-all.txt`; the second is named  :file:`applist-{set}.txt`
where ``{set}`` is the argument passed to :command:`lappdeploy` on the command
line (e.g. :command:`.\lappdeploy dummy`).

.. tip::

    applist files may be empty including :file:`applist-all.txt`.

These files are `text file`_ complying with the `Windows standard`_. So you can
use any text editor (e.g. notepad, notepad++, vim...) to edit them.

The `background_applist-format` topic details the format of these files.

In fact, you can have so much file as you want according to your needs. For
example, you can have an :dfn:`applist` file per computer or a set of computer
(e.g. children, purchasing department...). If you use a domain controller, you
can match :dfn:`applist` files with your Organisational Units (OU).

.. topic:: Applications store

   A way of making is to store installers into the same directory that
   :dfn:`applist` files with a separate folder for each product (Mozilla Firefox
   and its extension may be considered as one product). It clarifies the
   installers organisation and allow to have a :command:`__postinstall__`
   `hook script` for each of them.

By default, the :dfn:`applist` files are stored in the :file:`appstore`
directory located at the same level that the directory containing the
:command:`lappdeploy` script. To change the location of :dfn:`applist` files and
installers packages, you must tune the :envvar:`APP_STORE_DIR` environment
variable.

.. topic:: Example

   .. literalinclude:: /docs/background_papers/applist.example.txt
      :language: text
      :name: applist.example.txt

.. _howto-deploy_build-medium:

Build the medium
================
The :command:`lappdeploy` script is designed to be independent from the type of
used media. This can be a network share reached from its UNC name (e.g.
:file:`\\myserver\share`), a DVD or CD, a USB Stick or any removable media.
Thus the media building is limited to copy files or use your favourite CD/DVD
burner utility.

The medium must contain the directory with installers (see
:ref:`howto-deploy_build-applist`) according to the :envvar:`APP_STORE_DIR`
environment variable and the following files from the :file:`lappdeploy`
directory:

*   :file:`lappdeploy.cmd`

*   :file:`_appfilter.vbs`

*   :file:`_log2mail.vbs`

*   :file:`__exit__.cmd` (optional)

*   :file:`__init__.cmd` (optional)

The below block show a typical file tree for a media of deployment::

    \
    ├───lappdeploy
    │       lappdeploy.cmd
    │       _appfilter.vbs
    │       _log2mail.vbs
    │       __exit__.cmd
    │       __init__.cmd
    │
    └───appstore
        │   applist-all.txt
        │   applist-dummy.txt
        │
        ├───dummy
        │       aninstaller.cmd
        │       aninstaller.msi
        │
        └───extended dummy
                aninstaller.cmd
                __postinstall__.cmd


.. _howto-deploy_deploy-from-dvd:

Deploy from a DVD
=================
The phase of deployment start by calling :command:`lappdeploy` script from a
command shell. The only argument to pass is the set name according to your
organisation choice (see :ref:`howto-deploy_build-applist`)

As any installation of program, you must launch the script with administrator
privilege (right click on the command prompt link, and choose
":menuselection:`run as administrator`") .

.. topic:: Example

   ``C:\>d:\lappdeploy\lappdeploy.cmd dummy``


.. _howto-deploy_deploy-through-network:

Deploy through a network
========================
The phase of deployment start by calling :command:`lappdeploy` script from a
command shell. The only argument to pass is the set name according to your
organisation choice (see :ref:`howto-deploy_build-applist`)

As any installation of program, you must launch the script with administrator
privilege (right click on the command prompt link, and choose
":menuselection:`run as administrator`") .

To push system integration further, you can call this script from a schedule
task with the sending of an summary mail (see
`howto-deploy_tune-your-environment`).

.. topic:: Example

    ``C:>\\myserver\share\lappdeploy.cmd dummy``

