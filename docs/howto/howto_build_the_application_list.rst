.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _howto_build_the_application_list:

How to build the application list
=================================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

The `lappdeploy` script uses two `applist` files to verify which applications 
were installed and if it needs to be updated: the first one is named
:file:`applist-all.txt`; the second is named  :file:`applist-{set}.txt` where
`{set}` is the argument passed to `lappdeploy` on the command line (e.g.
:command:`.\lappdeploy dummy`).

.. tip::

    applist files may be empty including :file:`applist-all.txt`.

These files are `text file`_ complying with the `Windows standard`_. So you can
use any text editor (e.g. notepad, notepad++, vim...) to edit them.

The `applist` topic details the format of these files.

In fact, you can have so much file as you want according to your needs. For
example, you can have an `applist` file per computer or a set of computer
(e.g. children, purchasing department...). If you use a domain controller, you
can match `applist` files with your Organisational Units (OU).

By default, the `applist` files are stored in the :file:`appstore` directory
located at the same level that the directory containing the `lappdeploy` script.
To change the location of `applist` files and installers packages, you must tune
the `APP_STORE_DIR` environment variable.

Applications store
------------------
A way of making is to store installers into the same directory that `applist`
files with a separate folder for each product (Mozilla Firefox and its extension
may be considered as one product). It clarifies the installers organisation and
allow to have a `__postinstall__` :term:`hook script` for each of them.

example
-------

.. literalinclude:: /docs/background_papers/applist.example.txt
   :language: text
   :name: applist.example.txt

.. _text file: http://en.wikipedia.org/wiki/Text_file
.. _Windows standard: http://en.wikipedia.org/wiki/Text_file
   #Standard_Windows_.txt_files
