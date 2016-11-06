.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _howto_deploy_applications:

**************************
How to deploy applications
**************************
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

.. sidebar:: Be simple

    If you manage a unique PC connected to Internet, the easiest way is to let
    each application managing its own upgrades (automatically or manual way).

To deploy application, there are two main use cases. The first one is based on a
share network, the second is based on a DVD distribution. These cases have their
own constraints and answer to specific needs. The main advantage to have a
centralised application deploying system is to allow to a system administrator
to have a consistency application park.

The use of a network share implies that the pc is connected to a local network,
with an available file server. This use case is recommended for SOHO application
deploying (less than 10 pc) and allows silent installation of patches or new
applications.

The use of a DVD is attractive for use in a standalone and non connected
environment (e.g. Industrial PC or access control management console).

But, these two use cases comply with the following steps:

#.  :ref:`Tune your environment <howto_tune_your_environment>`

#.  :ref:`Build the application list to deploy
    <howto_build_the_application_list>`

#.  :ref:`Build the medium <howto_build_the_medium>`

#.  Deploy applications from a :ref:`DVD <howto_deploy_from_a_dvd>` or
    :ref:`Network share <howto_deploy_through_a_network>`
