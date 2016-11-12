.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lappdeploy-userguide_exit-usage:

__exit__
========
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>


Synopsis
--------

``__exit__``

Description
-----------
This optional script is a `hook script` called when `lappdeploy` script end.
See `about_usage-syntax` for details about used syntax.

When ``__exit__`` is called completion tasks have been launched. It is the
reverse script of `init` hook script. Thus this hook is designed to host
yours additional completion tasks.

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