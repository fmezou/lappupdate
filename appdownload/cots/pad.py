"""Lightweight PAD (Portable Application Description) support.

The parser is based on xml.etree.ElementTree module, and match the PAD 4.0
Specification (http://pad.asp-software.org/spec/spec.php).
Warning: the values control is done only when a file is parsed (i.e. when
loading a file). When building or modifying an PAD File, any control is done.

Classes
    PadParser : A PAD element hierarchy

Exception
    SpecSyntaxError: Raised when spec file is erroneous.
    PADSyntaxError: Raised when a tag in a PAD file don't matched the PAD Specs

Function
    None

Constant
    None

"""

import os
import logging
import re
import xml.etree.ElementTree


class Error(Exception):
    """Base class for PADParser exceptions."""

    def __init__(self, message=""):
        """Constructor.

        Parameters
            :param message: is the message explaining the reason of the
            exception raise.
        """
        self.message = message

    def __str__(self):
        return self.message


class SpecSyntaxError(Error):
    """Raised when spec file is erroneous."""

    def __init__(self, name):
        """Constructor.

        Parameters
            :param name: name of the missing tag.
        """
        msg = "PAD Specification file is erroneous. Tag '{0}' is missing."
        Error.__init__(self, msg.format(name))
        self.name = name


class PADSyntaxError(Error):
    """Raised when a tag in a PAD file don't matched the PAD Specs."""

    def __init__(self, name, value):
        """constructor.

        Parameters
            :param name: is the name of the erroneous tag.
            :param value: is the value of the erroneous tag
        """
        msg = "PAD file is erroneous. The value ('{1}') of '{0}' tag " \
              "don't match the PAD Specs."
        Error.__init__(self, msg.format(name, value))
        self.name = name
        self.value = value


class PadParser(xml.etree.ElementTree.ElementTree):
    """A PAD element hierarchy.

    Public instance variables

    Public methods
        None

    Subclass API variables (i.e. may be use by subclass)

    Subclass API Methods (i.e. must be overwritten by subclass)
    """
    _PADSPECS_FILENAME = "padspec40.xml"

    def __init__(self, element=None, file=None):
        """Constructor

        Parameters
            :param element: is an optional root element node,
            :param file: is an optional file handle or file name of an XML
            file whose contents will be used to initialize the tree with.
        """
        super().__init__(element, file)
        filename = os.path.join(os.path.dirname(__file__),
                                PadParser._PADSPECS_FILENAME)
        self._specs = xml.etree.ElementTree.parse(filename)
        self._tree = None

        # To make the module as versatile as possible, an nullHandler is added.
        # see 'Configuring Logging for a Library'
        # docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
        self._logger = logging.getLogger(__name__)
        self._logger.addHandler(logging.NullHandler())
        self._logger.debug("Instance created.")

    def parse(self, source, parser=None):
        """Load external PAD file into element tree.

        The PAD compliance is done at this time.

        Parameters
            :param source: is a file name or file object.
            :param parser: is an optional parser instance that defaults
            to XMLParser.

        Exception
            :exception ParseError: is raised if the parser fails to parse the
            document.

        Returns
            :return: the root element of the given source document.
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
            msg = "PAD Spec version : '{0}'".format(root[0].text)
            self._logger.info(msg)

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
                        if result is None:
                            raise PADSyntaxError(item.tag, item.text)
        return self._root
