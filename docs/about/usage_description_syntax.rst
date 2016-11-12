.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _about_usages:

Usages
======
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

The following topics details the usage of lAppUpdate scripts.

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

.. _Windows command line syntax: http://technet.microsoft.com/en-us/library/
    cc771080.aspx