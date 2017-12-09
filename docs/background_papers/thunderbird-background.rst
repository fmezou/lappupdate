.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _background_thunderbird:

Thunderbird
===========
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

.. sidebar:: Thunderbird

    .. image:: thunderbird_logo-wordmark.png
        :align: center
        :height: 48pt
        :target: https://www.mozilla.org/thunderbird

    Published by `Mozilla Foundation <https://www.mozilla.org/en-US/foundation/>`_,
    thunderbird is a `free <http://www.gnu.org/philosophy/free-sw.html>`_ and
    `open-source <http://www.opensource.org/docs/definition.php>`_ email client.

    License: `Mozilla Public License <https://www.mozilla.org/en-US/MPL/>`_

    Download: `Mainstream Release <http://www.mozilla.org/thunderbird/all/>`_

    The Thunderbird Extended Support Releases (ESR) have now been merged
    into the `mainstream releases <https://www.mozilla.org/en-US/thunderbird/
    organizations/>`_ [#esr]_

    `Thunderbird Branding <https://www.mozilla.org/en-US/styleguide/identity/
    thunderbird/logo/>`_

This topic introduces installers features or tools that can be used to deploy
Thunderbird and centrally manages its configuration in small organisations. It
also describes the mechanism used to notify users and distribute updates
(security patches, full version...) and what `lapptrack` uses to track
Thunderbird updates.


Deployment Tips
---------------

As for all the mozilla products, the :ref:`background_mozilla.deployment_tips`
section for :ref:`background_mozilla` details the common deployment tips.

The `Deploying Thunderbird in the Enterprise <https://developer.mozilla.org
/en-US/docs/Mozilla/Thunderbird/Deploying_Thunderbird_in_the_Enterprise>`_
article details how to tune the configuration and gives alternative scenarios to
deploy extensions in line with your use cases.

The snippet below shows a :ref:`post install
<lappdeploy-userguide_postinstall-usage>` script to deploy extension for
Thunderbird (Windows)

.. topic:: Deploy Thunderbird Extensions

    .. code-block:: winbatch

        setlocal
        set AddonsRootPath=%ProgramFiles(x86)%\Mozilla Thunderbird\extensions
        pushd %~dp0
        rem Deleting old plug-ins
        rem {BDD92442-0534-4D6F-A966-BAB7D561D781}: google_contacts
        rem {ad7d8a66-253b-11dc-977c-000c29a3126e}: Zindus
        rem en-gb@flyingtophat.co.uk: British English Dictionary (Updated)
        if exist "%AddonsRootPath%\{BDD92442-0534-4D6F-A966-BAB7D561D781}.xpi" del "%AddonsRootPath%\{BDD92442-0534-4D6F-A966-BAB7D561D781}.xpi"
        if exist "%AddonsRootPath%\{ad7d8a66-253b-11dc-977c-000c29a3126e}.xpi" del "%AddonsRootPath%\{ad7d8a66-253b-11dc-977c-000c29a3126e}.xpi"
        if exist "%AddonsRootPath%\en-gb@flyingtophat.co.uk.xpi" del "%AddonsRootPath%\en-gb@flyingtophat.co.uk.xpi"
        rem copy to upgrade or install extensions
        rem lightning folder must be deleted be copy to delete obsolete files.
        if exist "%AddonsRootPath%\{e2fda1a4-762b-4020-b5ad-a41df1933103}" rmdir /s /Q "%AddonsRootPath%\{e2fda1a4-762b-4020-b5ad-a41df1933103}"
        xcopy "%cd%\extensions" "%AddonsRootPath%" /i /s /e /d /v /c /y
        popd
        endlocal

.. _background_thunderbird-installer_options:

Installer Options
-----------------

As for all the mozilla products, the :ref:`background_mozilla.installer_options`
section for :ref:`background_mozilla` details the common installer options.


Update Mechanism
----------------

As for all the mozilla products, the :ref:`background_mozilla.update_mechanism`
section for :ref:`background_mozilla` details the update mechanism.

.. rubric:: References

.. [#esr] `Extended Support Release <https://www.mozilla.org/en-US/thunderbird/
   organizations/>`_