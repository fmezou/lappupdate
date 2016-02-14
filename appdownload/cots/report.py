"""
Make a report activity and publish it.

Classes
    Report: main class to make and publish report.

Exception

Function
    retrieve_file: retrieve a URL into a url on disk
    retrieve_tempfile: retrieve a URL into a temporary url on disk
    get_summary_header: return the header summary.
    get_summary_tail: return the tail of the summary.

Constant

"""

import logging
import os
import re
import email.mime.multipart
import email.mime.text
import email.utils
import mimetypes
import socket
import smtplib

__all__ = [
    "Report"
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
    of named sections.

    The use of the named keyword argument is based on the [string module]
    (https://docs.python.org/3/library/string.html#format-string-syntax).
    These named keyword are the ones returned by the `dump` method of the
    product class instance.

    Each section starts with a HTML comment and it ends with the start of
    next section or the end of the file. The comment match the following format
    and must be on one line:
    <!-- $lau:<name>$ -->
    `name` MUST comprise only ASCII alphanumerics and hyphen [0-9A-Za-z-] and
    MUST NOT be empty.

    If a named section is not declared in `Report.names`, its contents is added
    to the current section (i.e. no section is created).

    The 'summary.html' template is used by default.

    Public class variables
       names: is the list of the well-known named sections in a report template.

    Public instance variables
       ?name: is the name of the product (used in report mail and log file)

    Public methods
        add_section: add a section to the report.
        publish: publish the report with the registered handlers
        (see `add_handler`).
        add_handler: add a handler to publish the report.

        TODO
        get_config
        set_config : configure a report from a dictionary attribute
        (configparser compliant)
        see Config section for details

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None

    Configuration
        details the configuration ini file.
    """
    # TODO put the date of creation in the tail or head report
    # "this report was created on xxxxx"
    # or On xxxx, the below product have update available
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
    _SUMMARY = os.path.join(os.path.dirname(__file__), "summary_tmpl.html")

    def __init__(self, template=_SUMMARY, separator=""):
        """
        Constructor

        Parameters
        :param template: is the full path name of the template file. The format
        of the template file is described below.
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

        self._sections = []
        self._template = {}
        self._subtype = "plain"
        self._charset = "utf-8"
        self._handler = []
        self._separator = separator

        self._parse_template(template)

        msg = "Instance of {} created."
        _logger.debug(msg.format(self.__class__))

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

    def publish(self, attributes):
        """
        Publish the report with the registered handler

        :param attributes: is a dictionary containing the product attributes
        (typically the one returned by the `dump` method).
        """
        # Generate the report as a string
        report = ""
        report += self._template["Head"]
        report += self._template["HeaderStart"]
        report += self._template["Title"].format_map(attributes)
        report += self._template["HeaderEnd"]
        report += self._template["BodyStart"].format_map(attributes)

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

        report += self._template["BodyEnd"].format_map(attributes)
        report += self._template["Tail"].format_map(attributes)

        # Publish it
        for handler in self._handler:
            handler.publish(attributes["title"], report,
                            self._subtype, self._charset)

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

        self._handler.append(handler)
        msg = "{} added."
        _logger.debug(msg.format(handler.__class__))

    def _parse_template(self, filename):
        """
        Parse the template to extract the report sections.

        :param filename: is the full path name of the template file.
        """
        # check parameters type
        if not isinstance(filename, str):
            msg = "format_string argument must be a class 'str'. not {0}"
            msg = msg.format(filename.__class__)
            raise TypeError(msg)

        # Guess the content type based on the template file's extension.
        # If the content type cannot be guessed, the template is considered as
        # text plain. A plain text template is considered as using the utf-8
        # charset.
        content_type, encoding = mimetypes.guess_type(filename)
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
            _logger.warning(msg.format(os.path.basename(filename)))

        name = self.names[0]
        self._template[name] = ""
        with open(filename) as file:
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
    Base class for report publishing.

    Public instance variables
        ?name: is the name of the product (used in report mail and log file)

    Public methods
        publish: publish the report.

    Subclass API variables (i.e. may be use by subclass)
        ?_catalog_url: url of the product catalog.

    Subclass API Methods (i.e. must be overwritten by subclass)
        ?_parse_catalog: parse the catalog

    """
    def __init__(self):
        """
        Constructor

        """

        msg = "Instance of {} created."
        _logger.debug(msg.format(self.__class__))

    def publish(self, title, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param title: is a string specifying the subject of the email
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

    Public instance variables
        None

    Public methods
        publish: send the report.
    """
    def __init__(self, host, to_addresses, from_address=None, credentials=None):
        """Constructor

        Parameters
        :param host: is a string containing the full qualified name of the SMTP
        server host, or a tuple containing the full qualified name of the SMTP
        server and the port number to use.
        :param to_addresses: is a string or a list containing the mail addresses
        of the recipient.
        :param from_address: is a string containing the mail addresses of the
        sender. The default value is set to the local hostname. (see
        socket.getfqdn())
        :param credentials: is a tuple containing the username and the password
        to connect to SMTP server.

        Exception
            None
        """
        #
        # check parameters type
        if not isinstance(host, (str, tuple)):
            msg = "host argument must be a class 'str' or 'tuple'. not {0}"
            msg = msg.format(host.__class__)
            raise TypeError(msg)
        if not isinstance(to_addresses, (str, list)):
            msg = "to_addresses argument must be a class 'str' or 'list'. " \
                  "not {0}"
            msg = msg.format(to_addresses.__class__)
            raise TypeError(msg)
        if from_address is not None and not isinstance(from_address, str):
            msg = "from_address argument must be a class 'str'. not {0}"
            msg = msg.format(from_address.__class__)
            raise TypeError(msg)
        if credentials is not None and not isinstance(credentials, tuple):
            msg = "credentials argument must be a class 'tuple'. not {0}"
            msg = msg.format(from_address.__class__)
            raise TypeError(msg)

        # Initial values
        super().__init__()
        self._host = ""
        self._port = 0
        self._username = None
        self._password = None
        self._to_addresses = []
        self._from_address = ""

        if isinstance(host, tuple):
            self._host, self._port = host
        else:
            self._host = host
        if isinstance(to_addresses, list):
            self._to_addresses = to_addresses
        else:
            self._to_addresses = [to_addresses]
        if from_address is not None:
            self._from_address = from_address
        else:
            self._from_address = socket.getfqdn()
        if credentials is not None:
            self._username, self._password = credentials

    def publish(self, title, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param title: is a string specifying the subject of the email
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
        if not isinstance(title, str):
            msg = "title argument must be a class 'str'. not {0}"
            msg = msg.format(title.__class__)
            raise TypeError(msg)
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
        mail["Subject"] = title
        mail["From"] = self._from_address
        mail["To"] = ", ".join(self._to_addresses)

        # Send the message
        with smtplib.SMTP(self._host, self._port) as handler:
            if self._username is not None:
                handler.login(self._username, self._password)
            handler.send_message(mail)

        # FIXME: make a local copy to test
        with open(title, mode="w") as file:
            file.write(mail.as_string())


class FileHandler(BaseHandler):
    """
    Write the report in file.

    Public instance variables
        ?

    Public methods
        publish: send the report.
    """
    def __init__(self, filename):
        """Constructor

        Parameters
            None

        Exception
            None
        """
        super().__init__()
        self._filename = filename

    def publish(self, title, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param title: is a string specifying the subject of the email
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text). By default, the report is an HTML encoded one.
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        with open(self._filename, mode="w") as file:
            file.write(report)


class StreamHandler(BaseHandler):
    """
    Write the report in file.

    Public instance variables
        ?

    Public methods
        publish: send the report.
    """
    def __init__(self):
        """Constructor

        Parameters
            None

        Exception
            None
        """
        super().__init__()

    def publish(self, title, report, subtype, charset=None):
        """
        Publish the report

        Parameters
        :param title: is a string specifying the subject of the email
        :param report: is a string containing the report.
        :param subtype: is a string specifying the subtype of the content report
        as defined by the [IANA](http://www.iana.org/assignments/media-types/
        media-types.xhtml#text). By default, the report is an HTML encoded one.
        :param charset: is a string specifying the charset used in the report.
        If a "charset" parameter is specified in the report, this parameter
        should not used according to the [RFC 6838](http://tools.ietf.org/html
        /rfc6838#page-9).
        """
        print(report)


