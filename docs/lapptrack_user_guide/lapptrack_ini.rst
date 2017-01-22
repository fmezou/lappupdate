.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lapptrack-userguide_lapptrack-ini-content:

lapptrack.ini Content
=====================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

This file contains the configuration of :doc:`lapptrack` script. It use a
structure similar to what’s found in Microsoft Windows INI files, and parse with
the `configparser` module of the Python standard library. See the 'Supported INI
File Structure' section to have details about the file format.

The configuration consists of three main sections and one section per
applications such as below.

* :ref:`lapptrack-userguide_lapptrack-ini-core-section` contains general
  parameter

* :ref:`lapptrack-userguide_lapptrack-ini-sets-section` contains the list of
  named sets used to deploy applications

* :ref:`lapptrack-userguide_lapptrack-ini-applications-section` contains the
  list of applications to maintains.

* :ref:`lapptrack-userguide_lapptrack-ini-application-section` contains
  configuration items for a specific application.

The following items details each sections and the associated options, and give
an example.

.. topic:: Example of lapptrack.ini

   .. literalinclude:: /lapptrack/lapptrack.example.ini
      :language: ini

.. _lapptrack-userguide_lapptrack-ini-core-section:

Core Section
------------
The ``[core]`` section contains general parameters.

====================  ==========================================================
``store``             (mandatory) contains the path where installation package
                      and `applist` files are stored
``logger``            (optional) contains the path name of the configuration
                      file of the logging system based on `logging` module.
``pulling_report``    (optional) contains the path name of the configuration
                      file of the pulling activity report  (see `support.report`
                      for detailed information.
``fetching_report``   (optional) contains the path name of the configuration
                      file of the fetching activity report (see `support.report`
                      for detailed information.
``approving_report``  (optional) contains the path name of the configuration
                      file of the approving activity report (see
                      `support.report` for detailed information.
====================  ==========================================================

.. topic::  Example of a ``[core]`` section

   .. literalinclude:: /lapptrack/lapptrack.example.ini
      :language: ini
      :lines: 13-18

.. _lapptrack-userguide_lapptrack-ini-sets-section:

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

.. topic:: Example of a ``[sets]`` section

   .. literalinclude:: /lapptrack/lapptrack.example.ini
      :language: ini
      :lines: 30-34

.. _lapptrack-userguide_lapptrack-ini-applications-section:

Applications Section
--------------------
The ``[applications]`` section contains the list of applications to maintains.

====================  ==========================================================
``<name>``            (mandatory) is the name of the `application section
                      <lapptrack-userguide_lapptrack-ini-application-section>`
                      and contains a flag specifying if the application have
                      been taking into account.
====================  ==========================================================

.. topic:: Example of a ``[applications]`` section

   .. literalinclude:: /lapptrack/lapptrack.example.ini
      :language: ini
      :lines: 39-42

.. _lapptrack-userguide_lapptrack-ini-application-section:

Application Section
-------------------
The application (``[<name>]``) section contains configuration items for
a specific application.

.. warning::

    Name section must be lowercase, since the section name is a key in
    `applications section
    <lapptrack-userguide_lapptrack-ini-applications-section>`

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
                      application (see
                      `lapptrack-userguide_lapptrack-ini-sets-section`). The
                      default value is ``__all__``.
====================  ==========================================================

.. topic:: Example of an application section

   .. literalinclude:: /lapptrack/lapptrack.example.ini
      :language: ini
      :lines: 58-61
