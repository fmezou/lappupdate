.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _release_versioning:

Versioning scheme
=================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

Each release of lAppUpdate is identified by a version number that complies with
the `Semantic Versioning 2.0.0 <http://semver.org/>`_ standard.

Core Version
------------
According to the standard, given a version number MAJOR.MINOR.PATCH, increment
the:

* MAJOR version when you make incompatible API changes,

* MINOR version when you add functionality in a backwards-compatible manner,

* PATCH version when you make backwards-compatible bug fixes.

Additional labels for pre-release and build metadata are available as extensions
to the MAJOR.MINOR.PATCH format.

Alpha and Beta versions
-----------------------
While in alpha lAppUpdate uses the pre-release label "alpha" followed by a dot
and a release counter. Every alpha or beta releases increment the release
counter (for example : ``1.0.1-alpha.0``)

Interim versions
----------------
During development when a new release is being prepared, the pre-release label
is set to ``prerelease``.