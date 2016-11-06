.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

`cots.core` -- Product Handler Core Module
==========================================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>
.. codeauthor:: Frédéric MEZOU <frederic.mezou@free.fr>
.. automodule:: cots.core
    :platform: all
    :synopsis: Product Handlers Core Module

Objects reference
-----------------
This section details the objects defined in this module.

.. autoclass:: BaseProduct
    :members:
    :private-members:
    :show-inheritance:

Functions reference
-------------------
This section details the specific functions used in this module.

.. autofunction:: retrieve_file
.. autofunction:: retrieve_tempfile
.. autofunction:: get_handler

Data reference
--------------
This section details global data, including both variables and values used
as 'defined constants'.

.. autodata:: TARGET_X86
.. autodata:: TARGET_X64
.. autodata:: TARGET_UNIFIED

Exceptions reference
--------------------
This section details the specific exception used in this module.

.. autoexception:: UnexpectedContentLengthError
    :members:
    :show-inheritance:
.. autoexception:: UnexpectedContentError
    :members:
    :show-inheritance:
.. autoexception:: UnexpectedContentTypeError
    :members:
    :show-inheritance:
