.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lappdeploy-userguide_init-usage:

__init__
========
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>


Synopsis
--------

``__init__``

Description
-----------
This optional script is a `hook script` called when :doc:`lappdeploy` script start.
See `about_usage-syntax` for details about used syntax.

When ``__init__`` is called no initialisation task have been launched and no
`environment variables <lappdeploy-userguide_envvars>` are set. Thus this hook is
designed to host yours additional initialisation tasks (e.g. tuning
environment variables)


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