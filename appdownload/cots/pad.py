"""
This module defines functions and classes for a lightweight Portable
Application Description (PAD) support.

The parser uses `xml.etree.ElementTree` module, and checks the `PAD 4.0`_
Specification compliance.

Warning:
    the values checking is done only when a file is parsed (i.e. when
    loading a file). When building or modifying a PAD File, no control is done.


Public Classes
--------------
This module has only one public class.

===================================  ===================================
`PadParser`                          ..
===================================  ===================================


Public Exceptions
-----------------
This module has has a number of exceptions listed below in alphabetical order.

===================================  ===================================
`PADSyntaxError`                     `SpecSyntaxError`
===================================  ===================================


.. _PAD 4.0: http://pad.asp-software.org/spec/spec.php
"""

import os
import logging
import re
import xml.etree.ElementTree


__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "PadParser",
    "SpecSyntaxError",
    "PADSyntaxError"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Error(Exception):
    """
    Base class for PADParser exceptions.

    Args:
        message (str, optional): Human readable string describing the exception.

    Attributes:
        message (str): Human readable string describing the exception.
    """
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return self.message


class SpecSyntaxError(Error):
    """
    Raised when spec file is erroneous.

    Args:
        name (str): The name of the missing tag.

    Attributes:
        name (str): The name of the missing tag.
    """
    def __init__(self, name):
        msg = "PAD Specification file is erroneous. Tag '{0}' is missing."
        Error.__init__(self, msg.format(name))
        self.name = name


class PADSyntaxError(Error):
    """
    Raised when a tag in a PAD file don't match the PAD Specs.

    Args:
        name (str): The URL of the fetched file.
        value (int): The value of the erroneous tag.

    Attributes:
        name (str): The URL of the fetched file.
        value (int): The value of the erroneous tag.
    """
    def __init__(self, name, value):
        msg = "PAD file is erroneous. The value ('{1}') of '{0}' tag " \
              "don't match the PAD Specs."
        Error.__init__(self, msg.format(name, value))
        self.name = name
        self.value = value


class PadParser(xml.etree.ElementTree.ElementTree):
    """
    A PAD element hierarchy.

    Args:
        element (xml.etree.ElementTree.ElementTree, optional): Root element node
        file (str, optional): A file handle or file name of an XML file whose
            contents will be used to initialize the tree with.

    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `parse`                              ..
        ===================================  ===================================

    **Using PadParser...**
        This class is a derived class from `xml.etree.ElementTree.ElementTree`,
        and have the same using. Only the
        `xml.etree.ElementTree.ElementTree.parse` has been extended to support
        the PAD specification.
    """
    _PADSPECS_FILENAME = "padspec40.xml"

    def __init__(self, element=None, file=None):
        super().__init__(element, file)

        filename = os.path.join(os.path.dirname(__file__),
                                PadParser._PADSPECS_FILENAME)
        self._specs = xml.etree.ElementTree.parse(filename)
        self._tree = None

        msg = "Instance of {} created."
        _logger.debug(msg.format(self.__class__))

    def parse(self, source, parser=None):
        """
        Load external PAD file into element tree.

        The PAD compliance is done at this time.

        Args:
            source (object): A file name or file object.
            parser (object, optional): An optional parser instance that defaults
                to XMLParser.

        Raises:
            SpecSyntaxError: Spec file is erroneous.
            PADSyntaxError: A tag in a PAD file don't match the PAD Specs

        Return:
            xml.etree.ElementTree.ElementTree: the root element of the
                given source document.
        """
        super().parse(source, parser)

        # Load the PAD Specs (XML)
        root = self._specs.getroot()
        if root.tag != "PAD_Spec":
            raise SpecSyntaxError("PAD_Spec")
        else:
            if root[0].tag != "PAD_Spec_Version":
                raise SpecSyntaxError("PAD_Spec_Version")
            if root[1].tag != "Fields":
                raise SpecSyntaxError("Fields")
            msg = "Supported PAD Spec version : '{0}'".format(root[0].text)
            _logger.info(msg)

            for field in list(root[1]):
                name = field.find("Name")
                path = field.find("Path")
                regex = field.find("RegEx")
                if name is None:
                    raise SpecSyntaxError("Name")
                if path is None:
                    raise SpecSyntaxError("Path")
                if regex is None:
                    raise SpecSyntaxError("RegEx")

                # Check the compliance of each item of the PAD file
                # In PAD Specification, paths include the XML element root
                # (XML_DIZ_INFO). Now this item must be excluded from the path
                # argument of the find method, if it is present, the find
                # failed.
                item = self.find(path.text.split('/', 1)[1])
                if item is not None:
                    if regex.text is not None:
                        result = re.match(regex.text, item.text)
                        if result is not None:
                            msg = "'{0}':'{1}' - OK"
                            _logger.debug(msg.format(path.text, item.text))
                        else:
                            raise PADSyntaxError(item.tag, item.text)
        return self._root
