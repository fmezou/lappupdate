.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lapptrack-userguide_report-template:

Report Template
===============
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

This file contains the configuration of the logging facility used by the
:doc:`lapptrack` script. It use a structure similar to what’s found in Microsoft
Windows INI files. See the `Configuration file format
<logging-config-fileformat>` section to have details about the file format.

.. sidebar:: future

    the report module will use the `Jinja2 template engine
    <http://jinja.pocoo.org/>`_ in a next release.

A report is based on a template using named keyword argument and composed of
named sections. The module use the :file:`report_template.html` by default.
The use of the named keyword argument is based on the `string` module.

Each section starts with a HTML comment and it ends with the start of next
section or the end of the file. The comment match the following format and
must be on one line::

    <!-- $lau:<name>$ -->

``<name>`` is the name of the section. It MUST comprise only ASCII alphanumerics
and hyphen [0-9A-Za-z-] and MUST NOT be empty. If a named section is not
declared in `Report.names`, its contents is added to the current section
(i.e. no section is created).

.. topic:: Example of Report Template

   .. literalinclude:: /lapptrack/support/report_template.html
      :language: html
