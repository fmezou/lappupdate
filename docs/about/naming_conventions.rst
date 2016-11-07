.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

Naming Conventions
==================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

The following topics details the usage of lAppUpdate scripts.

Scripts naming
--------------

Scripts have short, all-lowercase names. 

A script may be `public <Public script>`, `non-public <Non-public script>` or 
a `hook <Hook script>`. 

`Public scripts <Public script>` have all-lowercase names (e.g. ``lappdeploy``).

`Non-public scripts <Non-public script>` have all lowercase names with a leading
underscore (e.g. ``_log2mail``).

`Hook scripts <Hook script>` have all lowercase names with a double leading and
trailing underscore (e.g. ``__init__``).

Furthermore, this set of rules is inspired from the naming convention defining
in :pep:`8#package-and-module-names`.