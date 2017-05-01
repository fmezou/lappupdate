.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _background_firefox:

Mozilla Firefox
===============
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

.. sidebar:: Mozilla Firefox

    .. image:: firefox_logo.png
        :align: center
        :height: 83

    Published by `Mozilla Foundation <https://www.mozilla.org/en-US/foundation/>`_,
    Firefox is a `free <http://www.gnu.org/philosophy/free-sw.html>`_ and
    `open-source <http://www.opensource.org/docs/definition.php>`_ web browser
    available under the `Mozilla Public License <https://www.mozilla.org/en-US/MPL/>`_.

    Download: `Rapid Release (RR) <http://www.mozilla.org/firefox/all/>`_,
    `Extended Support Release (ESR) <https://www.mozilla.org/firefox/organizations/all.html>`_

    Web site: https://www.mozilla.org/firefox

A deployment plan should consider the three following issues:

* making a installation without any user intervention, i.e. making a `silent
  install`
* setting a default configuration in line with your use cases
* distributing security patches, new features or versions

This topic introduces installers features or tools that can be used to deploy
Firefox and centrally manages its configuration in small organisations. It also
describes the mechanism used to notify users and distribute updates (security
patches, full version...) and what `lapptrack` uses to track Firefox updates.


Deployment Tips
---------------

Mozilla installer covers the two first issues. The command line option for a
:dfn:`silent install` is ``-ms`` and additional installation options may be
tuned in a configuration file specified with ``/INI``. See
:ref:`background_firefox-installer_options` for an overview of the installer
command line options.

