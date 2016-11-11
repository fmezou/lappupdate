.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _logger_ini:

logger.ini
==========
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

This file contains the configuration of the logging facility used by the
`lapptrack` script. It use a structure similar to what’s found in Microsoft
Windows INI files. See the `Configuration file format
<logging-config-fileformat>` section to have details about the file format.

Each python module declares its own logger module, so the logging mechanism may
be finely tuned (see ``[logger_<module name>]`` section below).

Example of logger.ini
---------------------

.. literalinclude:: /lapptrack/logger.example.ini
   :language: ini


