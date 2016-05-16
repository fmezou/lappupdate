.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _catalog_format:

Catalog Format
==============

The catalog is a file which is automatically generated, and **must not be
manually modified**. It contains the applications database and specifies the
following properties, for each application, using the JavaScript Object Notation
(JSON), specified by :rfc:`7159`. The :mod:`appdownload` script uses this
database to build the input files used by the ``appdeploy`` script.

The constant `appdownload.CATALOG_FNAME` specifies the file name of the catalog
and it's located in the 'store' folder (see item '`store`_' in the configuration
file).

The catalog contains several level of nested objects. The root level contains
the metadata of the database and the main object.

================    ============================================================
__version__         is the version number of the catalog scheme.
__warning__         is a warning message reminding that the content must not be
                    modified.
modified            is the date of the latest modification expressed in the
                    :rfc:`3339` format.
products            is an object specifying the list of handled application as
                    described in the configuration file (see ``--configfile``).
================    ============================================================

Each item of the products list is a 3-tuple specifying the deployment state of
the application.

================    ============================================================
pulled              indicate that the editor of the application has published an
                    update or a new major version.
fetched             indicate that an update or a new major version of the
                    application has been fetched. At this step, the system
                    administrator must approved the version before its
                    deployment (see ``--approve``)
approved            indicate that the system administrator approved the
                    deployment of the update or the new version. This version
                    will be added in the `applist` file (see ``--make``) to be
                    deployed.
================    ============================================================

Each item of the 3-tuple is an object containing the following attributes of the
application.

================    ============================================================
name                is the name of the product (used in a_report mail and log
                    file)
display_name        is the name of the product as it appears in the 'Programs
                    and Features' control panel (see `Uninstall Registry Key`_)
version             is the current version of the product.
published           is the date of the installer’s publication expressed in the
                    :rfc:`3339` format.
description         is a short description of the product (~250 characters)
editor              is the name of the editor of the product
url                 is the url of the current version of the installer
file_size           is the size of the product installer expressed in bytes
secure_hash         is the secure hash value of the product installer. It's a
                    2-tuple containing, in this order, the name of secure hash
                    algorithm (see `hashlib.algorithms_guaranteed`)
                    and the secure hash value in hexadecimal notation.
icon                is the name of the icon file located in the same directory
                    than the installer.
target              is the target architecture type (the Windows’ one) for the
                    application. This argument must be one of the following
                    values: ``x86``, ``x64`` or ``unified``.

                    * ``x86``: the application works only on 32 bits
                      architecture
                    * ``x64``: the application works only on 64 bits
                      architecture
                    * ``unified``: the application or the installation program
                      work on both architectures

release_note        is the release note’s URL for the current version of the
                    application
installer           is the path of the installer.
std_inst_args       are the arguments of the installer command line to make an
                    standard installation (i.e. an interactive installation).
silent_inst_args    are the arguments of the installer command line to make
                    an silent installation (i.e. without any user's interaction,
                    typically while an automated deployment using ``appdeploy``
                    script).
================    ============================================================

Example

.. code-block:: json

    {
        "__version__": "0.2.0",
        "__warning__": "This file is automatically generated, and must not be
        manually modified. It contains the applications database and specifies
        for each application its properties. Appdownload script uses this
        database to build the applist files used by appdeploy script.",
        "modified": "2016-02-28T19:30:00",
        "products": {
            "dummy": {
                "approved": {
                    "description": "This dummy module is a trivial example of a
                    Product class implementation. ",
                    "display_name": "Dummy Product (1.0.1)",
                    "editor": "Example. inc",
                    "file_size": -1,
                    "icon": "",
                    "installer": "tempstore\\dummy\\Dummy Product_1.0.1.html",
                    "name": "Dummy Product",
                    "published": "2016-02-28T19:04:43",
                    "release_note": "http://www.example.com/release_note.txt",
                    "secure_hash": null,
                    "silent_inst_args": "/silent",
                    "std_inst_args": "",
                    "target": "unified",
                    "url": "http://www.example.com/index.html",
                    "version": "1.0.1"
                },
                "fetched": {},
                "pulled": {}
            }
        }
    }

.. _Uninstall Registry Key: https://msdn.microsoft.com/library/windows/desktop/
    aa372105%28v=vs.85%29.aspx
.. _store: http://fmezou.github.io/lappupdate/lappupdate_wiki.html#appdownload.
    ini%20Core%20Section