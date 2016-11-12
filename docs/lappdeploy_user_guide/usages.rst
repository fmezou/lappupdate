.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _lappdeploy-userguide_usages:

******
Usages
******
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

The following topics details the usage of lAppUpdate scripts. Complying with the
`about_scripts-naming` convention.

**Public scripts** are those that you can use.

.. toctree::
    :maxdepth: 1

    lappdeploy

**Hook scripts** are only call from lAppUpdate scripts and have a public
interface. These scripts are designed for doing third parties tasks at specific
time.

.. toctree::
    :maxdepth: 1

    exit
    init
    postinstall

**Non-public scripts** are those that are not intended to be used by third
parties, so these scripts may change or even removed. **Their presence here is
only in a purpose of information.**

.. toctree::
    :maxdepth: 1

    appfilter
    log2mail

