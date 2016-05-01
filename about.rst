.. _about:

About...
========

This documentation describes data, classes and scripts composing the lAppUpdate
deployment system. It built around two main parts: the first one, named
**appdeploy**, deploys application from a removable media or a shared folder;
the second one, named **appdownload**, tracks and downloads application
installers or its updates.

The **appdeploy** part is written in `command shell`_ and `windows script`_.

The **appdownload** part is written only in Python, and it composed of several
components. The main component is a script (:mod:`appdownload`) in charge of the
user interface (in text mode), plug-in handling and operations scheduling. The
bulk of the appdownload part consists of a collection of python modules grouped
in a package (:mod:`cots`). Each of these modules tracks a :term:`product` based
on the editor's information sources and fetches the updates.

This manual is designed for a *developer audience* to enhance features or to add
plug-in to handle new products.

The `user manual`_ is designed for a *end-user audience* and details use
cases and the configuration files. This manual is available as a single file
based on `TiddlyWiki`_, a unique non-linear notebook.

.. _command shell: https://technet.microsoft.com/en-us/library/cc754340.aspx
    #BKMK_OVR
.. _windows script: https://msdn.microsoft.com/library/d1wf56tt.aspx
.. _user manual: http://fmezou.github.io/lappupdate/lappupdate_wiki.html
.. _TiddlyWiki: http://tiddlywiki.com/#A%20Gentle%20Guide%20to%20TiddlyWiki
