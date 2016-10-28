"""
This module defines functions and classes for a semantic versioning (aka SemVer)
support.

The parser match the `semantic versioning specification`_ 2.0.0.

Public Classes
--------------
This module has only one public class.

===================================  ===================================
`SemVer`                             ..
===================================  ===================================


.. _semantic versioning specification: http://semver.org/spec/v2.0.0.html
"""

import logging
import re


__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "SemVer"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

# Regular expression which match the semantics rules.
# Like the regular expression is fixed, it is compiled at the loading of the
# module to improve the efficiency of the `SemVer` class method.
_sem_re = re.compile("^(?P<major>(?:0|[1-9][0-9]*))"
                     "\.(?P<minor>(?:0|[1-9][0-9]*))"
                     "\.(?P<patch>(?:0|[1-9][0-9]*))"
                     "(\-(?P<pre_release>[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*))?"
                     "(\+(?P<build>[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*))?$",
                     flags=0)


class SemVer:
    """
    SemVer parser class.

    Args:
        version_string (str): The version string matching the `semantic
            versioning specification`_. Otherwise a ValueError exception is
            raised (see `semver.SemVer._parse`).


    Attributes:
        major (property): get the major version number.
        minor (property): get the minor version number.
        patch (property): get the patch version number.
        unstable (property): indicate if the version is unstable.

    **Special Methods**
        This class has a number of special methods, listed below in alphabetical
        order, to make the version comparison.

        ===================================  ===================================
        `__eq__`                             `__ne__`
        `__gt__`                             `__repr__`
        `__lt__`
        ===================================  ===================================

    **Using SemVer...**
        The main purpose of this class is to compute comparison between version
        identifier as described in `semantic versioning specification`_.
        So the using is limited to create class instance with the version
        identifier string and use the comparison operator as shown in the below
        example.

        >>> import appdownload.cots.semver as semver
        >>> v1 = semver.SemVer("1.0.0")
        >>> v2 = semver.SemVer("2.0.0")
        >>> v1 < v2
        True
        >>> v1 = semver.SemVer("1.0.0-alpha")
        >>> v2 = semver.SemVer("1.0.0-beta")
        >>> v1 > v2
        False
        >>> v1 = semver.SemVer("1.0.0")
        >>> v2 = semver.SemVer("1.0.0")
        >>> v1 < v2
        False
        >>> v1 == v2
        True
    """
    def __init__(self, version_string):
        # Default values
        self._version = []
        self._pre_release = []
        self._build = ""
        self._unstable = False

        # Parse the string
        self._parse(version_string)

        msg = "Instance of {} created <- {}."
        _logger.debug(msg.format(self.__class__, version_string))

    @property
    def major(self):
        """
        Get the major version number.

        Return:
            str: The version number with only the major number.
        """
        return str(self._version[0])

    @property
    def minor(self):
        """
        Get the minor version number.

        Return:
            str: The version number with the major and the minor number .
        """
        return str("{}.{}".format(self._version[0], self._version[1]))

    @property
    def patch(self):
        """
        Get the patch version number.

        Return:
            str: The version number with the major, the minor and the patch
                number.
        """
        return str("{}.{}.{}".format(self._version[0],
                                     self._version[1],
                                     self._version[2]))

    @property
    def unstable(self):
        """
        Indicate if the version is unstable.

        Return:
            bool: True if the version is unstable.
        """
        return self._unstable

    def __repr__(self):
        """
        Compute the string representation of the SemVer object.

        Return:
            str: the version string which can be used to recreate the
                SemVer object.
        """
        msg = "'{}.{}.{}".format(self._version[0],
                                 self._version[1],
                                 self._version[2])
        if len(self._pre_release) != 0:
            msg += "-"
            msg += ".".join(self._pre_release)
        if len(self._build) != 0:
            msg += "+"
            msg += self._build
        msg += "'"

        return msg

    def __eq__(self, other):
        """Rich comparison method, return self == other."""
        # check parameters type
        if not isinstance(other, SemVer):
            msg = "right operand argument must be a class 'SemVer'. not {0}"
            msg = msg.format(other.__class__)
            raise TypeError(msg)

        result = False
        cmp = _comp_version(self._version, other._version)
        if cmp == 0:
            cmp = _comp_prerelease(self._pre_release, other._pre_release)
        if cmp == 0:
            result = True

        msg = "{} vs {} -> {}"
        _logger.debug(msg.format(self, other, result))
        return result

    def __ne__(self, other):
        """Rich comparison method, return self != other."""
        result = not self.__eq__(other)
        msg = "{} vs {} -> {}"
        _logger.debug(msg.format(self, other, result))
        return result

    def __gt__(self, other):
        """Rich comparison method, return self > other."""
        # check parameters type
        if not isinstance(other, SemVer):
            msg = "right operand argument must be a class 'SemVer'. not {0}"
            msg = msg.format(other.__class__)
            raise TypeError(msg)

        result = False
        cmp = _comp_version(self._version, other._version)
        if cmp == 0:
            cmp = _comp_prerelease(self._pre_release, other._pre_release)
        if cmp == 1:
            result = True

        msg = "{} vs {} -> {}"
        _logger.debug(msg.format(self, other, result))
        return result

    def __lt__(self, other):
        """Rich comparison method, return self < other."""
        # check parameters type
        if not isinstance(other, SemVer):
            msg = "right argument must be a class 'SemVer'. not {0}"
            msg = msg.format(other.__class__)
            raise TypeError(msg)

        result = False
        cmp = _comp_version(self._version, other._version)
        if cmp == 0:
            cmp = _comp_prerelease(self._pre_release, other._pre_release)
        if cmp == -1:
            result = True

        msg = "{} vs {} -> {}"
        _logger.debug(msg.format(self, other, result))
        return result

    def _parse(self, version_string):
        """
        Parse the version string.

        Args:
            version_string (str): The version string matching the `semantic
                versioning specification`_. Otherwise a ValueError exception is
                raised.
        """
        # check parameters type
        if not isinstance(version_string, str):
            msg = "version_string argument must be a class 'str'. not {0}"
            msg = msg.format(version_string.__class__)
            raise TypeError(msg)

        match = _sem_re.match(version_string)
        if match is None:
            msg = "{} is not a valid version string as described in the " \
                  "specification."
            msg = msg.format(version_string)
            raise ValueError(msg)

        self._version.append(int(match.group("major")))
        self._version.append(int(match.group("minor")))
        self._version.append(int(match.group("patch")))
        msg = "{} -> Major:{}, Minor:{}, Patch:{}"
        _logger.debug(msg.format(version_string,
                                 self._version[0],
                                 self._version[1],
                                 self._version[2]))
        if self._version[0] == 0:
            self._unstable = True
            msg = "{} -> Major version is zero, it's an unstable version."
            _logger.debug(msg.format(version_string))

        pre_release = match.group("pre_release")
        if pre_release is not None:
            self._unstable = True
            self._pre_release = pre_release.split(".")
            msg = "{} -> Pre-release:{}, it's an unstable version."
            _logger.debug(msg.format(version_string, self._pre_release))

        build = match.group("build")
        if build is not None:
            self._build = build
            msg = "{} -> Build metadata:{}, it will be ignored."
            _logger.debug(msg.format(version_string, self._build))


