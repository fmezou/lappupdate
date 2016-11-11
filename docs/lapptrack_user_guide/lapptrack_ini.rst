.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lapptrack_ini:

lapptrack.ini
=============
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

This file contains the configuration of `lapptrack` script. It use a structure
similar to what’s found in Microsoft Windows INI files, and parse with the
`configparser` module of the Python standard library. See the 'Supported INI
File Structure' section to have details about the file format.

The configuration consists of three main sections and one section per
applications such as below.

* :ref:`core-section` contains general parameter

* :ref:`sets-section` contains the list of named sets used to deploy
  applications

* :ref:`applications-section` contains the list of applications to maintains.

* :ref:`application-section` contains configuration items for a specific
  application.

The following items details each sections and the associated options, and give
an example. The '`lapptrack.example.ini`' topic give a whole example.


.. _core-section:

Core Section
------------
The ``[core]`` section contains general parameters.

====================  ==========================================================
``store``             (mandatory) contains the path where installation package
                      and `applist` files are stored
``logger``            (optional) contains the path name of the configuration
                      file of the logging system based on `logging` module.
``pulling_report``    (optional) contains the path name of the configuration
                      file of the pulling activity report  (see `cots.report`
                      for detailed information.
``fetching_report``   (optional) contains the path name of the configuration
                      file of the fetching activity report (see `cots.report`
                      for detailed information.
``approving_report``  (optional) contains the path name of the configuration
                      file of the approving activity report (see `cots.report`
                      for detailed information.
====================  ==========================================================

Example of a ``[core]`` section

.. literalinclude:: /lapptrack/lapptrack.example.ini
   :language: ini
   :lines: 13-18

.. _sets-section:

Sets Section
------------
The ``[sets]`` section contains the list of named sets used to deploy
applications.

====================  ==========================================================
``<name>``            (mandatory) is the name of the set and contains a set of
                      computer names or any organisational units according with
                      the lappdeploy script call. A set may be empty, in this
                      case, no file is going to be created for this one.

                      * ``__manual__``: is a special set to specify that the
                        installer must be manually launched (an user interaction
                        is necessary)

                      * ``__thirdparty__``: is a special set to specify that the
                        installer is going to be launched from an other
                        installer (extension or language pack for exemple)

                      * ``__all__``: is a special set to specify that the
                        installer is going to be launched on all computer.
====================  ==========================================================

Example of a ``[sets]`` section

.. literalinclude:: /lapptrack/lapptrack.example.ini
   :language: ini
   :lines: 30-34

.. _applications-section:

Applications Section
--------------------
The ``[applications]`` section contains the list of applications to maintains.

====================  ==========================================================
``<name>``            (mandatory) is the name of the `application section
                      <application-section>` and contains a flag specifying if
                      the application have been taking into account.
====================  ==========================================================

Example of a ``[applications]`` section

.. literalinclude:: /lapptrack/lapptrack.example.ini
   :language: ini
   :lines: 39-42

.. _application-section:

Application Section
-------------------
The application (``[<name>]``) section contains configuration items for
a specific application.

.. warning::

    Name section must be lowercase, since the section name is a key in
    `applications section <applications-section>`

====================  ==========================================================
``handler``           (optional) is the qualified name of the handler class (A
                      dotted name showing the “path” from the global scope to
                      the handler class). The default value is
                      ``cots.<section name>.<section name>Handler`` with the
                      first letter of section capitalised for having a camel
                      case name for the class handler.
``path``              (optional) is the path name where to store the installer
                      package. The default value is ``${core:store}\<section
                      name>``.
``set``               (optional) is the name of the set associated with the
                      application (see `sets-section`). The default value is
                      ``__all__``.
====================  ==========================================================

Example of an application section

.. literalinclude:: /lapptrack/lapptrack.example.ini
   :language: ini
   :lines: 58-61

.. _lapptrack.example.ini:

Example of lapptrack.ini
------------------------

.. literalinclude:: /lapptrack/lapptrack.example.ini
   :language: ini
