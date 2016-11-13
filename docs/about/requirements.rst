.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _about_requirements:

Requirements
============
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

The requirements for this project were:

* :command:`lappdeploy` must run on Microsoft Windows (7 minimum) without
  prerequisites (i.e. no agent must be prior installed). Theses implies that
  theses modules must be written in `Command shell`_ or `Windows Script Host`_.

* :command:`lappdeploy``lappdeploy` must run from a network share (aka from a
  UNC path) or a removable disk (CD or DVD, USB stick...).

* :command:`lappdeploy``lappdeploy` must work with any type of installation
  package (MSI package, EXE package or a classic distribution with files and a
  setup.exe).

* :command:`lappdeploy``lappdeploy` must have pre install and post installation
  hook to customize the start menu or install additional packs (e.g. Firefox
  extension, VirtualBox Extension Pack, Tortoise Language Pack...)