def _comp_version(version1, version2):
    """
    Compare two version identifiers limited to the major, minor and patch fields.

    The rule #11 specify the precedence rules for comparing version identifiers
    (i.e. ``1.0.0 < 2.0.0 < 2.1.0 < 2.1.1``).

    Args:
        version1 (list): The list of fields from the version string,
            constituted by only ASCII digits [0-9], as that order: major, minor,
            patch.
        version2 (list): same as ``version1``.

    Return:
        int: -1, 0 or 1 as below

            * -1: ``version1`` is lower than ``version2``
            * 0: ``version1`` is equal to ``version2``
            * 1: ``version1`` is greater than ``version2``
    """
    # check parameters type
    if not isinstance(version1, list):
        msg = "version1 argument must be a class 'list'. not {0}"
        msg = msg.format(version1.__class__)
        raise TypeError(msg)
    if not isinstance(version2, list):
        msg = "version2 argument must be a class 'list'. not {0}"
        msg = msg.format(version2.__class__)
        raise TypeError(msg)

    # comparison of each field of the pre-release version
    result = 0
    for i in range(3):
        cmp = version1[i] - version2[i]
        if cmp != 0:
            if cmp < 0:
                result = -1
            elif cmp > 0:
                result = 1
            break

    return result


def _comp_prerelease(prerelease1, prerelease2):
    """
    Compare two pre-release version identifiers.

    The rule #11 specify the precedence rules for comparing pre-release version
    identifiers (i.e. 1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta < 1.0.0-beta.2
    < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0).

    Args:
        prerelease1 (list): The list of fields from the pre-release
            identifier, constituted by only ASCII alphanumerics and
            hyphen [0-9A-Za-z-]. The list may be empty.
        prerelease2 (list): Same as ``prerelease1``.

    Return:
        int: -1, 0 or 1 as below

            * -1: ``prerelease1`` is lower than ``prerelease2``
            * 0: ``prerelease1`` is equal to ``prerelease2``
            * 1: ``prerelease1`` is greater than ``prerelease2``
    """
    # check parameters type
    if not isinstance(prerelease1, list):
        msg = "prerelease1 argument must be a class 'list'. not {0}"
        msg = msg.format(prerelease1.__class__)
        raise TypeError(msg)
    if not isinstance(prerelease2, list):
        msg = "prerelease2 argument must be a class 'list'. not {0}"
        msg = msg.format(prerelease2.__class__)
        raise TypeError(msg)

    # comparison of each field of pre-release version identifiers.
    result = 0
    if len(prerelease1) == 0 and len(prerelease2) == 0:
        pass
    elif len(prerelease1) == 0:
        result = 1
    elif len(prerelease2) == 0:
        result = -1
    else:
        for i in range(min(len(prerelease1), len(prerelease2))):
            field1, field2 = prerelease1[i], prerelease2[i]
            result = _compstr(field1, field2)
            if result != 0:
                break
        else:
            cmp = len(prerelease1) - len(prerelease2)
            if cmp < 0:
                result = -1
            elif cmp > 0:
                result = 1

    return result


