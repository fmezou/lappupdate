.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _background_mock-script:

Mocking Script Format
=====================

The `cots.mock` module uses a mocking script which described the behaviour of
the :dfn:`mock handler`. It contains a list of python statement for each public
method which will be dynamically executed. This file uses the JavaScript Object
Notation (JSON), specified by :rfc:`7159`.

The `cots.mock.scripts_fname` variable specifies the file name of the script
file, and the `cots.mock.script` variable specifies the script to play.

The catalog contains several level of nested objects. The root level contains
the main object.

================    ============================================================
{name}              is an object specifying a script. It's this name that the
                    `cots.mock.script` variable contains.
================    ============================================================

Each script is an object specifying the public method which will be patched
(see `BaseProduct` class). If a public method is not declared or contains an
empty list, the :dfn:`mock` module do mothing (i.e. the behaviour of the
method isn't patched)

================    ============================================================
dump                see `BaseProduct.dump` method.
load                see `BaseProduct.load` method.
fetch               see `BaseProduct.fetch` method.
get_origin          see `BaseProduct.get_origin` method.
is_update           see `BaseProduct.is_update` method.
================    ============================================================

Each :dfn:`method` is a list of python statement which will be executed with the
`exec` function.

.. topic:: Example of a mocking script

   .. literalinclude:: /lapptrack/cots/mock.example.json
      :language: json
