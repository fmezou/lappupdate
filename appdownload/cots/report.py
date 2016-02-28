"""
This module defines functions and classes which implement a flexible reporting
system for applications and libraries.

Classes
    Report: main class to make and publish report.
    BaseHandler: base class for report publishing.
    MailHandler: send the report by mail.
    FileHandler: write the report in a file.
    StreamHandler: write the report in a stream.

Exceptions
    None

Functions
    None

Constants
    None

"""

import datetime
import email.mime.multipart
import email.mime.text
import email.utils
import io
import logging
import mimetypes
import os
import re
import shutil
import smtplib
import sys
import urllib.parse
import time

__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "Report",
    "BaseHandler",
    "MailHandler", "FileHandler", "StreamHandler"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class Report:
    """
    Main class to make and publish report with the registered handler.

    The report is based on a template using named keyword argument and composed
    of named sections. The module use the `report_template.html` by default. The
    use of the named keyword argument is based on the [string module]
    (https://docs.python.org/3/library/string.html#format-string-syntax).

    Each section starts with a HTML comment and it ends with the start of
    next section or the end of the file. The comment match the following format
    and must be on one line:
    <!-- $lau:<name>$ -->
    `name` MUST comprise only ASCII alphanumerics and hyphen [0-9A-Za-z-] and
    MUST NOT be empty.

    If a named section is not declared in `Report.names`, its contents is added
    to the current section (i.e. no section is created).

    Public class variables
       names: is the list of the well-known named sections in a report template.

    Public instance variables
       None

    Public methods
        load_config: configure the report module from a dictionary.
        set_template: set the report template.
        set_attributes: set the attributes of the report.
        add_handler: add a handler to publish the report.
        add_section: add a section to the report.
        publish: publish the report with the registered handlers
        (see `add_handler`).

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None

    Configuration
        The configuration is detailed in the `report.example.ini` file.
    """
    names = [
        "Head",
        "HeaderStart",
        "Title",
        "HeaderEnd",
        "BodyStart",
        "TOCStart",
        "TOCEntry",
        "TOCEnd",
        "SummaryStart",
        "SummaryEntry",
        "SummaryEnd",
        "BodyEnd",
        "Tail"
    ]

    # Regular expression which match the section name in report templates.
    # Like the regular expression is fixed, it is compiled at the loading of the
    # module to improve the efficiency of the `Report` class method.
    _re = re.compile("^\s*<!--\s+\$lau:(?P<name>[0-9A-Za-z-]+)\$\s+-->$",
                     flags=0)
    _SUMMARY = os.path.join(os.path.dirname(__file__), "report_template.html")

    def __init__(self):
        """
        Constructor

        Parameters
        None
        """
        self._attributes = {}
        self._sections = []
        self._template = {}
        self._subtype = "plain"
        self._charset = "utf-8"
        self._handlers = []
        self._separator = ""

        msg = "Instance of {} created."
        _logger.debug(msg.format(self.__class__))

    def load_config(self, config, append=True):
        """
        Configure the report module from a dictionary.

        :param config: is a dictionary containing the configuration as described
        in the `report.example.ini` file.
        :param append: is a boolean specifying if the current configuration
        will be overwritten by that specified by the `config` parameter.
        """
        # check parameters type
        if not isinstance(config, dict):
            msg = "config argument must be a class 'dict'. not {0}"
            msg = msg.format(config.__class__)
            raise TypeError(msg)
        # check parameters type
        if not isinstance(append, bool):
            msg = "append argument must be a class 'bool'. not {0}"
            msg = msg.format(append.__class__)
            raise TypeError(msg)

        if not append:
            self.__init__()
            self._load_default()

        # Parse the core section
        core = config["core"]
        if "template" in core:
            self.set_template(core["template"], separator="")

        for handler_name in core["handlers"].split(","):
            # Add each specified handler
            # The handler must be declared in this module, because I'am
            # using dynamic creation of instance with the `globals()`
            # function. This way of making avoid using the `exec()` or
            # `eval()` which is a security issue when the input
            # isn't fine controlled.
            handler_name = handler_name.strip()
            handler_params = config[handler_name]
            class_name = handler_name
            if "class" in handler_params:
                class_name = handler_params["class"]
            handler = globals()[class_name]()
            handler.load_config(handler_params)
            self.add_handler(handler)

        # Parse the attributes section if exist
        if "attributes" in config:
            self.set_attributes(config["attributes"])

    def _load_default(self):
        """
        Configure the report module with its default value.
        """
        # use the default template
        self.set_template()
        self.set_attributes()

    def set_template(self, template=_SUMMARY, separator=""):
        """
        Set the report template.

        Parameters
        :param template: is the full path name of the template file. The format
        of the template file is described in the Report class introduction. The
        template named 'report_template.html' is used by default.
        :param separator: is the separator added at the end of each added
        section in the report.
        """
        # check parameters type
        if not isinstance(template, str):
            msg = "template argument must be a class 'str'. not {0}"
            msg = msg.format(template.__class__)
            raise TypeError(msg)

        if not isinstance(separator, str):
            msg = "separator argument must be a class 'str'. not {0}"
            msg = msg.format(separator.__class__)
            raise TypeError(msg)

        self._separator = separator
        self._parse_template(template)

        msg = "Template is set to '{}'."
        _logger.debug(msg.format(template))

    def set_attributes(self, attributes=None):
        """
        Set the attributes of the report.

        Theses attributes are used in the header and tail sections of the
        report (see `Title`, `BodyStart`, `BodyEnd`, `Tail` sections in the
        template)

        :param attributes: is a dictionary containing the attributes.
        """
        # check parameters type
        if attributes is not None and not isinstance(attributes, dict):
            msg = "attributes argument must be a class 'dict'. not {0}"
            msg = msg.format(attributes.__class__)
            raise TypeError(msg)

        # make a copy of the attributes because a date attribute is added
        self._attributes = {}
        if attributes:
            self._attributes = attributes.copy()
        dt = datetime.date.today()
        self._attributes["date"] = dt.isoformat()

        msg = "Report attributes are set to : {}"
        _logger.debug(msg.format(self._attributes))

    def add_handler(self, handler):
        """
        Add a handler to publish the report.

        :param handler: is a class instance derived from the `BaseHandler` base
        class.
        """
        # check parameters type
        if not isinstance(handler, BaseHandler):
            msg = "handler argument must be a class 'BaseHandler'. not {0}"
            msg = msg.format(handler.__class__)
            raise TypeError(msg)

        self._handlers.append(handler)
        msg = "{} added."
        _logger.debug(msg.format(handler.__class__))

    def add_section(self, attributes):
        """
        Add a section to the report.

        Parameters
        :param attributes: is a dictionary containing the product attributes
        (typically the one returned by the `dump` method).
        """
        # check parameters type
        if not isinstance(attributes, dict):
            msg = "attributes argument must be a class 'dict'. not {0}"
            msg = msg.format(attributes.__class__)
            raise TypeError(msg)

        # make a copy of the attributes because a unique identifier is added
        section = attributes.copy()
        section["id"] = str(id(section))
        self._sections.append(section)

        msg = "A new section was added and attributes are : {}"
        _logger.debug(msg.format(self._sections[-1]))

    def publish(self):
        """
        Publish the report with the registered handler

        Parameters
        None
        """
        # Generate the report as a string
        report = ""
        report += self._template["Head"]
        report += self._template["HeaderStart"]
        report += self._template["Title"].format_map(self._attributes)
        report += self._template["HeaderEnd"]
        report += self._template["BodyStart"].format_map(self._attributes)

        report += self._template["TOCStart"]
        for section in self._sections:
            report += self._template["TOCEntry"].format_map(section)
            report += self._separator
        report += self._template["TOCEnd"]

        report += self._template["SummaryStart"]
        for section in self._sections:
            report += self._template["SummaryEntry"].format_map(section)
            report += self._separator
        report += self._template["SummaryEnd"]

        report += self._template["BodyEnd"].format_map(self._attributes)
        report += self._template["Tail"].format_map(self._attributes)

        # Publish it
        if len(self._handlers) != 0:
            for handler in self._handlers:
                handler.publish(report, self._subtype, self._charset)
        else:
            # no handler to publish the report
            msg = "There is no handler defined. So the publishing do nothing."
            _logger.warning(msg)

    def _parse_template(self, template):
        """
        Parse the template to extract the report sections.

        :param template: is the full path name of the template file.
        """
        # Guess the content type based on the template file's extension.
        # If the content type cannot be guessed, the template is considered as
        # text plain. A plain text template is considered as using the utf-8
        # charset.
        content_type, encoding = mimetypes.guess_type(template)
        if content_type is not None:
            maintype, subtype = content_type.split("/", 1)
            if maintype != "text":
                msg = "The template must be a text-like format such as html"
                raise ValueError(msg)

            self._subtype = subtype
            if self._subtype == "html":
                self._charset = None
        else:
            msg = "The type of '{}' cannot be guessed. Considered as " \
                  "text/plain."
            _logger.warning(msg.format(os.path.basename(template)))

        name = self.names[0]
        self._template[name] = ""
        with open(template) as file:
            for line in file:
                match = self._re.match(line)
                if match is None:
                    self._template[name] += line
                    msg = "Add the following line to {} section : '{}'."
                    _logger.debug(msg.format(name, repr(line)))
                else:
                    if match.group("name") in self.names:
                        name = match.group("name")
                        self._template[name] = ""
                        msg = "Start a new section '{}'."
                        _logger.debug(msg.format(name))
                    else:
                        # The named section is not a well-known section,
                        # its content is simply added to the current section
                        msg = "'{}' is not a well-know section. Line ignored"
                        _logger.warning(msg.format(name))


