.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _howto_deploy_through_a_network:

How to deploy through a network
===============================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

The phase of deployment start by calling `lappdeploy` script from a command
shell. The only argument to pass is the set name according to your organisation
choice (see :ref:`howto_build_the_application_list`)

As any installation of program, you must launch the script with administrator
privilege (right click on the command prompt link, and choose
":menuselection:`run as administrator`") .

To push system integration further, you can call this script from a schedule
task with the sending of an summary mail (see `howto_tune_your_environment`).

example
-------

::

    C:>\\myserver\share\lappdeploy.cmd dummy
