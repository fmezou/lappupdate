"""Implementation of Product class for Adobe Flash Player.

Classes
    Product : base class for a product

Exception

Function

Constant

"""


import os
import subprocess
import tempfile

import xml.etree.ElementTree as Et
import urllib.request


from cots import core


class Product(core.BaseProduct):
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
        self._catalog_location = \
            "http://fpdownload.adobe.com/get/flashplayer/current/licensing" \
            "/win/AdobeFlashPlayerCatalog_SCUP.cab"
        self._catalog_name = "AdobeFlashPlayerCatalog_SCUP.xml"
        self._dict = []

    def check_update(self, version=None, modified=None):
        """Checks if a new version is available.

        Parameters
            :param version: version of the currently deployed product.
            :param modified: release date of the currently deployed product.
        """
        local_filename, headers = \
            urllib.request.urlretrieve(self._catalog_location)
        fname = os.path.join(tempfile.gettempdir(), self._catalog_name)
        subprocess.call("expand.exe " + local_filename +
                        " -f:" + self._catalog_name + " " + fname)
        # parse the file
        tree = Et.parse(fname)
        Et.register_namespace("smc",
                              "http://schemas.microsoft.com/sms/2005/04/"
                              "CorporatePublishing/"
                              "SystemsManagementCatalog.xsd")
        Et.register_namespace("bar", 
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/"
                              "BaseApplicabilityRules.xsd")
        Et.register_namespace("bt", 
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/"
                              "BaseTypes.xsd")
        Et.register_namespace("cmd", 
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/Installers/"
                              "CommandLineInstallation.xsd")
        Et.register_namespace("lar", 
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/"
                              "LogicalApplicabilityRules.xsd")
        Et.register_namespace("msi", 
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/Installers/"
                              "MsiInstallation.xsd")
        Et.register_namespace("msiar",
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/"
                              "MsiApplicabilityRules.xsd")
        Et.register_namespace("msp", 
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/Installers/"
                              "MspInstallation.xsd")
        Et.register_namespace("sdp", 
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/"
                              "SoftwareDistributionPackage.xsd")
        Et.register_namespace("usp", 
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/"
                              "UpdateServicesPackage.xsd")
        Et.register_namespace("drv", 
                              "http://schemas.microsoft.com/wsus/2005/04/"
                              "CorporatePublishing/Installers"
                              "/WindowsDriver.xsd")
        Et.register_namespace("xsi", 
                              "http://www.w3.org/2001/XMLSchema-instance")
        root = tree.getroot()
        find = root.findall("{http://schemas.microsoft.com/sms/2005/04/"
                            "CorporatePublishing/SystemsManagementCatalog.xsd}"
                            "SoftwareDistributionPackage")
        for child in find:
            cfind = child.findall("{http://schemas.microsoft.com/wsus/2005/04/"
                                  "CorporatePublishing/"
                                  "SoftwareDistributionPackage.xsd}Properties")
            print("++" + child.tag, child.attrib)
            for cchild in cfind:
                print("+++++"+cchild.tag, cchild.attrib)
        print(local_filename)
        print(fname)
        os.remove(fname)
        urllib.request.urlcleanup()
