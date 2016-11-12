.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _global-glossary:

########
Glossary
########
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

.. glossary::
    :sorted:

    Applist
        The applist file describe a list of application packages which will be
        deployed on a workstation or a server. The `background_applist-format`
        details the content of this file.

    Catalog
        A file where :class:`lAppTrack` class (resp. :mod:`lapptrack`
        script) stores information (name, version, published date,...) about the
        handled products.

    COST
    Commercial off-the-shelf
        It's is a term which refer to packaged solutions which are then adapted
        to satisfy the needs of the organisation, rather than the commissioning
        of custom made solutions. This `wikipedia article <https://en.wikipedia.
        org/wiki/Commercial_off-the-shelf>`_ give you more details.

    Hook script
        Hook scripts are only call from lAppUpdate scripts and have a public
        interface. These scripts are designed for doing third parties tasks
        (e.g. tuning the environment) at specific time (i.e before starting
        the script). By definition, a hook script is optional and may be not
        exist.

        .. note::

            a hook script name is hard coded in the caller script, so the name
            is considered like a reserved keyword and cannot be modified.

    Public script
        Public scripts are those that you can use, with the commitment to avoid
        backward incompatible changes (i.e. specially with the command line
        options).

    Non-public script
        Non-public scripts are those that are not intended to be used by third
        parties, so these scripts may change or even removed.

    Product
        A product is an commercial software tracked and deployed by lAppUpdate.
        It is commercial or a custom software, where commercial term covers
        :term:`commercial off-the-shelf` , free software and open source
        software [#f1]_.

.. rubric:: Footnotes

.. [#f1] Free-Libre / Open Source Software (FLOSS) is Commercial Software,
   http://www.dwheeler.com/essays/commercial-floss.html.

