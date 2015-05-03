# About...
Lightweight application update (`lappupdate`) is a set of scripts to download and deploy application for small lan 
or standalone pc running under Microsoft Windows.

At the beginning, I searched a means to deploy application for my two personal pc from a home server 
(based on [freenas](http://www.freenas.org/)). My searches led me to the following products :

* [OCS Inventory NG](http://www.ocsinventory-ng.org/en/) : it's a good choice for IT professional who manages thousand
 of PC, and a agent must be deployed on every PC.

* Active Directory GPO :  you can do this with a Windows Server or a server with 
[Samba configured in domain controller mode](https://wiki.samba.org/index.php/Samba_AD_DC_HOWTO). The main constraint 
is that GPO accept only MSI package.

So I choose to develop my own deployment system built around two main module : the first one, named `appdeploy`, 
deploy application, the second one, named `appdownload`, check and download the application update if any (or the full
installation package).


#Requirements
The requirements for this project was :

* `appdeploy` must run on windows 7 without prerequisites (I.e. no agent must be prior installed). Theses implies that
 this modules must be written in [Command shell](https://technet.microsoft.com/en-us/library/cc754340.aspx#BKMK_OVR) 
 or [Windows Script Host](https://msdn.microsoft.com/library/d1wf56tt.aspx).
 
* `appdeploy` must run from a network share (aka from a UNC path) or a removable disk (CD or DVD, usb stick...).

* `appdeploy` must work with any type of installation package (MSI package, EXE package or a classic distribution with
 files and a setup.exe).
 
* `appdeploy` must have pre install and post installation hook to customize the start menu or install additional packs 
(Firefox extension, VirtualBox Extension Pack, Tortoise Language Pack...)


#Use case __\<ToBeWrite\>__

> this section will explained a use case detailing the following case : deploy from a DVD, deploy from a network share
 
> * how to tune the environment 

> * how to call appdeploy script in a schedule task

> * how to write a applist file... 


#Usage

## appdeploy

This script launch the installer package of the standard application.

    Usage : appdeploy [set]
        set is the set name, the script use a file named applist-[set].txt which describing
        applications to install.
        all is the default value.
    
    Exit code
        0 : no error
        1 : an error occurred while filtering application
        2 : invalid argument. An argument of the command line is not valid (see Usage)
 
## appdownload   __\<ToBeWrite\>__




