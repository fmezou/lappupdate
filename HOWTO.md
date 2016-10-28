# How-to

To deploy application, there are two main use cases. The first one is based on
a share network, the second is based on a DVD distribution. These cases have
their own constraints and answer to specific needs. The main advantage to have
a centralised application deploying system is to allow to a system
administrator to have a consistency application park.

_**Note**: If you manage a unique PC connected to Internet, the easiest way is
to let each application managing its own upgrades (automatically or manual
way)._

The use of a network share implies that the pc is connected to a local
network, with an available file server. This use case is recommended for SOHO
application deploying (less than 10 pc) and allows silent installation of
patches or new applications.

The use of a DVD is attractive for use in a standalone and non connected
environment (e.g. Industrial PC or access control management console).

But, these two use cases comply with the following steps:

  1. Tune your environment 
  2. Build the application list to deploy
  3. Build the medium
  4. Deploy applications from a DVD or Network share

# Tune your environment

By default, you have nothing to tune. The default values of environment
variables allows a working with the following features:

  * all action, expect debug one, are only logged in a text file named _lappdeploy.log_ in the `%SystemRoot%` directory (typically _C:\Windows\lappdeploy.log_).
  * the applist files (at least _applist-all.txt_) are stored in the _appstore_ directory located at the same level that the directory containing the lappdeploy script.

If these features do not comply with your need, you must consider tuning the
environment variables. The most efficient way to do that is to use __init__
and __exit__ hook scripts. See ___init__.cmd.example_ and
___exit__.cmd.example_ located in the directory containing the lappdeploy
script. in to have examples.

  * To change the location of applist files and installers packages, you must tune the APP_STORE_DIR environment variable. 
  * To change the level of messages logged, you must tune the LOGLEVEL environment variable.
  * To receive an email with a summary and detailed informations on actions done by lAppUpdate, you must tune the LOGMAIL environment variable, and specifies your account mail configuration in SMTP_SERVER (eventually SMTP_SERVER_PORT), FROM_MAIL_ADDR and TO_MAIL_ADDR environment variables.
  * To run the script in an interactive mode (i.e. following installation actions in real time through the command shell), you must tune the SILENT environment variable.

# Build the application list to deploy

The lappdeploy script uses two applist files to verify which applications were
installed and if it needs to be updated: the first one is named _applist-
all.txt_; the second is named _applist-<set>.txt_ where `<set>` is the
argument passed to lappdeploy on the command line (e.g. `.\lappdeploy dummy`).

_**Note**: applist files may be empty including applist-all.txt._

These files are [text file](http://en.wikipedia.org/wiki/Text_file) complying
with the [Windows
standard](http://en.wikipedia.org/wiki/Text_file#Standard_Windows_.txt_files).
So you can use any text editor (e.g. notepad, notepad++, vim...) to edit them.

The applist topic details the format of these files.

In fact, you can have so much file as you want according to your needs. For
example, you can have an applist file per computer or a set of computer (e.g.
children, purchasing department...). If you use a domain controller, you can
match applist files with your Organisational Units (OU).

By default, the applist files are stored in the _appstore_ directory located
at the same level that the directory containing the lappdeploy script. To
change the location of applist files and installers packages, you must tune
the APP_STORE_DIR environment variable.

## Applications store

A way of making is to store installers into the same directory that applist
files with a separate folder for each product (Mozilla Firefox and its
extension may be considered as one product). It clarifies the installers
organisation and allow to have a __postinstall__ hook script for each of them.

## example

    #appArch; appName; appVersion; appPackage; appArgs
       ; Adobe Reader XI - Français; 11.0.08; %APP_STORE_DIR%\AdobeReader\AdbeRdr11008_fr_FR.exe
    x64; Java 7 Update 67 (64-bit); 7.0.670; %APP_STORE_DIR%\Java\jre-7u67-windows-x64.exe ; /s 
    x86; 7-Zip 9.20; 9.20.00.0; %APP_STORE_DIR%\7-zip\7z920.msi

# Build the medium

The lappdeploy script is designed to be independent from the type of used
media. This can be a network share reached from its UNC name (e.g.
_\\\myserver\share_), a DVD or CD, a USB Stick or any removable media. Thus
the media building is limited to copy files or use your favourite CD/DVD
burner utility.

The medium must contain the directory with installers (see 'How to build the
application list') according to the APP_STORE_DIR environment variable and the
following files from the _lappdeploy_ directory:

  * _lappdeploy.cmd_
  * __appfilter.vbs_
  * __log2mail.vbs_
  * ___exit__.cmd_ _(optional)_
  * ___init__.cmd_ _(optional)_

## example

The below block show a typical file tree for a media of deployment.

    \
    ├───lappdeploy
    │       lappdeploy.cmd
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

he phase of deployment start by calling lappdeploy script from a command
shell. The only argument to pass is the set name according to your
organisation choice (see How to build the application list)

As any installation of program, you must launch the script with administrator
privilege (right click on the command prompt link, and choose `run as
administrator`) .

## example

C:\>d:\lappdeploy\lappdeploy.cmd dummy

# Deploy applications from a Network share

The phase of deployment start by calling lappdeploy script from a command
shell. The only argument to pass is the set name according to your
organisation choice (see How to build the application list)

As any installation of program, you must launch the script with administrator
privilege (right click on the command prompt link, and choose `run as
administrator`) .

To push system integration further, you can call this script from a schedule
task with the sending of an summary mail (see How to tune your environment).

## example

C:>\\\myserver\share\lappdeploy.cmd dummy

* * *

This file was automatically generated by [TiddlyWiki](http://tiddlywiki.com/).

