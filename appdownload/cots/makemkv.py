"""
This module is the product handler of `MakeMKV <http://www.makemkv.com/>`_ from
GuinpinSoft inc. The `user manual`_ details information about it.


Public Classes
==============
This module has only one public class.

===================================  ===================================
:class:`Product`                     ..
===================================  ===================================


.. _user manual: http://fmezou.github.io/lappupdate/lappupdate_wiki.html#MakeMKV
"""


import datetime
import logging
import re
from html.parser import HTMLParser


from cots import core
from cots import pad
from cots import semver


__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "Product"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Product(core.BaseProduct):
    """
    MakeMKV product handler.

    This concrete class implements the tracking mechanism for the MakeMKV
    product. So most of information are in the :mod:`core` and more particularly
    in the `BaseProduct` class documentation. The information blow focuses on
    the added value of this class.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `_get_description`                   `_get_release_note`
        `_get_display_name`                  `_get_silent_inst_args`
        `_get_editor`                        `_get_std_inst_args`
        `_get_file_size`                     `_get_target`
        `_get_hash`                          `_get_url`
        `_get_icon`                          `_get_version`
        `_get_name`                          `_parse_catalog`
        `_get_published`                     ..
        ===================================  ===================================
    """
    def __init__(self):
        super().__init__()

        # At this point, only name and catalog url are known.
        # All others attributes will be discovered during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "MakeMKV"
        self._catalog_url = "http://www.makemkv.com/makemkv.xml"
        self._parser = pad.PadParser()

    def is_update(self, product):
        """
        Return if this instance is an update of product.

        This method compare the version of the two product, and return the
        comparison result. The version numbers used by the editor are compliant
        with the semantic versioning specification 2.0.0 (see `cots.semver`
        module)

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: True if this instance is an update of the product specified
                by the `product` parameter.

        Raises:
            TypeError: Parameters type mismatch.
        """
        # check parameters type
        if not isinstance(product, Product):
            msg = "product argument must be a class 'makemv.Product'. not {0}"
            msg = msg.format(product.__class__)
            raise TypeError(msg)

        # comparison based on version number.
        result = False
        if semver.SemVer(self.version) > semver.SemVer(product.version):
            result = True
            msg = "A new version exist ({})."
            _logger.debug(msg.format(self.version))
        else:
            msg = "No new version available."
            _logger.debug(msg)
        return result

    def _parse_catalog(self, filename):
        """
        Parse the catalog.

        This method parses the downloaded product catalog to prepare
        ``_get_...`` methods call. This catalog is a PAD File (see
        `cots.pad` module).

        Parameters
            filename (str): The local name of the downloaded product catalog.

        Exceptions
            pad.SpecSyntaxError: PAD spec file is erroneous.
            pad.PADSyntaxError: A tag in a PAD file don't match the PAD Specs.
         """
        self._parser.parse(filename)

    def _get_name(self):
        """
        Extract the name of the product (used in a_report mail and log file).
        """
        self.name = None
        path = "Program_Info/Program_Name"
        item = self._parser.find(path)
        if item is not None:
            self.name = item.text
            msg = "Product name :'{0}'"
            _logger.debug(msg.format(self.name))
        else:
            msg = "Unknown product name"
            _logger.warning(msg)

    def _get_display_name(self):
        """
        Extract the name of the product as it appears in the 'Programs and
        Features' control panel.

        This name is built from the name and the version attribute, thus this
        method must be called after `_get_name` and `_get_version`.
        """
        name = "{} v{}"
        self.display_name = name.format(self.name, self.version)

    def _get_version(self):
        """
        Extract the current version of the product from the PAD File.
        """
        self.version = None
        path = "Program_Info/Program_Version"
        item = self._parser.find(path)
        if item is not None:
            self.version = item.text
            msg = "Product version :'{0}'"
            _logger.debug(msg.format(self.version))
        else:
            msg = "Unknown product version"
            _logger.warning(msg)

    def _get_published(self):
        """
        Extract the date of the installer’s publication from the PAD file.
        """
        self.published = None
        path = "Program_Info/Program_Release_Year"
        item = self._parser.find(path)
        if item is not None:
            year = int(item.text)
            path = "Program_Info/Program_Release_Month"
            item = self._parser.find(path)
            if item is not None:
                month = int(item.text)
                path = "Program_Info/Program_Release_Day"
                item = self._parser.find(path)
                if item is not None:
                    day = int(item.text)
                    self.published = datetime.date(year, month, day).isoformat()
                    msg = "Release date :'{0}'"
                    _logger.debug(msg.format(self.published))
                else:
                    msg = "Unknown release day"
                    _logger.warning(msg)
            else:
                msg = "Unknown release month"
                _logger.warning(msg)
        else:
            msg = "Unknown release year"
            _logger.warning(msg)

    def _get_description(self):
        """
        Extract the short description of the product (~250 characters).
        """
        self.description = None
        path = "Program_Descriptions/English/Char_Desc_250"
        item = self._parser.find(path)
        if item is not None:
            self.description = item.text
            msg = "Product description :'{0}'"
            _logger.debug(msg.format(self.description))
        else:
            msg = "Unknown product description"
            _logger.warning(msg)

    def _get_editor(self):
        """
        Extract the name of the editor of the product.
        """
        self.editor = None
        path = "Company_Info/Company_Name"
        item = self._parser.find(path)
        if item is not None:
            self.editor = item.text
            msg = "Product editor :'{0}'"
            _logger.debug(msg.format(self.editor))
        else:
            msg = "Unknown product editor"
            _logger.warning(msg)

    def _get_url(self):
        """
        Extract the url of the current version of the installer
        """
        self.url = None
        path = "Web_Info/Download_URLs/Primary_Download_URL"
        item = self._parser.find(path)
        if item is not None:
            self.url = item.text
            msg = "Download url (for windows version) :'{0}'"
            _logger.debug(msg.format(self.url))
        else:
            msg = "Unknown Download url"
            _logger.warning(msg)

    def _get_file_size(self):
        """
        Extract the size of the product installer expressed in bytes
        """
        self.file_size = None
        # path = "Program_Info/File_Info/File_Size_Bytes"
        # item = self._parser.find(path)
        # if item is not None:
        #     self.file_size = int(item.text)
        #     msg = "File size :'{0}'"
        #     _logger.debug(msg.format(self.file_size))
        # else:
        #     msg = "Unknown File size"
        #     _logger.warning(msg)

    def _get_hash(self):
        """
        Extract the secure_hash value of the product installer (tuple).

        The PAD file doesn't specify a secure_hash for the installer product.
        """
        self.secure_hash = None

    def _get_icon(self):
        """
        Extract the name of the icon file.
        """
        self.icon = None
        path = "Web_Info/Application_URLs/Application_Icon_URL"
        item = self._parser.find(path)
        if item is not None:
            self.icon = item.text
            msg = "Icon file :'{0}'"
            _logger.debug(msg.format(self.icon))
        else:
            msg = "Unknown icon"
            _logger.warning(msg)

    def _get_target(self):
        """
        Extract the target architecture type (the Windows’ one).
        """
        self.target = core.PROD_TARGET_UNIFIED
        msg = "Target :'{0}'"
        _logger.debug(msg.format(self.icon))

    def _get_release_note(self):
        """
        Extract the release note’s URL from the PAD File.
        """
        self.release_note = "http://www.makemkv.com/download/history.html"

        # TODO: remove reading from a file
        # url="http://www.makemkv.com/download/history.html"
        # local_filename = core.retrieve_tempfile(url)
        local_filename = r".\MakeMKV - Revision history.html"
        # print("History downloaded: '{0}'".format(local_filename))

        parser = ReleaseNotesParser()

        with open(local_filename) as file:
            parser.feed(file.read())

        # os.unlink(local_filename)


        msg = "Release note :'{0}'"
        _logger.debug(msg.format(self.release_note))

    def _get_std_inst_args(self):
        """
        Extract the arguments to use for a standard installation.
        """
        self.std_inst_args = ""
        msg = "Standard installation options :'{0}'"
        _logger.debug(msg.format(self.std_inst_args))

    def _get_silent_inst_args(self):
        """
        Extract the arguments to use for a silent installation.
        """
        self.silent_inst_args = "/S"
        msg = "Silent installation option :'{0}'"
        _logger.debug(msg.format(self.silent_inst_args))


