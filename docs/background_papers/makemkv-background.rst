.. Set the default domain and role, for limiting the markup overhead.
.. default-domain:: py
.. default-role:: any

.. _background_makemkv:

MakeMKV Background
==================
.. sectionauthor:: Frédéric MEZOU <frederic.mezou@free.fr>

Published by GuinpinSoft inc, MakeMKV is your one-click solution to convert
video that you own into free and patents-unencumbered format that can be played
everywhere. MakeMKV is a format converter, otherwise called "transcoder".

Product web site: http://www.makemkv.com/

The following topics give more information about the installation process and
the update mechanism.


MakeMKV Installation
--------------------

The installer is based on the `NSIS <https://sourceforge.net/projects/nsis/>`_
(Nullsoft Scriptable Install System) framework and delivered as a single
executable.


Installer common option
^^^^^^^^^^^^^^^^^^^^^^^

.. include:: nsis_installer_common_option.txt


Silent Installation
^^^^^^^^^^^^^^^^^^^

.. include:: nsis_silent_installers.txt


Deployment Tips
^^^^^^^^^^^^^^^

MakeMKV are free while program is in beta, so you may use the `temporary beta
key <http://www.makemkv.com/forum2/viewtopic.php?f=5&t=1053&sid=9bdbec1cd06e7a61
150dcf4e65bbc592>`_.

The user preferences include the license key, so a schedule task (i.e. when user
log on) or an user action with the following script.

.. topic:: Example

    .. code-block:: winbatch

        reg add HKCU\Software\MakeMKV /v app_Key /t REG_SZ /d "<license key>" /f
        reg add HKCU\Software\MakeMKV /v app_ExpertMode /t REG_DWORD /d 00000001 /f
        reg add HKCU\Software\MakeMKV /v app_DestinationDir /t REG_SZ /d "U:\\Users\\Public\\Videos\\RIP" /f
        reg add HKCU\Software\MakeMKV /v app_PreferredLanguage /t REG_SZ /d "fre" /f
        exit /b 0


MakeMKV Update Mechanism
------------------------

In `this post <http://www.makemkv.com/forum2/viewtopic.php?f=1&t=4363>`_, the
MakeMKV author give a method to detect the up-to-date version. It based on a XML
file matching the `PAD 3.10 Specification <http://pad.asp-software.org/spec/
spec_310.php>`_ at http://www.makemkv.com/makemkv.xml.
Consequently, the update checking mechanism of `lapptrack` use this method.

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

For information at startup, MakeMKV download a GZIP compressed file named
``makemkv.pad.gz`` at http://www.makemkv.com/makemkv.pad.gz?a=7. This archive
contains only one file (makemkv.pad), which is a PAD too but poorest than the
file above.