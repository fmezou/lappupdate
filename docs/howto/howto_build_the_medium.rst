.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _howto_build_the_medium:

How to build the medium
=======================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

The `lappdeploy` script is designed to be independent from the type of used 
media. This can be a network share reached from its UNC name (e.g. 
:file:`\\myserver\share`), a DVD or CD, a USB Stick or any removable media. 
Thus the media building is limited to copy files or use your favourite CD/DVD 
burner utility.

The medium must contain the directory with installers (see 
:ref:`howto_build_the_application_list`) according to the
:envvar:`APP_STORE_DIR` environment variable and the following files from the
:file:`lappdeploy` directory:

*   :file:`lappdeploy.cmd`

*   :file:`_appfilter.vbs`

*   :file:`_log2mail.vbs`

*   :file:`__exit__.cmd` (optional)

*   :file:`__init__.cmd` (optional)

Example
-------
The below block show a typical file tree for a media of deployment. ::

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

