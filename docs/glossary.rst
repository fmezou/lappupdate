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
        A catalog is a file where :class:`LAppTrack` class (resp.
        :mod:`lapptrack` script) stores information (name, version, published
        date,...) about the handled products.

    COST
    Commercial off-the-shelf
        Commercial off-the-shelf refers to packaged solutions which are then
        adapted to satisfy the needs of the organisation, rather than the
        commissioning of custom made solutions.

        .. seealso::

            `Commercial off-the-shelf <https://en.wikipedia. org/wiki/
            Commercial_off-the-shelf>`_ Wikipedia article

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

    Progress bar
        A progress bar is a element of a user interface to visualize the
        progression of an extended computer operation, such as a download, file
        transfer, or installation.

        .. seealso::

            `Progress bar <https://en.wikipedia.org/wiki/Progress_bar>`_
            Wikipedia article

    Progress indicator
        A progress indicator is a element of a user interface to inform the user
        that an operation is in progress.

        .. seealso::

            `Progress indicator <https://en.wikipedia.org/wiki/
            Progress_indicator>`_ Wikipedia article

    Non-public script
        Non-public scripts are those that are not intended to be used by third
        parties, so these scripts may change or even removed.

    Product
        A product is an commercial software tracked and deployed by lAppUpdate.
        It is commercial or a custom software, where commercial term covers
        :term:`commercial off-the-shelf` , free software and open source
        software [#f1]_.

    Silent install
        A silent install is an installation process which require no user
        intervention, accordingly installation options are set to default
        values or may be tuned with command line options.

    Throbber
        A throbber is an animated widget used to show that an extended computer
        operation, such as a download, file transfer, or installation is in
        progress. In contrast to a `progress bar`, a throbber does not inform
        how much of the action has been completed.

        .. seealso::

            `Throbber <https://en.wikipedia.org/wiki/Throbber>`_ wikipedia
            article


.. rubric:: Footnotes

.. [#f1] Free-Libre / Open Source Software (FLOSS) is Commercial Software,
   http://www.dwheeler.com/essays/commercial-floss.html.

