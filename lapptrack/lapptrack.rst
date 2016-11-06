.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any


:mod:`lapptrack` -- Products Tracking Manager
=============================================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>
.. codeauthor:: Frédéric MEZOU <frederic.mezou@free.fr>
.. automodule:: lapptrack
    :platform: all
    :synopsis: Products Tracking Manager

Objects reference
-----------------
This section details the objects defined in this module. In this case, there is
only one object which is the main entry point of the scheduler. It offers an API
for implementing user interface.

.. autoclass:: lAppTrack
    :members:
    :show-inheritance:

Data reference
--------------
This section details global data, including both variables and values used
as 'defined constants'.

.. autodata:: CATALOG_FNAME
.. autodata:: CAT_WARNING_KNAME
.. autodata:: CAT_VERSION_KNAME
.. autodata:: CAT_VERSION
.. autodata:: CAT_MODIFIED_KNAME
.. autodata:: CAT_PRODUCTS_KNAME
.. autodata:: CAT_PULLED_KNAME
.. autodata:: CAT_FETCHED_KNAME
.. autodata:: CAT_APPROVED_KNAME

Exceptions reference
--------------------
This section details the specific exception used in this module.

.. autoexception:: Error
    :members:
    :show-inheritance:
.. autoexception:: ConfigurationError
    :members:
    :show-inheritance:

Configuration file
------------------

.. literalinclude:: lapptrack.example.ini
   :language: ini
   :caption: Example of configuration file
   :name: lapptrack.example.ini

.. literalinclude:: logger.example.ini
   :language: ini
   :caption: Example of logging configuration file
   :name: logger.example.ini