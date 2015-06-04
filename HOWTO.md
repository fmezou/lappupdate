# How-to

To deploy application, there are two main use cases. The first one is based on
a share network, the second is based on a DVD distribution. These cases have
their own constraints and answer to specific needs. The main advantage to have
a centralised application deploying system is to allow to a system
administrator to have a consistency application park.

The use of a network share implies that the pc is connected to a local
network, with an available file server. This use case is recommended for SOHO
application deploying (less than 10 pc) and allows silent installation of
patches or new applications.

The use of a DVD is attractive for use in a standalone and non connected
environment (e.g. Industrial PC or access control management console).

But, these two use cases comply with the following steps:

  1. [Tune your environment ][1]
  2. [Build the application list to deploy][2]
  3. [Build the medium][3]
  4. Deploy applications from a [DVD][4] or [Network share][5]

# Tune your environment

By default, you have nothing to tune. The default values of [environment
variables][6] allows a working with the following features:

  * all action, expect debug one, are only logged in a text file named in the `%SystemRoot%` directory (typically ).
  * the [applist][7] files (at least ) are stored in the directory located at the same level that the directory containing the [appdeploy][8] script.

If these features do not comply with your need, you must consider tuning the
[environment variables][6]. The most efficient way to do that is to use
[__init__][9] and [__exit__][10] hook scripts. See and located in the
directory containing the [appdeploy][8] script. in to have examples.

  * To change the location of [applist][7] files and installers packages, you must tune the [APP_STORE_DIR][11] environment variable. 
  * To change the level of messages logged, you must tune the [LOGLEVEL][12] environment variable.
  * To receive an email with a summary and detailed informations on actions done by lAppUpdate, you must tune the [LOGMAIL][13] environment variable, and specifies your account mail configuration in [SMTP_SERVER][14] (eventually [SMTP_SERVER_PORT][15]) and [SYSADM_TO_ADDR][16] environment variables.
  * To run the script in an interactive mode (i.e. following installation actions in real time through the command shell), you must tune the [SILENT][17] environment variable.

# Build the application list to deploy

The [appdeploy][8] script uses two [applist][7] files to verify which
applications were installed and if it needs to be updated: the first one is
named and **must be exist** even if it is empty; the second is named where
`<set>` is the argument passed to appdeploy on the command line (e.g.
`.\appdeploy dummy`).

These files are [text file][18] complying with the [Windows standard][19]. So
you can use any text editor (e.g. notepad, notepad++, vim...) to edit them.

The [applist topic][7] details the format of these files.

In fact, you can have so much file as you want according to your needs. For
example, you can have an [applist][7] file per computer or a set of computer
(e.g. children, purchasing department...). If you use a domain controller, you
can match [applist][7] files with your Organisational Units (OU).

By default, the [applist][7] files are stored in the directory located at the
same level that the directory containing the [appdeploy][8] script. To change
the location of [applist][7] files and installers packages, you must tune the
[APP_STORE_DIR][11] environment variable.

## Applications store

A way of making is to store installers into the same directory that
[applist][7] files with a separate folder for each product (Mozilla Firefox
and its extension may be considered as one product). It clarifies the
installers organisation and allow to have a [__postinstall__][20] [hook
script][21] for each of them.

## example

    #appArch; appName; appVersion; appPackage; appArgs
       ; Adobe Reader XI - Français; 11.0.08; %APP_STORE_DIR%\AdobeReader\AdbeRdr11008_fr_FR.exe
    x64; Java 7 Update 67 (64-bit); 7.0.670; %APP_STORE_DIR%\Java\jre-7u67-windows-x64.exe ; /s 
    x86; 7-Zip 9.20; 9.20.00.0; %APP_STORE_DIR%\7-zip\7z920.msi

# Build the medium

The [appdeploy][8] script is designed to be independent from the type of used
media. This can be a network share reached from its UNC name (e.g. ), a DVD or
CD, a USB Stick or any removable media. Thus the media building is limited to
copy files or use your favourite CD/DVD burner utility.

The medium must contain the directory with installers (see '[How to build the
application list][2]') according to the [APP_STORE_DIR][11] environment
variable and the following files from the directory:

  *   *   *   * _(optional)_
  * _(optional)_

## example

The below block show a typical file tree for a media of deployment.

    \
    ├───appdeploy
    │       appdeploy.cmd
    │       _appfilter.vbs
    │       _log2mail.vbs
    │       __exit__.cmd
    │       __init__.cmd
    │       
    └───appstore
        │   applist-all.txt
        │   applist-dummy.txt
        │   
        ├───dummy
        │       aninstaller.cmd
        │       aninstaller.msi
        │              
        └───extended dummy
                aninstaller.cmd
                __postinstall__.cmd

# Deploy applications from a DVD

he phase of deployment start by calling [appdeploy][8] script from a command
shell. The only argument to pass is the set name according to your
organisation choice (see [How to build the application list][2])

As any installation of program, you must launch the script with administrator
privilege (right click on the command prompt link, and choose `run as
administrator`) .

## example

C:\>d:\appdeploy\appdeploy.cmd dummy

# Deploy applications from a Network share

The phase of deployment start by calling [appdeploy][8] script from a command
shell. The only argument to pass is the set name according to your
organisation choice (see [How to build the application list][2])

As any installation of program, you must launch the script with administrator
privilege (right click on the command prompt link, and choose `run as
administrator`) .

To push system integration further, you can call this script from a schedule
task with the sending of an summary mail (see [How to tune your
environment][1]).

## example

C:>\\myserver\share\appdeploy.cmd dummy

* * *

This file was automatically generated by [TiddlyWiki][22].

   [1]: #How%20to%20tune%20your%20environment
   [2]: #How%20to%20build%20the%20application%20list
   [3]: #How%20to%20build%20the%20medium
   [4]: #How%20to%20deploy%20from%20a%20DVD
   [5]: #How%20to%20deploy%20through%20a%20network
   [6]: #Environment%20Variables
   [7]: #applist
   [8]: #appdeploy
   [9]: #__init__
   [10]: #__exit__
   [11]: #APP_STORE_DIR
   [12]: #LOGLEVEL
   [13]: #LOGMAIL
   [14]: #SMTP_SERVER
   [15]: #SMTP_SERVER_PORT
   [16]: #SYSADM_TO_ADDR
   [17]: #SILENT
   [18]: http://en.wikipedia.org/wiki/Text_file
   [19]: http://en.wikipedia.org/wiki/Text_file#Standard_Windows_.txt_files
   [20]: #__postinstall__
   [21]: #Hook%20script
   [22]: http://tiddlywiki.com/

