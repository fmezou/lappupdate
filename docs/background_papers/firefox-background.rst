.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _background_firefox:

Firefox
=======
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

.. sidebar:: Firefox

    .. image:: firefox_logo-wordmark.png
        :align: center
        :height: 48pt
        :target: https://www.mozilla.org/firefox

    Published by `Mozilla Foundation <https://www.mozilla.org/en-US/foundation/>`_,
    Firefox is a `free <http://www.gnu.org/philosophy/free-sw.html>`_ and
    `open-source <http://www.opensource.org/docs/definition.php>`_ web browser.

    License: `Mozilla Public License <https://www.mozilla.org/en-US/MPL/>`_

    Download: `Rapid Release (RR) <http://www.mozilla.org/firefox/all/>`_,
    `Extended Support Release (ESR) <https://www.mozilla.org/firefox/organizations/all.html>`_

    `Firefox Branding
    <https://www.mozilla.org/en-US/styleguide/identity/firefox/branding/>`_

This topic introduces installers features or tools that can be used to deploy
Firefox and centrally manages its configuration in small organisations. It also
describes the mechanism used to notify users and distribute updates (security
patches, full version...) and what `lapptrack` uses to track Firefox updates.


Deployment Tips
---------------

As for all the mozilla products, the :ref:`background_mozilla.deployment_tips`
section for :ref:`background_mozilla` details the common deployment tips.

The `Deploying Firefox in an enterprise environment
<https://developer.mozilla.org/en-US/Firefox/Enterprise_deployment>`_ article
details how to tune the configuration and gives alternative scenarios to
deploy extensions in line with your use cases.

The snippet below shows a :ref:`post install
<lappdeploy-userguide_postinstall-usage>` script to deploy extension for Firefox
(Windows 64-bit)

.. topic:: Deploy Firefox Extensions

    .. code-block:: winbatch

        setlocal
        set AddonsRootPath=%ProgramFiles%\Mozilla Firefox\browser\extensions
        pushd %~dp0
        rem Deleting old plug-ins
        rem if exist "%AddonsRootPath%\{id}.xpi" del "%AddonsRootPath%\{id}.xpi"
        rem copy to upgrade or install extensions
        xcopy "%cd%\extensions" "%AddonsRootPath%" /i /s /e /d /v /c /y
        popd
        endlocal


.. _background_firefox-installer_options:

Installer Options
-----------------

As for all the mozilla products, the :ref:`background_mozilla.installer_options`
section for :ref:`background_mozilla` details the common installer options.


Update Mechanism
----------------

As for all the mozilla products, the :ref:`background_mozilla.update_mechanism`
section for :ref:`background_mozilla` details the update mechanism.