All configuration parameters are stored in configuration files and Mozilla
products offer a mechanism, using text files, to tuned the configuration at
application startup (with or without the overwriting of user's modification).
The `Deploying Firefox in an enterprise environment
<https://developer.mozilla.org/en-US/Firefox/Enterprise_deployment>`_ article
details how to achieve this goal in line with your use cases.

Mozilla product offers a background service named `Mozilla Maintenance Service
<https://support.mozilla.org/t5/Install-and-Update/What-is-the-Mozilla-
Maintenance-Service/ta-p/11800>`_ which allows application updates to occur in
the background without any user intervention. In a centrally managed environment
this service is not required, so its installation may be skipped by setting the
``MaintenanceService`` key to ``false`` in the `configuration installation file
<https://wiki.mozilla.org/Installer:Command_Line_Arguments>`_ or unsinstall the
Maintenance Service as a :ref:`post install
<lappdeploy-userguide_postinstall-usage>` action.

.. topic:: Uninstall the Mozilla Maintenance Service

    .. code-block:: winbatch

        "%ProgramFiles(x86)%\Mozilla Maintenance Service\uninstall.exe" /S

In a deployment plan for Mozilla products, the extensions deployment should be
taken into account as a part of the plan. There is several scenarios to achieve
this goal. The simplest method is to rename the .xpi file or the folder with the
extension ID [#emid]_ and to drop it into the :file:`{program directory}\\browser
\\extensions`. The `Deploying Firefox in an enterprise environment
<https://developer.mozilla.org/en-US/Firefox/Enterprise_deployment>`_ article
gives alternative scenarios. The snippet below shows a :ref:`post install
<lappdeploy-userguide_postinstall-usage>` script to deploy extension for Firefox
(Windows 64-bit)

.. topic:: Deploy Mozilla Extensions

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

The installer is based on a Mozilla framework and delivered as a single
executable.

Mozilla installers accepts a few options on the command line. These options give
the user a bit more control over the installation process, mainly doing a
`silent install`. The `Command Line Arguments <https://wiki.mozilla.org/
Installer:Command_Line_Arguments>`_ page details these options and the end of
the section focuses on the silent running mode.

.. program:: firefox setup

.. option:: -ms

    make a silent install.

.. option:: /INI=<PATHNAME>

    specifies the full path name of the configuration file. When a configuration
    is specifying, the installer make a silent install.

.. topic:: Example

    .. code-block:: winbatch

        firefox-setup.exe -ms
        firefox-setup.exe /INI="C:\Installers\Mozilla Firefox\silent.ini"


Update Mechanism
----------------

Mozilla has its own software update system to distribute updates of security
patches and bug fixes for :ref:`Firefox <background_firefox>` and
:ref:`Thunderbird <background_thunderbird>`. The `Mozilla wiki
<https://wiki.mozilla.org/Main_Page>`_ contains an `overview of the software
update system <https://wiki.mozilla.org/Software_Update>`_.

The update system has two components: an *agent* working either in the
application core or as a background service named `Mozilla Maintenance Service
<https://support.mozilla.org/t5/Install-and-Update/What-is-the-Mozilla-
Maintenance-Service/ta-p/11800>`_, and a *server component* named `Balrog
<http://mozilla-balrog.readthedocs.io/en/latest/index.html>`_ (formerly
`Application Update Service <https://wiki.mozilla.org/AUS>`_).

The *agent* sends an :ref:`update request <background_firefox.update_request>`
over HTTPS specifying the installed application version  to the Mozilla update
servers. The *server component* will return a :ref:`manifest file
<background_firefox.manifest_file>` (which is a simple XML file) specifying
the right update package to download. However, this latter is a `Mozilla archive
<https://wiki.mozilla.org/Software_Update:MAR>`_ aimed at the application
updating [#mar]_ (i.e. not a first installation), and Mozilla recommends
[#retr]_ to use a :ref:`download request <background_firefox.download_request>`
to retrieve a release.

Consequently, the update mechanism comprises the following two steps:

#. determination of the latest release for the branch with an
   :ref:`update request <background_firefox.update_request>`
#. making the :ref:`download request <background_firefox.download_request>` with
   the attributes of the ``update`` element from the received :ref:`manifest
   file <background_firefox.manifest_file>`, provided that a *complete* ``patch``
   element is present

.. note:: At the date of writing this section, the Balrog 2.22 documentation
   doesn't describe the request and the manifest file content, so the following
   topics are the result of an analysis work of documentation from the Mozilla
   wiki (see `Software Update <https://wiki.mozilla.org/Software_Update>`_ and
   `AUS <https://wiki.mozilla.org/AUS>`_ wiki pages), the `Balrog repository
   <https://github.com/mozilla/balrog>`_ and testing. So, the specifications may
   be changed in the future.


.. _background_firefox.update_request:

Update Request
^^^^^^^^^^^^^^

The update request URL is defined in the ``app.update.url`` option (see
about:config) and matches the following syntax:

:file:`https://aus5.mozilla.org/update/6/{product}/{version}/{buildID}/{buildTarget}/{locale}/{channel}/{osVersion}/{systemCapabilities}/{distribution}/{distVersion}/update.xml?force=1/`

.. list-table::
   :widths: 10 30 15
   :header-rows: 1

   * - Part
     - Description
     - Value
   * - ``6``
     - The schema version. It exist 6 versions and they differ according to
       the number of parameters. [#schema]_
     -
   * - ``product``
     - The name of the application requesting an update
     - ``Firefox``, ``Thunderbird``
   * - ``version``
     - The version of the application requesting an update. This value is
       present in the `manifest file <background_firefox.manifest_file>`
       (see ``appVersion`` attribute) and in the :file:`platform.ini` file
       (see ``Milestone`` key) located in the installation directory of the
       application.
     - ``42.0``
   * - ``buildID``
     - The build ID of the application requesting an update. It's the
       building date of the application (see `Build section
       <https://wiki.mozilla.org/AUS:Manual#Build>`_). It is used to compare
       the latest available update with what the application currently is,
       and offers the update only if the available update is newer. This
       part may be empty (i.e. space charaters). This value is present in
       the `manifest file <background_firefox.manifest_file>` (see
       ``buildID`` attribute) and in the :file:`platform.ini` file (see
       ``BuildID`` key) located in the installation directory of the
       application.
     - ``20151029151421``
   * - ``buildTarget``
     - The "build target" of the application requesting an update. This is
       usually related to the target platform [#mozharnes]_ the application
       was built for.
     - | ``WINNT_x86-msvc``
       | ``WINNT_x86_64-msvc``
       | ``Linux_x86_64-gcc3``
       | ``Linux_x86-gcc3``
       | ``Darwin_x86_64-gcc3``
   * - ``locale``
     - The locale [#locale]_ of the application requesting an update.
     - ``en-US``, ``fr``
   * - ``channel``
     - The update channel of the application request an update. It is used
       to separate releases from others applications updates. The
       ``app.update.channel`` option defines the update channel for the
       requesting application (see about:config).
     - ``release``
   * - ``osVersion``
     - The OS Version of the application requesting an update. It is used to
       point desupported operating systems to their last supported build.
       For the Windows System family, it consist of "Windows_NT <major>.
       <minor>.<service pack number>" ("Windows_NT 6.1.1" = Microsoft Windows 
       7 version 6.1.7601 Service Pack 1 for example). This part may be
       empty (i.e. consist of space characters)
     - ``Windows_NT 6.1.1``
   * - ``systemCapabilities``
     - The supported hardware features of the application requesting an
       update. It is used to point desupported hardware (hardware which
       don't support SSE2). This part may be empty (i.e. consist of space
       characters)
     - ``SSE3``
   * - ``distribution``
     - The partner distribution name of the application requesting an update
       or "default" if the application is not a partner build.
     - ``default``
   * - ``distVersion``
     - The version of the partner distribution of the application requesting
       an update or "default" if the application is not a partner build.
     - ``default``


.. tip:: The *agent* (only windows version) stores the update request and the
   associated response in the file
   :file:`{%LOCALAPPDATA%}/Mozilla/updates/{E7CF176E110C211B}/active-update.xml`.

.. tip:: At the date of writing this section, the Mozilla update server is
   hosted on ``aus5.mozilla.org``. The `Client Domains page
   <https://wiki.mozilla.org/Balrog/ Client_Domains>`_ details older domains.

.. topic:: Example

    The below URL is an update request from *Mozilla Firefox 50.1.0 (x64 fr)*
    running on *Microsoft Windows 10 (10.0.14393)*::

        https://aus5.mozilla.org/update/6/Firefox/50.1.0/20161208153507/WINNT_x86_64-msvc-x64/fr/release/Windows_NT%2010.0.0.0%20(x64)(noBug1296630v1)/SSE3/default/default/update.xml



.. _background_firefox.manifest_file:

Manifest File
^^^^^^^^^^^^^

On an :ref:`update request <background_firefox.update_request>`, the server
returned a XML file specifying the right update package to download. The XML
schema isn't formally described in the :dfn:`Balrog` documentation, and the
Mozilla wiki contains an `older specification <https://wiki.mozilla.org/
Software_Update:updates.xml_Format>`_ (last updated on october 2015).

A typical manifest file look like the following snippet.

.. code-block:: xml

    <?xml version="1.0"?>
    <updates>
        <update type="minor"
                appVersion="..."
                buildID="..."
                detailsURL="http://download.example.com/releasenotes/..."/>
            <patch type="complete"
                   URL="http://download.example.com/..."/>
            <patch type="partial"
                   URL="http://download.example.com/..."/>
        </update>
    </updates>

Every manifest file contains one ``updates`` element as root without any
attributes.

An ``updates`` element may have ``update`` child elements, each of them
specifying an update to an application version.

.. list-table:: ``update`` element attributes
   :widths: 10 30 15
   :header-rows: 1
   :name: update_attrs

   * - Attribute
     - Description
     - Value
   * - ``type``
     - The update type. This attribute was used to describe a major revision, or
       a minor revision (security releases or incremental updates). Nowadays,
       it's very rare to used anything than ``minor`` [#rule]_.
     - | ``minor``
       | ``major``
   * - ``displayVersion``
     - The application version to display. Generally, the *agent* client will
       show this in the UI.
     - ``43.0.1``
   * - ``appVersion``
     - The version of the application.
     - ``43.0.1``
   * - ``platformVersion``
     - The version of the platform (usually Gecko) that the application
       represented is built from. This attribute is deprecated [#apprelease]_
       since Gecko 51.0 and above (i.e. Firefox/Thunderbird 51.0 and above).
     - ``43.0.1``
   * - ``buildID``
     - The build ID of the application.
     - ``20151216175450``
   * - ``detailsURL``
     - The location of the release note of the application update.
     - ``https://www.mozilla.org/fr/firefox/43.0.1/releasenotes/``

An ``update`` element has at least one and no more than two ``patch`` child
elements specifying a patch file to apply to the application to update it to
that version. A patch file describes either binary differences between versions
of the application (partial patches), or complete updates that replace and
remove files as necessary (i.e. a full installer).

.. list-table:: ``patch`` element attributes
   :widths: 10 30 15
   :header-rows: 1
   :name: patch_attrs

   * - Attribute
     - Description
     - Value
   * - ``type``
     - The type of the patch file.
     - | ``complete``
       | ``partial``
   * - ``URL``
     -  The location of the patch file.
     - ``http://download.mozilla.org/?product=firefox-43.0.1-complete&amp;os=win64&amp;lang=fr``
   * - ``hashFunction``
     - The name of the hash algorithm used to calculate the ``hashValue``
       attribute.
     - ``sha512``
   * - ``hashValue``
     - The hash value of the patch file, calculated using the hash algorithm
       defined in the ``hashFunction`` attribute.
     - ``020c01ba..c7f2``
   * - size
     - The file size of the patch file expressed in bytes.
     - ``56171708``

.. topic:: Example

    The manifest file below is the response to the following update request from
    *Mozilla Firefox 42.0 (x64 fr)* running on *Microsoft Windows 7 Entreprise
    (6.1.7601 Service Pack 1 Build 7601)*::

        https://aus5.mozilla.org/update/3/Firefox/42.0/20151029151421/WINNT_x86_64-msvc-x64/fr/release/Windows_NT%206.1.1.0%20(x64)/default/default/update.xml

    .. code-block:: xml

        <?xml version="1.0"?>
        <updates>
           <update type="minor"
                   displayVersion="43.0.1"
                   appVersion="43.0.1"
                   platformVersion="43.0.1"
                   buildID="20151216175450"
                   detailsURL="https://www.mozilla.org/fr/firefox/43.0.1/releasenotes/">
               <patch type="complete"
                      URL="http://download.mozilla.org/?product=firefox-43.0.1-complete&amp;os=win64&amp;lang=fr"
                      hashFunction="sha512"
                      hashValue="020c01badf94867feb4a91b5a85b9f4ef55a9a22154f0012f89820366b300c2ed3799b0a150760775be1352fe2fee68ffb340583909bba08407086bd2927c7f2"
                      size="56171708"/>
               <patch type="partial"
                      URL="http://download.mozilla.org/?product=firefox-43.0.1-partial-42.0&amp;os=win64&amp;lang=fr"
                      hashFunction="sha512"
                      hashValue="7ad8b74561b378b50248010a9946f8abce18d0a69b8392f4f0cd64438f7cbd34343321fb835c0a53d30605ccb2f8c9f0b3bed5dd210f5c9bf6a682998c450740"
                      size="22914817"/>
           </update>
        </updates>


.. _background_firefox.download_request:

Download Request
^^^^^^^^^^^^^^^^

The download request URL [#retr]_ matches the following syntax:

:file:`https://download.mozilla.org/?product={product}-{version}&os={target}&lang={locale}`

.. list-table::
   :widths: 10 30 15
   :header-rows: 1

   * - Part
     - Description
     - Value
   * - ``product``
     - The name of the application to retrieve
     - ``firefox``, ``thunderbird``
   * - ``version``
     - The version of the application to retrieve. This part may be either a
       version identifier as described in the `Toolkit version format
       <https://developer.mozilla.org/en-US/docs/Toolkit_version_format>`_ topic
       or ``latest`` to retrieve the latest version
     - ``42.0``
   * - ``target``
     - The "build target" of the application to retrieve. This part must
       contain one of the following values:

       * ``win``: Windows 32 bits
       * ``win64``: Windows 64 bits
       * ``osx``: MacOS X
       * ``linux64``: Linux x86 64 bits
       * ``linux``: Linux i686
     - | ``win``
       | ``win64``
       | ``osx``
       | ``linux64``
       | ``linux``

   * - ``locale``
     - The locale [#locale]_ of the the application to retrieve
     - | ``en-US``
       | ``fr``

.. topic:: Example

    The below URL is an download request from *Mozilla Firefox 50.1.0 (x64 fr)*
    running on *Windows 64 bits*::

         https://download.mozilla.org/?product=firefox-50.1.0&os=win64&lang=fr


.. rubric:: References

.. [#schema] The expected schema are defined in the `base python module
   <https://github.com/mozilla/balrog/blob/master/auslib/web/base.py>`_ in the
   Balrog auslib.web Package
.. [#mozharnes] The expected values are defined in the `mozharness package
   <https://hg.mozilla.org/releases/mozilla-release/file/tip/testing/mozharness/
   configs/single_locale>`_.
.. [#rule] `What’s in a rule? <http://mozilla-balrog.readthedocs.io/en/latest/
   database.html#what-s-in-a-rule>`_
.. [#apprelease] `apprelease module <https://github.com/mozilla/balrog/blob/
   master/auslib/blobs/apprelease.py>`_ in the Balrog repository
.. [#mar] `Manually Installing a MAR file
   <https://wiki.mozilla.org/ Software_Update:Manually_Installing_a_MAR_file>`_
.. [#retr] `README
    <http://ftp.mozilla.org/pub/firefox/releases/latest/README.txt>`_
.. [#locale] The `Locale Codes <https://wiki.mozilla.org/L10n:Locale_Codes>`_
   wiki page describes the scheme - based on :rfc:`5646` - used by Mozilla.

.. rubric:: Footnotes

.. [#emid] the extension ID is available under "extensions" section in
   'about:support'.
