.. _about:

********
About...
********

History of lAppUpdate
=====================

At the beginning, I searched a way to deploy application for my two personal pc
from a home server (based on `freenas`_). My searches led me to the following
products:

* `OCS Inventory NG`_: it's a good choice for IT professional who manages
  thousands of PC, and an agent must be deployed on every PC.

* Active Directory GPO: you can do this with a Windows Server or a server with
  `Samba configured in domain controller mode`_. The main constraint is that GPO
  only accepts MSI package.

* updaters family (`Avast Software Updater`_, `FileHippo App Manager`_ (formerly
  FileHippo Update Checker)...): theses tools are well designed for home PC
  connected to internet, but they mix the two  following functions (checking the
  availability of updates from the editor web site, checking installed local
  applications). In my point of view, theses function must be separated to
  consider the case where target PC are not connected or the need to centralise
  custom software updates.

So I choose to develop my own deployment system built around two main module:
the first one deploys application; the second one checks and downloads
applications updates if any (or the full installation package).

.. _freenas: <http://www.freenas.org/>
.. _OCS Inventory NG: <http://www.ocsinventory-ng.org/en/>
.. _Samba configured in domain controller mode:
    <https://wiki.samba.org/index.php/Samba_AD_DC_HOWTO
.. _Avast Software Updater: <https://www.avast.com/f-software-updater>
.. _FileHippo App Manager: <http://filehippo.com/download_app_manager>

Requirements
============

The requirements for this project were:

* `lappdeploy` must run on windows 7 without prerequisites (I.e. no agent must
  be prior installed). Theses implies that this modules must be written in
  `Command shell`_ or `Windows Script Host`_.

* `lappdeploy` must run from a network share (aka from a UNC path) or a
  removable disk (CD or DVD, USB stick...).

* `lappdeploy` must work with any type of installation package (MSI package, EXE
  package or a classic distribution with files and a setup.exe).

* `lappdeploy` must have pre install and post installation hook to customize the
  start menu or install additional packs (e.g. Firefox extension, VirtualBox
  Extension Pack, Tortoise Language Pack...)

.. _Command shell: https://technet.microsoft.com/en-us/library/cc754340.aspx
   #BKMK_OVR
.. _Windows Script Host: https://msdn.microsoft.com/library/d1wf56tt.aspx