class BaseHandler:
    """
    Base class for publish a report.

    Public instance variables
        None

    Public methods
        load_config: configure the handler from a dictionary.
        publish: publish the report.

    Subclass API variables (i.e. may be use by subclass)
        None.

    Subclass API Methods (i.e. must be overwritten by subclass)
        None

    Configuration
        None.
    """
    def __init__(self):
        """
        Constructor

        Parameters
            None, the real __init__ signature is unknown for a base class.
        """
        msg = "Instance of {} created."
        _logger.debug(msg.format(self.__class__))

    def load_config(self, config):
        """
        Configure the handler from a dictionary.

        :param config: is a dictionary containing the configuration as described
        in the `report.example.ini` file.
        """
        raise NotImplementedError

    def _load_default(self):
        """
        Configure the handler with its default value.
        """
        raise NotImplementedError

    def publish(self, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text).
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        raise NotImplementedError


class MailHandler(BaseHandler):
    """
    Send the report by mail.

    Public methods
        load_config: configure the handler from a dictionary.
        set_host: set the SMTP host.
        set_credentials: set the recipients mail addresses.
        set_from_address: set the sender mail address.
        set_mail_sent_folder: set the mail sent special folder.
        set_pending_mail_folder: set the pending mail special folder.
        set_to_addresses; set the recipients mail addresses.
        publish: publish the report.

    Subclass API variables (i.e. may be use by subclass)
        None.

    Subclass API Methods (i.e. must be overwritten by subclass)
        None

    Configuration
        The configuration is detailed in the `report.example.ini` file.
    """
    def __init__(self):
        """Constructor

        Parameters
            None

        Exception
            None
        """
        # Initial values
        super().__init__()
        self._hostname = ""
        self._port_number = 0
        self._credentials = None

        self._from_address = ""
        self._mail_sent_folder = ""
        self._pending_mail_folder = ""

        self._subject = "Report"
        self._to_addresses = []

    def load_config(self, config):
        """
        Configure the handler from a dictionary.

        :param config: is a dictionary containing the configuration as described
        in the `report.example.ini` file.
        """
        # check parameters type
        if not isinstance(config, dict):
            msg = "config argument must be a class 'dict'. not {0}"
            msg = msg.format(config.__class__)
            raise TypeError(msg)

        # Host configuration
        host = config["host"].split(",", maxsplit=1)
        if len(host) == 2:
            if host[1].isdecimal:
                self.set_host(host[0], int(host[1]))
            else:
                msg = "Port number has to be a decimal number (see host " \
                      "configuration item)."
                raise ValueError(msg)
        else:
            self.set_host(host[0])
        if "credentials" in config:
            self.set_credentials(config["credentials"].split(","))

        # Mail service configuration
        if "from_address" in config:
            self.set_from_address(config["from_address"])
        if "mail_sent" in config:
            self.set_mail_sent_folder(config["mail_sent"])
        if "pending_mail" in config:
            self.set_pending_mail_folder(config["pending_mail"])

        # Mail content configuration
        self.set_to_addresses(config["to_addresses"].split(","))
        if "subject" in config:
            self.set_subject(config["subject"])

    def _load_default(self):
        """
        Configure the handler with its default value.

        For the mail handler, there is no default value
        """
        self.__init__()

    def set_host(self, hostname, port_number=25):
        """
        Set the SMTP host.

        :param hostname: is a string containing the full qualified name of the
        SMTP server host.
        :param port_number: is a integer specifying the port number to use. By
        default, the standard SMTP port number is used.
        """
        # check parameters type
        if not isinstance(hostname, str):
            msg = "hostname argument must be a class 'str'. not {0}"
            msg = msg.format(hostname.__class__)
            raise TypeError(msg)
        if not isinstance(port_number, int):
            msg = "port_num argument must be a class 'int'. not {0}"
            msg = msg.format(port_number.__class__)
            raise TypeError(msg)

        if hostname == "":
            msg = "SMTP server name has to be specified."
            raise ValueError(msg)

        self._hostname = hostname
        self._port_number = port_number

        msg = "Mail host is set to '{}:{}'"
        _logger.debug(msg.format(self._hostname, self._port_number))

    def set_credentials(self, credentials):
        """
        Set the recipients mail addresses.

        :param credentials: is a list containing containing the username and the
        password to connect to the SMTP server.
        """
        # check parameters type
        if not isinstance(credentials, list):
            msg = "credentials argument must be a class 'list'. " \
                  "not {0}"
            msg = msg.format(credentials.__class__)
            raise TypeError(msg)

        self._credentials = credentials

        msg = "Credential are set to '{}'"
        _logger.debug(msg.format(self._credentials[0]))

    def set_from_address(self, address=""):
        """
        Set the sender mail address.

        :param address: is a string containing the mail addresses of the
        sender. If not specified, the address is set to the local hostname.
        (see smtplib.SMTP())
        """
        # check parameters type
        if address is not None and not isinstance(address, str):
            msg = "address argument must be a class 'str'. not {0}"
            msg = msg.format(address.__class__)
            raise TypeError(msg)

        self._from_address = address

        msg = "Sender addresses are set to '{}'"
        _logger.debug(msg.format(self._from_address))

    def set_mail_sent_folder(self, path):
        """
        Set the mail sent special folder.

        :param path: is the full path name of the folder where a copy of the
        mail will be written. If the folder doesn't exit, it will be create.
        An empty string does nothing.
        """
        # check parameters type
        if path is not None and not isinstance(path, str):
            msg = "path argument must be a class 'str'. not {0}"
            msg = msg.format(path.__class__)
            raise TypeError(msg)

        path = path.strip()
        if len(path) != 0:
            # TODO : treat the exception for os.makedirs
            os.makedirs(path, exist_ok=True)
            self._mail_sent_folder = path

        msg = "Mail sent special folder is set to '{}'"
        _logger.debug(msg.format(self._mail_sent_folder))

    def set_pending_mail_folder(self, path=""):
        """
        Set the pending mail special folder.

        :param path: is the full path name of the folder where a copy of the
        mail will be written until it is sent. It avoid to lost mail if the mail
        server configuration is erroneous or if the mail server doesn't answer.
        An empty string does nothing.
        """
        # check parameters type
        if path is not None and not isinstance(path, str):
            msg = "path argument must be a class 'str'. not {0}"
            msg = msg.format(path.__class__)
            raise TypeError(msg)

        path = path.strip()
        if len(path) != 0:
            # TODO : treat the exception for os.makedirs
            os.makedirs(path, exist_ok=True)
            self._pending_mail_folder = path

        msg = "Mail sent special folder is set to '{}'"
        _logger.debug(msg.format(self._pending_mail_folder))

    def set_to_addresses(self, addresses):
        """
        Set the recipients mail addresses.

        :param addresses: is a string or a list containing the mail addresses
        of the recipient. An empty item of the list, an empty list or an empty
        string (or only composed of space) raised a ValueError exception.
        """
        # check parameters type
        if not isinstance(addresses, (str, list)):
            msg = "addresses argument must be a class 'str' or 'list'. " \
                  "not {0}"
            msg = msg.format(addresses.__class__)
            raise TypeError(msg)
        if len(addresses) == 0:
            msg = "Recipients mail addresses have to be specified."
            raise ValueError(msg)

        self._to_addresses = []
        if isinstance(addresses, list):
            for address in addresses:
                address = address.strip()
                if len(address) != 0:
                    self._to_addresses.append(address)
                else:
                    msg = "Recipients mail addresses have to be specified."
                    raise ValueError(msg)
        else:
            self._to_addresses = [addresses]

        msg = "Recipient addresses are set to '{}'"
        _logger.debug(msg.format(self._to_addresses))

    def set_subject(self, subject=""):
        """
        Set the subject mail.

        :param subject: is a string containing the subject mail. An empty
        string does nothing.
        """
        # check parameters type
        if not isinstance(subject, str):
            msg = "subject argument must be a class 'str'. not {0}"
            msg = msg.format(subject.__class__)
            raise TypeError(msg)

        if len(subject) != 0:
            self._subject = subject

        msg = "Subject mail is set to '{}'"
        _logger.debug(msg.format(self._subject))

    def publish(self, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text). By default, the report is an HTML encoded one.
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        # check parameters type
        if not isinstance(report, str):
            msg = "report argument must be a class 'str'. not {0}"
            msg = msg.format(report.__class__)
            raise TypeError(msg)
        if not isinstance(subtype, str):
            msg = "subtype argument must be a class 'str'. not {0}"
            msg = msg.format(subtype.__class__)
            raise TypeError(msg)
        if charset is not None and not isinstance(charset, str):
            msg = "charset argument must be a class 'str'. not {0}"
            msg = msg.format(charset.__class__)
            raise TypeError(msg)

        # Create the message container
        mail = email.mime.text.MIMEText(report, subtype, charset)
        mail["Subject"] = self._subject
        mail["From"] = self._from_address
        mail["To"] = ", ".join(self._to_addresses)

        # Write a copy in pending mail
        basename = self._subject2filename()
        if self._pending_mail_folder != "":
            filename = os.path.join(self._pending_mail_folder, basename)
            with open(filename, mode="w") as file:
                file.write(mail.as_string())

        # Send the message
        with smtplib.SMTP(self._hostname, self._port_number) as handler:
            if self._credentials is not None:
                handler.login(self._credentials[0], self._credentials[1])
            handler.send_message(mail)

        # Write a copy in sent mail
        if self._pending_mail_folder != "":
            if self._mail_sent_folder != "":
                source = os.path.join(self._pending_mail_folder, basename)
                destination = os.path.join(self._mail_sent_folder, basename)
                shutil.move(source, destination)
        else:
            if self._mail_sent_folder != "":
                filename = os.path.join(self._mail_sent_folder, basename)
                with open(filename, mode="w") as file:
                    file.write(mail.as_string())

    def _subject2filename(self):
        """
        Convert a mail subject in a file name.

        The method replace special characters in string using the %xx escape
        using the `urllib.parse.quote()` function (see 'https://docs.python.org/
        3/library/urllib.parse.html#urllib.parse.quote' for details.

        The method use only the first 20 characters of the subject to avoid long
        file name. The file name has a suffix based on current date time to
        guarantee to have a unique value.

        :return: a unique string for a filename.
        """
        name = urllib.parse.quote(self._subject.lower()[:14], safe="")
        timestamp = str(time.time())
        filename = "{}-{}.eml".format(name, timestamp)

        return filename


