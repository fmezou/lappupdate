.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lapptrack-devguide:

#########################
lAppTrack Developer Guide
#########################
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

This manual is designed for a *developer audience* to enhance features or to add
plug-in to handle new products. This documentation describes data, classes and
scripts composing the lAppTrack part.

The **lAppTrack** part is written only in Python, and it composed of several
components. The main component is a script (:mod:`lapptrack`) in charge of the
user interface (in text mode), plug-in handling and operations scheduling. The
bulk of the lAppTrack part consists of a collection of python modules grouped
in a package (:mod:`cots`). Each of these modules tracks a :term:`product` based
on the editor's information sources and fetches the updates.


.. toctree::
    :maxdepth: 2

    ../../lapptrack/scripts
    ../../lapptrack/cots/index
    ../../lapptrack/support/index
    ../../lapptrack/further-modules