# ex: MakeMKV v1.9.7 ( 5.10.2015 )
# MakeMKV v1.01 build 646
_title_re = re.compile("^MakeMKV v(?P<version>(([0-9]+\.)+([0-9]+)))"
                       "((\s+\(\s*(?P<date>(([0-9]+\.)+([0-9]+)))\s*\))?"
                       "|(\s+build\s+(?P<build>[0-9]+))?)$")


class ReleaseNotesParser(HTMLParser):
    """

    The figure below is the state graph of the parser.

    .. digraph:: parsing

         NULL -> CONTENT [label = <div id=content>];
         CONTENT -> RELEASES_LIST [label = _is_releases_list_beginning];
         CONTENT -> NULL [label = _is_content_ending];
         RELEASES_LIST -> CONTENT [label = _is_releases_list_ending];
         RELEASES_LIST -> RELEASE_ID [label = _is_release_id_beginning];
         RELEASE_ID -> RELEASE_NOTES [label = _is_expected_release];
         RELEASE_ID -> IGNORE [label = _is_unknown_release];
         RELEASE_NOTES -> FETCHING [label = _is_release_notes_beginning];
         FETCHING -> RELEASES_LIST [label = _is_release_notes_ending];
         IGNORE -> IGNORE [label = _is_release_notes_beginning];
         IGNORE -> RELEASES_LIST [label = _is_release_notes_ending];
    """
    # Scheduler's state
    _STATE_NULL = 0
    _STATE_CONTENT = 1
    _STATE_RELEASES_LIST = 2
    _STATE_RELEASE_ID = 3
    _STATE_RELEASE_NOTES = 4
    _STATE_FETCHING = 5
    _STATE_IGNORE =6
    _STATE_NOT_RECORDING = 7

    # Events
    _START_TAG_EVT = 0
    _END_TAG_EVT = 1
    _DATA_EVT = 2

    # todo : make the automate graph considering the approved version (capture delta)

    def __init__(self):
        super().__init__()

        self._state = self._STATE_NULL
        self._ul_count = 0

        self.note = ""

        self._sched_map = {
            self._STATE_NULL: [
                self._null_actuating, [
                    (self._is_content_beginning, self._STATE_CONTENT)
                ]
            ],
            self._STATE_CONTENT: [
                self._null_actuating, [
                    (self._is_releases_list_beginning, self._STATE_RELEASES_LIST),
                    (self._is_content_ending, self._STATE_NULL)
                ]
            ],
            self._STATE_RELEASES_LIST: [
                self._null_actuating, [
                    (self._is_releases_list_ending, self._STATE_CONTENT),
                    (self._is_release_id_beginning, self._STATE_RELEASE_ID)
                ]
            ],
            self._STATE_RELEASE_ID: [
                self._release_id_fetching, [
                    (self._is_expected_release, self._STATE_RELEASE_NOTES),
                    (self._is_unknown_release, self._STATE_IGNORE)
                ]
            ],
            self._STATE_RELEASE_NOTES: [
                self._null_actuating, [
                    (self._is_release_notes_beginning, self._STATE_FETCHING),
                ]
            ],
            self._STATE_FETCHING: [
                self._release_notes_fetching, [
                    (self._is_release_notes_ending, self._STATE_RELEASES_LIST),
                ]
            ],
            self._STATE_IGNORE: [
                self._null_actuating, [
                    (self._is_release_notes_beginning, self._STATE_IGNORE),
                    (self._is_release_notes_ending, self._STATE_RELEASES_LIST),
                ]
            ]
        }
        self._actuating = None
        self._transitions = None
        self._set_state(self._state)

        self._release = ""
        self._release_notes = ""
        self._tag_depth = 0
        self._depth_map = {}
        self._release_id = None

    def _process_event(self, event, data, attributes):
        """
        Process the event

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes (dict):  The attributes of the tag.
        """
        if event == self._START_TAG_EVT:
            self._tag_depth += 1

        for transition, state in self._transitions:
            if transition(event, data, attributes):
                self._actuating(event, data, attributes, first=False, last=True)
                self._set_state(state)
                self._actuating(event, data, attributes, first=True, last=False)
                break
        else:
            self._actuating(event, data, attributes)  # no transition

        if event == self._END_TAG_EVT:
            self._tag_depth -= 1

    def _set_state(self, state):
        """
        Set the state

        Args:
            state (int): The state identifier.
        """
        print("State {} -> {}".format(self._state, state))
        self._actuating = self._sched_map[state][0]
        self._transitions = self._sched_map[state][1]
        self._state = state

    def _null_actuating(self, event, data, attributes,
                        first=False, last=False):
        """
        Null state actuating.

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes (dict):  The attributes of the tag.
            first (boolean, optional): Indicate if it's the first call of the
                actuating function (i.e. just after a state change (see
                `_set_state`) including if it's the same state). False is the
                default.
            last (boolean, optional): Indicate if it's the last call of the
                actuating function (i.e. just before a state change (see
                `_set_state`) including if it's the same state). False is the
                default.
        """
        pass

    def _is_content_beginning(self, event, data, attributes):
        """

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes:  The attributes of the tag.

        Returns:
            bool: True if the transition is verified.
        """
        verified = False

        if event == self._START_TAG_EVT and data == "div":
            if "id" in attributes:
                if attributes["id"] == "content":
                    verified = True
                    self._depth_map["content"] = self._tag_depth

        return verified

    def _is_content_ending(self, event, data, attributes):
        """

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes:  The attributes of the tag.

        Returns:
            bool: True if the transition is verified.
        """
        verified = False

        if event == self._END_TAG_EVT and data == "div":
            if self._depth_map["content"] == self._tag_depth:
                verified = True

        return verified

    def _is_releases_list_beginning(self, event, data, attributes):
        """

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes:  The attributes of the tag.

        Returns:
            bool: True if the transition is verified.
        """
        verified = False

        if event == self._START_TAG_EVT and data == "ul":
            if "class" in attributes:
                if attributes["class"] == "bullets":
                    verified = True
                    self._depth_map["release_list"] = self._tag_depth

        return verified

    def _is_releases_list_ending(self, event, data, attributes):
        """

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes:  The attributes of the tag.

        Returns:
            bool: True if the transition is verified.
        """
        verified = False

        if event == self._END_TAG_EVT and data == "ul":
            if self._depth_map["release_list"] == self._tag_depth:
                verified = True

        return verified

    def _is_release_id_beginning(self, event, data, attributes):
        """

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes:  The attributes of the tag.

        Returns:
            bool: True if the transition is verified.
        """
        verified = False

        if event == self._START_TAG_EVT and data == "li":
            verified = True
            self._depth_map["release_id"] = self._tag_depth
            self._release = ""

        return verified

    def _release_id_fetching(self, event, data, attributes,
                             first=False, last=False):
        """
        Release state actuating.

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes (dict):  The attributes of the tag.
            first (boolean, optional): Indicate if it's the first call of the
                actuating function (i.e. just after a state change (see
                `_set_state`) including if it's the same state). False is the
                default.
            last (boolean, optional): Indicate if it's the last call of the
                actuating function (i.e. just before a state change (see
                `_set_state`) including if it's the same state). False is the
                default.
        """
        if first:
            self._release = ""

        if event == self._DATA_EVT:
            self._release += data

        if last:
            if self._release_id:
                if self._release_id.group("date"):
                    pubdate = self._release_id.group("date").split(".")
                    dt = datetime.date(int(pubdate[2]), int(pubdate[1]),
                                       int(pubdate[0]))
                else:
                    dt = None
                ver_id = self._release_id.group("version").split(".")
                ver = "{}.{}.0".format(int(ver_id[0]), int(ver_id[1]))
                if len(ver_id) == 3:
                    ver = "{}.{}.{}".format(int(ver_id[0]), int(ver_id[1]),
                                            int(ver_id[2]))
                if self._release_id.group("build"):
                    ver += "+{}".format(self._release_id.group("build"))
                version = semver.SemVer(ver)
                print("MakeMKV", version, dt)
            else:
                print("ERROR Unknown MakeMKV")

    def _is_expected_release(self, event, data, attributes):
        """

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes:  The attributes of the tag.

        Returns:
            bool: True if the transition is verified.
        """
        verified = False

        if event == self._END_TAG_EVT and data == "li":
            if self._depth_map["release_id"] == self._tag_depth:
                self._release_id = _title_re.match(self._release)
                if self._release_id:
                    verified = True

        return verified

    def _is_unknown_release(self, event, data, attributes):
        """

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes:  The attributes of the tag.

        Returns:
            bool: True if the transition is verified.
        """
        verified = False

        if event == self._END_TAG_EVT and data == "li":
            if self._depth_map["release_id"] == self._tag_depth:
                self._release_id = _title_re.match(self._release)
                if not self._release_id:
                    verified = True

        return verified

    def _is_release_notes_beginning(self, event, data, attributes):
        """

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes:  The attributes of the tag.

        Returns:
            bool: True if the transition is verified.
        """
        verified = False

        if event == self._START_TAG_EVT and data == "ul":
            if "class" in attributes:
                if attributes["class"] == "bullets2":
                    verified = True
                    self._depth_map["release_notes"] = self._tag_depth

        return verified

    def _release_notes_fetching(self, event, data, attributes,
                                first=False, last=False):
        """
        Release notes state actuating.

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes (dict):  The attributes of the tag.
            first (boolean, optional): Indicate if it's the first call of the
                actuating function (i.e. just after a state change (see
                `_set_state`) including if it's the same state). False is the
                default.
            last (boolean, optional): Indicate if it's the last call of the
                actuating function (i.e. just before a state change (see
                `_set_state`) including if it's the same state). False is the
                default.
        """
        if first:
            self._release_notes = ""

        if event == self._DATA_EVT:
            self._release_notes += data
        elif event == self._START_TAG_EVT:
            self._release_notes += "<{}>".format(data)
        elif event == self._END_TAG_EVT:
            self._release_notes += "</{}>".format(data)

        if last:
            print(self._release_notes)

    def _is_release_notes_ending(self, event, data, attributes):
        """

        Args:
            event (int): The event identifier
            data (str): The tag identifier (i.e. ul) or the text.
            attributes:  The attributes of the tag.

        Returns:
            bool: True if the transition is verified.
        """
        verified = False

        if event == self._END_TAG_EVT and data == "ul":
            if self._depth_map["release_notes"] == self._tag_depth:
                verified = True

        return verified

    def handle_starttag(self, tag, attrs):
        """
        https://docs.python.org/3/library/html.parser.html#html.parser.HTMLParser.handle_starttag
        """
        attributes = {}
        for attr in attrs:
            attributes[attr[0]] = attr[1]
        self._process_event(self._START_TAG_EVT, tag, attributes)

    def handle_endtag(self, tag):
        self._process_event(self._END_TAG_EVT, tag, None)

    def handle_data(self, data):
        self._process_event(self._DATA_EVT, data, None)

    # def handle_comment(self, data):
    #     print("Comment  :", data)
    #
    # def handle_entityref(self, name):
    #     c = chr(name2codepoint[name])
    #     print("Named ent:", c)
    #
    # def handle_charref(self, name):
    #     if name.startswith('x'):
    #         c = chr(int(name[1:], 16))
    #     else:
    #         c = chr(int(name))
    #     print("Num ent  :", c)
    #
    # def handle_decl(self, data):
    #     print("Decl     :", data)

