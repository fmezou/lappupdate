.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any


:mod:`support.report` -- Reporting Manager
==========================================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>
.. codeauthor:: Frédéric MEZOU <frederic.mezou@free.fr>
.. automodule:: support.report
    :platform: all
    :synopsis: Reporting Manager


Objects reference
-----------------
This section details the objects defined in this module.

.. autoclass:: Report
    :members:
    :private-members:
    :show-inheritance:

.. autoclass:: BaseHandler
    :members:
    :private-members:
    :show-inheritance:

.. autoclass:: MailHandler
    :members:
    :private-members:
    :show-inheritance:

.. autoclass:: FileHandler
    :members:
    :private-members:
    :show-inheritance:

.. autoclass:: StreamHandler
    :members:
    :private-members:
    :show-inheritance:


Configuration file
------------------

.. literalinclude:: report.example.ini
   :language: ini
   :caption: Example of configuration file
   :name: report.example.ini


Report Templates
-----------------

.. literalinclude:: report_template.html
   :language: html
   :caption: HTML Default template
   :name: report_template.html

.. literalinclude:: report_template.txt
   :language: text
   :caption: Example of a text template
   :name: report_template.txt