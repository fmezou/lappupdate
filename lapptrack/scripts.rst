.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

***********
Main Script
***********
The main component is the :mod:`lapptrack` module which offers a command line
interface and is in charge of plug-in handling and operations scheduling.

To sum up, this module call a product handler from the `cots` package to
retrieve product information and the updated installer from the web site's
editor, store theses information in a :term:`catalog` and makes the input files
used by the ``lappdeploy`` script.

.. toctree::
    :maxdepth: 1

    lapptrack