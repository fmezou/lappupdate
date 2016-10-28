"""
This module is the product handler of `MakeMKV <http://www.makemkv.com/>`_ from
GuinpinSoft inc. The `makemkv-background` details information about it.


Public Classes
--------------
This module has several public class listed below in alphabetical order.

===================================  ===================================
:class:`Product`                     `ReleaseNotesParser`
===================================  ===================================


.. _user manual: http://fmezou.github.io/lappupdate/lappupdate_wiki.html#MakeMKV
"""


import datetime
import logging
import re
import os
from html.parser import HTMLParser


from cots import core
from support import pad
from support import semver


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
        `get_origin`                         `is_update`
        ===================================  ===================================
    """
    def __init__(self):
        super().__init__()

        # At this point, only the name and the catalog location are known.
        # All others attributes will be discovered during catalog parsing
        # (`get_origin`) and update downloading (`fetch`)
        self.name = "MakeMKV"
        self.target = core.TARGET_UNIFIED

        self.web_site_location = "http://www.makemkv.com/"
        self.announce_location = ""
        self.feed_location = ""
        self.release_note_location = \
            "http://www.makemkv.com/download/history.html"

        self.std_inst_args = ""
        self.silent_inst_args = "/S"

        self._catalog_url = "http://www.makemkv.com/makemkv.xml"
        self._parser = pad.PadParser()

    def get_origin(self, version=None):
        """
        Get product information from the remote repository.

        Args:
            version (str): The version of the reference product (i.e. the
                deployed product). It'a string following the editor versioning
                rules.

        Raises:
            `TypeError`: Parameters type mismatch.
            `pad.SpecSyntaxError`: PAD spec file is erroneous.
            `pad.PADSyntaxError`: A tag in a PAD file don't match the PAD Specs.
       """
        # check parameters type
        if version is not None and not isinstance(version, str):
            msg = "version argument must be a class 'str' or None. not {0}"
            msg = msg.format(version.__class__)
            raise TypeError(msg)

        msg = "Get the latest product information. Current version is '{0}'"
        _logger.debug(msg.format(self.version))

        local_filename = core.retrieve_tempfile(self._catalog_url)
        msg = "Catalog downloaded: '{0}'".format(local_filename)
        _logger.debug(msg)

        # Parse the catalog and retrieve information
        self._parser.parse(local_filename)

        self.name = self._get_field("Program_Info/Program_Name")
        self.version = self._get_field("Program_Info/Program_Version")
        self.display_name = "{} v{}".format(self.name, self.version)
        self._get_published()
        self.description = self._get_field(
            "Program_Descriptions/English/Char_Desc_250")
        self.editor = self._get_field("Company_Info/Company_Name")
        self.location = self._get_field(
            "Web_Info/Download_URLs/Primary_Download_URL")
        self.icon = self._get_field(
            "Web_Info/Application_URLs/Application_Icon_URL")
        self._get_change_summary(version)

        # FIXME: incorrect file size in the PAD File.
        # The PAD file specifies a file size which do not match with the real
        # file size. So -1 (unknown file size) is used.
        # size = self._get_field("Program_Info/File_Info/File_Size_Bytes")
        # if size is not None:
        #     self.file_size = int(size)
        # else:
        #     self.file_size = -1
        self.file_size = -1

        # clean up the temporary files
        os.unlink(local_filename)

    def is_update(self, product):
        """
        Return if this instance is an update of product.

        This method compare the version of the two product, and return the
        comparison result. The version numbers used by the editor are compliant
        with the semantic versioning specification 2.0.0 (see `support.semver`
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

    def _get_published(self):
        """
        Extract the date of the installer’s publication from the PAD file.
        """
        self.published = None
        year = self._get_field("Program_Info/Program_Release_Year")
        month = self._get_field("Program_Info/Program_Release_Month")
        day = self._get_field("Program_Info/Program_Release_Day")
        if year is not None and month is not None and day is not None:
            self.published = \
                datetime.date(int(year), int(month), int(day)).isoformat()
            msg = "Release date :'{0}'"
            _logger.debug(msg.format(self.published))

    def _get_change_summary(self, version=None):
        """
        Extract the release note’s URL from the PAD File.

        Args:
            version (str): The version of the reference product (i.e. the
                deployed product). It'a string following the editor versioning
                rules.
        """
        local_filename = core.retrieve_tempfile(self.release_note_location)
        print("History downloaded: '{0}'".format(local_filename))

        parser = ReleaseNotesParser(version)
        with open(local_filename) as file:
            parser.feed(file.read())

        self.change_summary = "<ul>"
        template = "<li>version {} published on {}</li>{}"
        for i in parser.changelog:
            self.change_summary += template.format(i[0], i[1], i[2])
        self.change_summary += "</ul>"
        os.unlink(local_filename)

        msg = "Change summary :{0}"
        _logger.debug(msg.format(repr(self.change_summary)))

    def _get_field(self, path):
        """
        Get the value from a field in a PAD File.

        Args:
            path (str): The field's path in the PAD file.

        Returns:
            str: Contain the value of the field
        """
        text = None
        item = self._parser.find(path)
        if item is not None:
            text = item.text
            msg = "{} : {}"
            _logger.debug(msg.format(repr(path), repr(text)))
        else:
            msg = "Unknown path ({})"
            _logger.warning(msg.format(repr(path)))

        return text


class ReleaseNotesParser(HTMLParser):
    """
    MakeMKV release notes parser.

    This concrete class parses release notes and extracts notes since the
    deployed version.

    Args:
        version (str): The version of the deployed product. It's a string
            following the editor versioning rules.


    Attributes:
        changelog (list): The changelog of the product since the deployed
            product (see ``version`` argument). It is a list of 3-tuple
            containing, in this order, the version (as a string using the editor
            versioning rules), the date of the installer’s publication (as a
            string using the ISO 8601 format) and the release note (as a string)
            using a simple HTML syntax (nested unordered list) as shown below.

            .. code-block:: html

                <ul>
                <li>Added support for AACS v60</li>
                <li>Small miscellaneous improvements and bugfixes</li>
                </ul>


    **Using ReleaseNotesParser...**
        The main purpose of this class is to parse the `revision history
        <http://www.makemkv.com/download/history.html>`_ and fulfills the
        `changelog` attribute. So the using is limited to create class instance
        and call the :meth:`.feed` method with the content of the revision
        history file.

        Examples
            .. code-block:: python

                from cots.makemkv import ReleaseNotesParser
                parser = ReleaseNotesParser("1.9.8")
                with open(r".\history.html") as file:
                    parser.feed(file.read())
                print(parser.changelog)


    **Inside ReleaseNotesParser...**
        This class is a derived class from `html.parser.HTMLParser` by adding a
        scheduler to parse the HTML content. The figure below is the parser's
        state graph.

        .. digraph:: parsing

             NULL -> CONTENT [label = <div id=content>];
             CONTENT -> RELEASES_LIST [label = _is_releases_list_beginning];
             CONTENT -> NULL [label = _is_content_ending];
             RELEASES_LIST -> CONTENT [label = _is_releases_list_ending];
             RELEASES_LIST -> RELEASE_ID [label = _is_release_id_beginning];
             RELEASE_ID -> RELEASE_NOTES [label = _is_new_release];
             RELEASE_ID -> IGNORE [label = _is_old_or_unknown_release];
             RELEASE_NOTES -> FETCHING [label = _is_release_notes_beginning];
             FETCHING -> RELEASES_LIST [label = _is_release_notes_ending];
             IGNORE -> IGNORE [label = _is_release_notes_beginning];
             IGNORE -> RELEASES_LIST [label = _is_release_notes_ending];
    """
    # Scheduler's state
    _STATE_NULL = "NULL"
    _STATE_CONTENT = "CONTENT"
    _STATE_RELEASES_LIST = "RELEASES_LIST"
    _STATE_RELEASE_ID = "RELEASE_ID"
    _STATE_RELEASE_NOTES = "RELEASE_NOTES"
    _STATE_FETCHING = "FETCHING"
    _STATE_IGNORE = "IGNORE"

    # Events
    _START_TAG_EVT = 0
    _END_TAG_EVT = 1
    _DATA_EVT = 2

    # Regular expression to parse the release identifier.
    # ex: MakeMKV v1.9.7 ( 5.10.2015 )
    # MakeMKV v1.01 build 646
    _title_re = re.compile("^MakeMKV v(?P<version>(([0-9]+\.)+([0-9]+)))"
                           "((\s+\(\s*(?P<date>(([0-9]+\.)+([0-9]+)))\s*\))?"
                           "|(\s+build\s+(?P<build>[0-9]+))?)$")

    def __init__(self, version=None):
        # check parameters type
        if version is not None and not isinstance(version, str):
            msg = "version argument must be a class 'str' or None. not {0}"
            msg = msg.format(version.__class__)
            raise TypeError(msg)

        super().__init__()
        self.changelog = []

        self._state = self._STATE_NULL
        self._ul_count = 0
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
                    (self._is_new_release, self._STATE_RELEASE_NOTES),
                    (self._is_old_or_unknown_release, self._STATE_IGNORE),
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
        self._version = None
        self._published = ""
        if version is not None:
            self._deployed = semver.SemVer(version)
        else:
            self._deployed = semver.SemVer("0.0.0")

        msg = "Instance of {} created."
        _logger.debug(msg.format(self.__class__))

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
            state (str): The state identifier.
        """
        msg = "State {} -> {}"
        _logger.debug(msg.format(self._state, state))

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

    def _is_new_release(self, event, data, attributes):
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
                self._release_id_computing()
                if self._release_id:
                    if self._version > self._deployed:
                        verified = True

        return verified

    def _is_old_or_unknown_release(self, event, data, attributes):
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
                self._release_id_computing()
                if not self._release_id:
                    verified = True
                else:
                    if not (self._version > self._deployed):
                        verified = True

        return verified

    def _release_id_computing(self):
        """
        Release id computing.

        """
        self._release_id = self._title_re.match(self._release)
        if self._release_id:
            if self._release_id.group("date"):
                pubdate = self._release_id.group("date").split(".")
                self._published = datetime.date(int(pubdate[2]),
                                                int(pubdate[1]),
                                                int(pubdate[0]))
            else:
                self._published = None
            ver_id = self._release_id.group("version").split(".")
            ver = "{}.{}.0".format(int(ver_id[0]), int(ver_id[1]))
            if len(ver_id) == 3:
                ver = "{}.{}.{}".format(int(ver_id[0]), int(ver_id[1]),
                                        int(ver_id[2]))
            if self._release_id.group("build"):
                ver += "+{}".format(self._release_id.group("build"))
            self._version = semver.SemVer(ver)

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
            if self._published is not None:
                self.changelog.append(("{}".format(self._version),
                                       self._published.isoformat(),
                                       self._release_notes))
            else:
                self.changelog.append(("{}".format(self._version),
                                       "unknown",
                                       self._release_notes))

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
        attributes = {}
        for attr in attrs:
            attributes[attr[0]] = attr[1]
        self._process_event(self._START_TAG_EVT, tag, attributes)

    def handle_endtag(self, tag):
        self._process_event(self._END_TAG_EVT, tag, {})

    def handle_data(self, data):
        self._process_event(self._DATA_EVT, data, {})
