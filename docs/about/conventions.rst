.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _about_naming:

Conventions
===========
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

The following topics details the conventions used in the project.

.. _about_scripts-naming:

Scripts naming
--------------

Scripts have short, all-lowercase names. 

A script may be `public <Public script>`, `non-public <Non-public script>` or 
a `hook <Hook script>`. 

*   `Public scripts <Public script>` have all-lowercase names (e.g.
    ``lappdeploy``).

*   `Non-public scripts <Non-public script>` have all lowercase names with a
    leading underscore (e.g. ``_log2mail``).

*   `Hook scripts <Hook script>` have all lowercase names with a double leading
    and trailing underscore (e.g. ``__init__``).

Furthermore, this set of rules is inspired from the naming convention defining
in :pep:`8#package-and-module-names`.

.. _about_usage-syntax:

Usage description syntax
------------------------
Built-in usage help and usages topics comply with the
`Windows command line syntax`_ reminded below.

* angle brackets for *required* parameters: :command:`ping <hostname>`
* square brackets for *optional* parameters: :command:`mkdir [-p] <dirname>`
* ellipses for *repeated* items: :command:`cp <source1> [source2...] <dest>`
* vertical bars for *choice* of items: :command:`netstat {-t|-u}`

Furthermore, usage topics comply the rules defining in 'Python Developer's
Guide' :pep:`257#multi-line-docstrings`, by documenting the script's function
and command line syntax, environment variables, and files.
