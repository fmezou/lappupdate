.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _init:

__init__
========
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>


Synopsis
--------

``__init__``

Description
-----------
This optional script is a `hook script` called when `lappdeploy` script start.
See `Usage description syntax` for details about used syntax.

When ``__init__`` is called no initialisation task have been launched and no
`environment variables <Environment Variables>` are set. Thus this hook is
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