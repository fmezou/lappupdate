#######
Read-Me
#######
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

********
About...
********
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

* *lappdeploy* deploys application

* *lapptrack* one checks and downloads applications updates if any (or the full
  installation package)

The *lapptrack* is written only in Python, and it composed of several
components. The main component is a script (*lapptrack*) in charge of the
user interface (in text mode), plug-in handling and operations scheduling. The
bulk of the *lapptrack* part consists of a collection of python modules grouped
in a package (*cots*). Each of these modules tracks a *product* based
on the editor's information sources and fetches the updates.

The *lappdeploy* part is written in `command shell`_ and `windows script`_.

.. _freenas: <http://www.freenas.org/>
.. _OCS Inventory NG: <http://www.ocsinventory-ng.org/en/>
.. _Samba configured in domain controller mode:
    <https://wiki.samba.org/index.php/Samba_AD_DC_HOWTO
.. _Avast Software Updater: <https://www.avast.com/f-software-updater>
.. _FileHippo App Manager: <http://filehippo.com/download_app_manager>

******
Get it
******

* `Documentation <http://fmezou.github.io/lappupdate/develop/docs/index.html>`_
* `Release 0.3.0 (in development) <http://fmezou.github.io/lappupdate/develop/
  release/lappupdate-develop.zip>`_

********
Features
********
The requirements for this project were:

* *lappdeploy* run on Microsoft Windows (7 minimum) without prerequisites (i.e.
  no agent must be prior installed). Theses implies that theses modules must be
  written in `Command shell`_ or `Windows Script Host`_.

* *lappdeploy* run from a network share (aka from a UNC path) or a removable
  disk (CD or DVD, USB stick...).

* *lappdeploy* work with any type of installation package (MSI package, EXE
  package or a classic distribution with files and a setup.exe).

* *lappdeploy* have pre install and post installation hook to customize the
  start menu or install additional packs (e.g. Firefox extension, VirtualBox
  Extension Pack, Tortoise Language Pack...)

.. _Command shell: https://technet.microsoft.com/en-us/library/cc754340.aspx
   #BKMK_OVR
.. _Windows Script Host: https://msdn.microsoft.com/library/d1wf56tt.aspx
.. _Windows Script: https://technet.microsoft.com/en-us/library/cc784547%28v=
   ws.10%29.aspx

