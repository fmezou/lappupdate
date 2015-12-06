"""Semver  support.

The parser match the semantic versioning specification 2.0.0
(http://semver.org/spec/v2.0.0.html).

Classes
    semver : is the class object to manipulate semver string

Exception
    None.

Function
    None

Constant
    None

"""

import os
import logging
import re


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


class SemVer():
    """SemVer class .

    Public instance variables

    Public methods
        None

    Subclass API variables (i.e. may be use by subclass)

    Subclass API Methods (i.e. must be overwritten by subclass)
    """

    def __init__(self, semver):
        """Constructor

        Parameters
            :param semver: is a string containing the version string matching
            the semver specification. Otherwise a XXX exception raised.
        """

        # To make the module as versatile as possible, an nullHandler is added.
        # see 'Configuring Logging for a Library'
        # docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
        self._logger = logging.getLogger(__name__)
        self._logger.addHandler(logging.NullHandler())
        self._logger.debug("Instance created.")

    def get_major(self):
        """get

        Parameters
            :param semver: is a string containing the version string matching
            the semver specification. Otherwise a XXX exception raised.
        """
        pass

    @property
    def is_pre_release(self):
        """Indicate if the version is a pre-release or not.

        Parameters
            None.

        Exception
            None.

        Returns
            :return: True if the version is a pre-release one.
        """
        return False

    def __eq__(self, *args, **kwargs): # real signature unknown
        """ Return self==value. """
        pass

    def __ge__(self, *args, **kwargs): # real signature unknown
        """ Return self>=value. """
        pass

    def __gt__(self, *args, **kwargs): # real signature unknown
        """ Return self>value. """
        pass

    def __le__(self, *args, **kwargs): # real signature unknown
        """ Return self<=value. """
        pass

    def __lt__(self, *args, **kwargs): # real signature unknown
        """ Return self<value. """
        pass
