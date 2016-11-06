.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

Requirements
============
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>
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
