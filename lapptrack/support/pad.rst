.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

`support.pad` -- Lightweight Portable Application Description Support
=====================================================================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>
.. codeauthor:: Frédéric MEZOU <frederic.mezou@free.fr>
.. automodule:: support.pad
    :platform: all
    :synopsis: Lightweight Portable Application Description Support

Objects reference
-----------------
This section details the objects defined in this module.

.. autoclass:: PadParser
    :members:
    :private-members:
    :show-inheritance:


Exceptions reference
--------------------
This section details the specific exception used in this module.

.. autoexception:: Error
    :members:
    :private-members:
    :show-inheritance:
.. autoexception:: SpecSyntaxError
    :members:
    :private-members:
    :show-inheritance:
.. autoexception:: PADSyntaxError
    :members:
    :private-members:
    :show-inheritance:

Definitions files
-----------------

.. literalinclude:: padspec40.xml
   :language: xml
   :caption: PAD specification version 4.0
   :name: padspec40.xml
