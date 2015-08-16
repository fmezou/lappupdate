"""Implementation of Product class for Adobe Flash Player

Classes
    Product : base class for a product

Exception

Function

Constant

"""


import os
import subprocess
import tempfile

import xml.etree.ElementTree as ET
import urllib.request


from cots import core


class AdobeFlashPlayer(core.Product):
    """Adobe Flash Player derived Product class.

    Public instance variables
        .

    Public methods
        None

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None

    """
    def __init__(self):
        """Constructor

        Parameters
            None
        """
        super().__init__()
        self._catalog_location=\
            "http://fpdownload.adobe.com/get/flashplayer/current/licensing/win/" \
            "AdobeFlashPlayerCatalog_SCUP.cab"
        self._catalog_name = "AdobeFlashPlayerCatalog_SCUP.xml"
        self._dict = []

    def check_update(self, version=None, modified=None):
        """checks if a new version is available

        Parameters
            version: version of the currently deployed product.
            modified: release date of the currently deployed product.
        """
        local_filename, headers = urllib.request.urlretrieve(self._catalog_location)
        fname = os.path.join(tempfile.gettempdir(), self._catalog_name)
        subprocess.call("expand.exe "+local_filename+" -f:"+self._catalog_name+" "+fname)
        # parse the file
        tree = ET.parse(fname)
        qname=ET.QName("http://schemas.microsoft.com/sms/2005/04/CorporatePublishing/SystemsManagementCatalog.xsd")
        ET.register_namespace("smc",
                              "http://schemas.microsoft.com/sms/2005/04/"
                              "CorporatePublishing/SystemsManagementCatalog.xsd")
        ET.register_namespace("bar", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/BaseApplicabilityRules.xsd")
        ET.register_namespace("bt", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/BaseTypes.xsd")
        ET.register_namespace("cmd", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/Installers/CommandLineInstallation.xsd")
        ET.register_namespace("lar", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/LogicalApplicabilityRules.xsd")
        ET.register_namespace("msi", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/Installers/MsiInstallation.xsd")
        ET.register_namespace("msiar", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/MsiApplicabilityRules.xsd")
        ET.register_namespace("msp", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/Installers/MspInstallation.xsd")
        ET.register_namespace("sdp", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/SoftwareDistributionPackage.xsd")
        ET.register_namespace("usp", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/UpdateServicesPackage.xsd")
        ET.register_namespace("drv", "http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/Installers/WindowsDriver.xsd")
        ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root = tree.getroot()
        find=root.findall("{http://schemas.microsoft.com/sms/2005/04/CorporatePublishing/SystemsManagementCatalog.xsd}SoftwareDistributionPackage")
        for child in find:
            cfind=child.findall("{http://schemas.microsoft.com/wsus/2005/04/CorporatePublishing/SoftwareDistributionPackage.xsd}Properties")
            print("++"+child.tag, child.attrib)
            for cchild in cfind:
                print("+++++"+cchild.tag, cchild.attrib)
        print(local_filename)
        print(fname)
        os.remove(fname)
        urllib.request.urlcleanup()



class AdobeFlashPlayerActiveX(AdobeFlashPlayer):
    """Adobe Flash Player for Internet Explorer edition derived Product class.

    Public instance variables
        name: name of the product
        version: current version of the product
        modified: modification date of the installer
        filename: filename of the installer (full path)
        inst_args: arguments to do a standard installation.
        silent_inst_arg: arguments to do a silent installation.

    Public methods
        None

    """
    _TITLE = "Adobe Flash Player"
    _PRODUCT_NAME = "Adobe Flash Player 32-bit/64-bit ActiveX"
    _DISPLAY_NAME = "Adobe Flash Player %n ActiveX"
    pass


class AdobeFlashPlayerPlugIn(AdobeFlashPlayer):
    """Adobe Flash Player Plug-in derived Product class.

    Public instance variables
        name: name of the product
        version: current version of the product
        modified: modification date of the installer
        filename: filename of the installer (full path)
        inst_args: arguments to do a standard installation.
        silent_inst_arg: arguments to do a silent installation.

    Public methods
        None

    """
    _TITLE = "Adobe Flash Player"
    _PRODUCT_NAME = "Adobe Flash Player 32-bit/64-bit Plugin"
    _DISPLAY_NAME = "Adobe Flash Player %n NAPI"
    pass
