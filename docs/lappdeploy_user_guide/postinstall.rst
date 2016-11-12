.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lappdeploy-userguide_postinstall-usage:

__postinstall__
===============
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>


Synopsis
--------

``__postinstall__``

Description
-----------
This optional script is a `hook script` called when `lappdeploy` script ended an
installation. See `about_usage-syntax` for details about used syntax.

When ``__postinstall__`` is called the installation package execution ended.
Thus this hook is designed to host yours additional post installation tasks
like customize the start menu or install additional packs (e.g. Firefox
extensions, VirtualBox Extension Pack, Tortoise Language Pack...).

If this script exist, it must stored in the same directory that the installer,
so it exists one hook for each installer.

Command line options
^^^^^^^^^^^^^^^^^^^^

None

Exit code
^^^^^^^^^

==  ============================================================================
0   no error
==  ============================================================================

Environment variables
^^^^^^^^^^^^^^^^^^^^^

None