def _compstr(string1, string2):
    """
    Compare two string either numerically or lexically.

    If the two string are constituted of only digits, there are compared
    numerically and strings with letters or hyphens are compared lexically
    in ASCII sort order. So numeric string always have lower precedence than
    non-numeric string.

    Example:
        | '2' < '11'``
        | 'ab' < 'abc', 'ab' < 'ac', 'AC' < 'ac'
        | '12' < 'abc'

    Args:
        string1 (str): A string constituted by only ASCII alphanumerics and
            hyphen [0-9A-Za-z-].
        string2 (str): Same as ``string1``

    Return:
        int: -1, 0 or 1 as below

            * -1: ``string1`` is lower than ``string2``
            * 0: ``string1`` is equal to ``string2``
            * 1: ``string1`` is greater than ``string1``
    """
    # check parameters type
    if not isinstance(string1, str):
        msg = "string1 argument must be a class 'str'. not {0}"
        msg = msg.format(string1.__class__)
        raise TypeError(msg)
    if not isinstance(string2, str):
        msg = "string2 argument must be a class 'str'. not {0}"
        msg = msg.format(string2.__class__)
        raise TypeError(msg)

    # comparison
    result = 0
    if string1.isdigit() and string2.isdigit():
        # numerical comparison
        cmp = int(string1) - int(string2)
        if cmp < 0:
            result = -1
        elif cmp > 0:
            result = 1
    else:  # lexical comparison
        if string1 < string2:
            result = -1
        elif string1 > string2:
            result = 1

    return result
