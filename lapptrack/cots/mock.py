"""
This module is a mocking product handler to test the `lapptrack` module or any
python module using the `cots` package.

This module differs from the dummy module, because the latter exists as an
example (more precisely as a skeleton) to implement a product handler.


Public Classes
--------------
This module has one public class listed below.

===================================  ===================================
:class:`MockHandler`                 ..
===================================  ===================================

"""


import datetime
import logging
import os
import os.path
import json


from cots import core


__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "MockHandler"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

# Global variables
scripts_fname = "mock.json"
"""
Filename of the script. The topic '`background_mock-script`' details the
content of theses scripts.

The default value is: ``mock.json`` located in the same directory than the
module.
"""
script = "Default"
"""
Name of the current script. The topic '`background_mock-script`' details the
content of theses scripts.

The default value is: ``Default``.
"""


class MockHandler(core.BaseProduct):
    """
    Mocking handler.

    This concrete class implements a handler whose behaviour can be altered by
    a script. This latter is a text file containing python statement. The topic
    '`background_mock-script`' details the content of theses scripts. Most of
    information about handler mechanism are in the :mod:`core` and more
    particularly in the `BaseProduct` class documentation.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `dump`                               `is_update`
        `fetch`                              `load`
        `get_origin`                          ..
        ===================================  ===================================
    """
    def __init__(self):
        super().__init__()

        # load the script file
        # An exception is a non fatal error, the latter are only log.
        # nota: the logger module use the old style format specification.
        self._scripts = {}
        filename = os.path.join(os.path.dirname(__file__), scripts_fname)
        try:
            with open(filename, "r+t") as file:
                self._scripts = json.load(file)
        except FileNotFoundError:
            msg = "Script file '%s' not exist."
            _logger.warning(msg, filename)
        except json.JSONDecodeError as error:
            msg = "Error in script file: %s"
            _logger.error(msg, error)

        # At this point, only the name is set.
        # All others attributes will be set during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "Mocker"

    def load(self, attributes=None):
        """
        Load the saved handler class attributes.

        Args:
            attributes (dict): The instance variables values to set. Previous
                value of the instance variables kept if this argument value is
                None. The key value pairs which don't exist in the
                instance variables dictionary are ignored.

        Raises:
            TypeError: Parameters type mismatch.
        """
        super().load()
        # Execute the additional statement in the context of the current method.
        self.patch("load", globals(), locals())

    def dump(self):
        """
        Dump the handler class attributes.

        The method use a variable named ``attributes`` to store a copy of
        public attributes. The ``attributes`` content may be altered by the
        script.

        Returns:
            dict: Contain a copy of the instance variables values.
        """
        attributes = super().dump()
        # Execute the additional statement in the context of the current method.
        self.patch("dump", globals(), locals())
        return attributes

    def get_origin(self, version=None):
        """
        Get the mocking information.

        Args:
            version (str): The version of the reference product.
        """
        # Execute the additional statement in the context of the current method.
        patched = self.patch("get_origin", globals(), locals())
        if not patched:
            self._default_get_origin(version)

    def fetch(self, path):
        """
        Download the mocking installer.

        Args:
            path (str): The path name where to store the installer package.
        """
        # Execute the additional statement in the context of the current method.
        patched = self.patch("fetch", globals(), locals())
        if not patched:
            self._default_fetch(path)

    def is_update(self, product):
        """
        Return if this instance is an update.

        The method use a variable named ``update`` to store the result of the
        comparison. The ``update`` content may be altered by the script.

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: True if this instance is an update of the product specified
                by the `product` parameter.
        """
        # Execute the additional statement in the context of the current method.
        update = False
        self.patch("fetch", globals(), locals())
        return update

    def _default_get_origin(self, version=None):
        """
        Get the default mocking information.

        Args:
            version (str): The version of the reference product (i.e. the
                deployed product). It'a string following the editor versioning
                rules.
       """
        # check parameters type
        if version is not None and not isinstance(version, str):
            msg = "version argument must be a class 'str' or None. not {0}"
            msg = msg.format(version.__class__)
            raise TypeError(msg)

        # set the instance variables to the default value
        self.target = core.TARGET_UNIFIED
        self.web_site_location = "http://mockapp.example.com"
        self.announce_location = ""
        self.feed_location = ""
        self.release_note_location = \
            "http://mockapp.example.com/history.html"
        self.std_inst_args = ""
        self.silent_inst_args = "/S"

        patch = 0
        if version:
            patch = 1 + int(version.split(".")[2])
        self.version = "1.0.{}".format(patch)
        self.display_name = "{} v{}".format(self.name, self.version)

        dt = (datetime.datetime.now()).replace(microsecond=0)
        self.published = dt.isoformat()

        self.description = "Mocking handler"
        self.editor = "MockApp. Inc"
        self.location = "http://mockapp.example.com/dist.zip"
        self.icon = None
        self.change_summary = \
            "<ul>" \
            "<li>a feature</li>" \
            "<li>Small miscellaneous improvements and bugfixes</li>" \
            "</ul>"
        self.file_size = -1
        self.secure_hash = None

    def _default_fetch(self, path):
        """
        Download the default mocking installer..

        Args:
            path (str): The path name where to store the installer package.
        """
        content = """
        This file is the result of the use of a mocking handler.
        """
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, "mocker.txt")
        with open(filename, mode="w") as file:
            file.writelines(content)
        self._rename_installer(filename)

    def patch(self, name, global_vars, local_vars):
        """
        Execute additional statement from a script.

        Args:
            name (str): The name of the patched method (i.e. the calling method)
            global_vars (dict): The global variables dictionary (see `globals`)
            local_vars (dict): The local variables dictionary (see `locals`).
                This enables local variables to declared and uses in the
                statements defined in a script.

        Returns:
            bool: True if additional statement have been executed.
        """
        # Execute the additional statement in the context of the calling method.
        patched = False
        if script in self._scripts:
            if name in self._scripts[script]:
                if self._scripts[script][name]:
                    patched = True
                    for stmt in self._scripts[script][name]:
                        exec(stmt, global_vars, local_vars)
                        print (local_vars)
        return patched