class FileHandler(BaseHandler):
    """
    Write the report in a file.

    Public methods
        load_config: configure the handler from a dictionary.
        set_mode: set the mode in which the file is opened.
        set_filename: set the full path name of the destination file.
        publish: publish the report.

    Subclass API variables (i.e. may be use by subclass)
        None.

    Subclass API Methods (i.e. must be overwritten by subclass)
        None

    Configuration
        The configuration is detailed in the `report.example.ini` file.
    """
    def __init__(self):
        """Constructor

        Parameters
            None

        Exception
            None
        """
        super().__init__()
        self._filename = ""
        self._mode = "w"

    def load_config(self, config):
        """
        Configure the handler from a dictionary.

        :param config: is a dictionary containing the configuration as described
        in the `report.example.ini` file.
        """
        # check parameters type
        if not isinstance(config, dict):
            msg = "config argument must be a class 'dict'. not {0}"
            msg = msg.format(config.__class__)
            raise TypeError(msg)

        # File configuration
        self.set_filename(config["filename"])
        if "mode" in config:
            self.set_mode(config["mode"])

    def _load_default(self):
        """
        Configure the handler with its default value.

        For the file handler, there is no default value
        """
        self.__init__()

    def set_mode(self, mode="w"):
        """
        Set the mode in which the file is opened.

        :param mode: is a string specifying the mode in which the file is
        opened.(see [`open()`](https://docs.python.org/3/library/
        functions.html#open)
        """
        # check parameters type
        if not isinstance(mode, str):
            msg = "mode argument must be a class 'str'. not {0}"
            msg = msg.format(mode.__class__)
            raise TypeError(msg)

        self._mode = mode

        msg = "Open mode is set to '{}'"
        _logger.debug(msg.format(self._mode))

    def set_filename(self, filename):
        """
        Set the full path name of the destination file.

        :param filename: is a string containing the full path name of the
        destination file.
        """
        # check parameters type
        if not isinstance(filename, str):
            msg = "filename argument must be a class 'str'. not {0}"
            msg = msg.format(filename.__class__)
            raise TypeError(msg)

        filename = filename.strip()
        if len(filename) != 0:
            # TODO : treat the exception for os.makedirs
            path = os.path.dirname(filename)
            os.makedirs(path, exist_ok=True)
            self._filename = filename

        msg = "Filename is set to '{}'"
        _logger.debug(msg.format(self._filename))

    def publish(self, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text). By default, the report is an HTML encoded one.
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        # check parameters type
        if not isinstance(report, str):
            msg = "report argument must be a class 'str'. not {0}"
            msg = msg.format(report.__class__)
            raise TypeError(msg)
        if not isinstance(subtype, str):
            msg = "subtype argument must be a class 'str'. not {0}"
            msg = msg.format(subtype.__class__)
            raise TypeError(msg)
        if charset is not None and not isinstance(charset, str):
            msg = "charset argument must be a class 'str'. not {0}"
            msg = msg.format(charset.__class__)
            raise TypeError(msg)

        with open(self._filename, self._mode) as file:
            file.write(report)


