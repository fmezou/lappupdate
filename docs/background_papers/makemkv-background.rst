.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _background_makemkv:

MakeMKV
=======
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

.. sidebar:: MakeMKV

    .. image:: makemkv_logo.png
        :align: center
        :height: 83

    Published by GuinpinSoft inc, MakeMKV is a video format converter. Its main
    feature is to extract audio and video tracks from a DVD or a BluRay disc
    into `MKV <http://www.matroska.org/>`_ files.

    Download: `Current Release <http://www.makemkv.com/download/>`_

    Web site:  http://www.makemkv.com/

A deployment plan should consider the three following issues:

* making a installation without any user intervention, i.e. making a `silent
  install`
* setting a default configuration in line with your use cases
* distributing security patches, new features or versions

This topic introduces installers features or tools that can be used to deploy
MakeMKV and centrally manage its configuration in small organisations. It also
describes the mechanism used to notify users and distribute updates (security
patches, full version...) and what `lapptrack` uses to track MakeMKV updates.


Deployment Tips
---------------

MakeMKV installer covers the two first issues. The command line option for a
:dfn:`silent install` is ``/S``. See
:ref:`background_makemkv-installer_options` for an overview of the installer
command line options.

All configuration parameters are stored in the cuurent user registry (HKCU)
including the license key, so a schedule task (i.e. when user log on) or an user
action with the following script.

.. topic:: Setting up the MakeMKV user preference

    .. code-block:: winbatch

        reg add HKCU\Software\MakeMKV /v app_Key /t REG_SZ /d "<license key>" /f
        reg add HKCU\Software\MakeMKV /v app_ExpertMode /t REG_DWORD /d 00000001 /f
        reg add HKCU\Software\MakeMKV /v app_DestinationDir /t REG_SZ /d "U:\\Users\\Public\\Videos\\RIP" /f
        reg add HKCU\Software\MakeMKV /v app_PreferredLanguage /t REG_SZ /d "fre" /f
        exit /b 0

MakeMKV are free while program is in beta, so you may use the `temporary beta
key <http://www.makemkv.com/forum2/viewtopic.php?f=5&t=1053&sid=9bdbec1cd06e7a61
150dcf4e65bbc592>`_.


.. _background_makemkv-installer_options:

Installer Options
-----------------

.. include:: nsis_installer_common_option.txt


Update Mechanism
----------------

In `this post <http://www.makemkv.com/forum2/viewtopic.php?f=1&t=4363>`_, the
MakeMKV author give a method to detect the up-to-date version. It based on a XML
file matching the `PAD 3.10 Specification <http://pad.asp-software.org/spec/
spec_310.php>`_ at http://www.makemkv.com/makemkv.xml.

.. topic:: Example

    .. code-block:: xml

        <?xml version="1.0" encoding="UTF-8"?>
        <XML_DIZ_INFO>
        <MASTER_PAD_VERSION_INFO>
        <MASTER_PAD_VERSION>3.10</MASTER_PAD_VERSION>
        </MASTER_PAD_VERSION_INFO>
        <Company_Info>
        <Company_Name>GuinpinSoft inc</Company_Name>
        <Company_WebSite_URL>http://www.makemkv.com</Company_WebSite_URL>
        ...
        <File_Size_Bytes>6291456</File_Size_Bytes>
        <File_Size_K>6144</File_Size_K>
        <File_Size_MB>6</File_Size_MB>
        ...
        <Program_Name>MakeMKV</Program_Name>
        <Program_Version>1.9.8</Program_Version>
        <Program_Release_Year>2015</Program_Release_Year>
        <Program_Release_Month>12</Program_Release_Month>
        <Program_Release_Day>20</Program_Release_Day>
        ...
        <Web_Info>
        <Application_URLs>
        <Application_Info_URL>http://www.makemkv.com</Application_Info_URL>
        <Application_Order_URL>http://www.makemkv.com/buy</Application_Order_URL>
        ...
        <Application_Icon_URL>
            http://www.makemkv.com/images/mkv_icon.png
        </Application_Icon_URL>
        <Download_URLs>
            <Primary_Download_URL>
                http://www.makemkv.com/download/Setup_MakeMKV_v1.9.8.exe
            </Primary_Download_URL>
            <Secondary_Download_URL>
                http://www.makemkv.com/download/makemkv_v1.9.8_osx.dmg
            </Secondary_Download_URL>
            <Additional_Download_URL_1>
                http://www.makemkv.com/download/makemkv-bin-1.9.8.tar.gz
            </Additional_Download_URL_1>
            <Additional_Download_URL_2>
                http://www.makemkv.com/download/makemkv-oss-1.9.8.tar.gz
            </Additional_Download_URL_2>
        </Download_URLs>
        ...
        </XML_DIZ_INFO>

At startup, MakeMKV downloads a GZIP compressed file named
``makemkv.pad.gz`` at http://www.makemkv.com/makemkv.pad.gz?a=7. This archive
contains only one file (makemkv.pad), which is a PAD too but poorest than the
file above.