class StreamHandler(BaseHandler):
    """
    Write the report in a stream (standard output).

    Public methods
        load_config: configure the handler from a dictionary.
        set_stream: set the stream in which the report will be written.
        publish: publish the report.

    Subclass API variables (i.e. may be use by subclass)
        None.

    Subclass API Methods (i.e. must be overwritten by subclass)
        None

    Configuration
        The configuration is detailed in the `report.example.ini` file.
    """
    _known_streams = {
        "sys.stdout": sys.stdout,
        "sys.stderr": sys.stderr
    }

    def __init__(self):
        """Constructor

        Parameters
            None

        Exception
            None
        """
        super().__init__()
        self._stream = sys.stdout

    def load_config(self, config):
        """
        Configure the handler from a dictionary.

        :param config: is a dictionary containing the configuration as described
        in the `report.example.ini` file.
        """
        # check parameters type
        if not isinstance(config, dict):
            msg = "config argument must be a class 'dict'. not {0}"
            msg = msg.format(config.__class__)
            raise TypeError(msg)

        # Stream configuration
        # The

        if "stream" in config:
            if config["stream"] in self._known_streams:
                self.set_stream(self._known_streams[config["stream"]])
            else:
                msg = "Unknown stream ({}). Streams are limited to known " \
                      "stream : {sys.stdout|sys.stderr}."
                msg = msg.format(config["stream"])
                raise ValueError(msg)
        else:
            self.set_stream(sys.stdout)

    def _load_default(self):
        """
        Configure the handler with its default value.

        For the file handler, there is no default value
        """
        self.__init__()

    def set_stream(self, stream=sys.stdout):
        """
        Set the stream in which the report will be written.

        :param stream: is a string specifying the standard stream on which
        report will be written. If it is not present, sys.stdout will be used.
        (see https://docs.python.org/3/library/sys.html#sys.stdin).
        """
        # check parameters type
        if not isinstance(stream, io.TextIOWrapper):
            msg = "mode argument must be a class '_io.TextIOWrapper'. not {0}"
            msg = msg.format(stream.__class__)
            raise TypeError(msg)

        self._stream = stream

        msg = "Stream is set to '{}'"
        _logger.debug(msg.format(self._stream))

    def publish(self, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text). By default, the report is an HTML encoded one.
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        print(report, file=self._stream)


