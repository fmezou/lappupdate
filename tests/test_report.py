"""
This module defines a test suite for testing the report module.
"""

import logging
import sys
import configparser
import os
import smtplib
import socket
import traceback

import report

__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"

# Basic configuration of the logging facility.
logging.basicConfig(
    filename=os.path.splitext(__file__)[0]+".log",
    filemode="w",
    format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
    level=logging.DEBUG)
_logger = logging.getLogger(__name__)


def test_api_default():
    """
    Make a report based on default values and publish it using available
    handlers (Mail, File and Stream)
    """
    a_report = report.Report()
    a_report.set_template()
    a_report.set_attributes(report_attributes)

    a_handler = report.MailHandler()
    a_handler.set_host("smtp.free.fr")
    a_handler.set_to_addresses("frederic.mezou@free.fr")
    a_report.add_handler(a_handler)

    a_handler = report.FileHandler()
    a_handler.set_filename("./tempstore/report.html")
    a_report.add_handler(a_handler)

    a_handler = report.StreamHandler()
    a_report.add_handler(a_handler)

    a_report.add_section(content_attributes)
    a_report.publish()

    return True


def test_multiple_report():
    """
    Make reports using multiple templates based on default values and write
    it in files.
    """
    a_report = report.Report()
    a_report.set_template()
    a_report.set_attributes(report_attributes)

    a_handler = report.FileHandler()
    a_handler.set_filename("./tempstore/report.html")
    a_report.add_handler(a_handler)

    a_report.add_section(content_attributes)
    a_report.publish()

    a_report.set_template("report_template.txt")
    a_handler.set_filename("./tempstore/report.txt")
    a_report.publish()

    return True


def test_api_custom():
    """
    Make a report based on custom values and publish it using available
    handlers (Mail, File and Stream). Customised values are set with API
    """
    a_report = report.Report()
    a_report.set_template()
    a_report.set_attributes(report_attributes)

    a_handler = report.MailHandler()
    a_handler.set_host("smtp.free.fr", 25)
    a_handler.set_from_address("lappupdate.mezou@free.fr")
    a_handler.set_sent_mail_folder("./mailstore/sent")
    a_handler.set_pending_mail_folder("./mailstore/pending")
    a_handler.set_to_addresses(["frederic.mezou@free.fr",
                                "maskeudennou@free.fr"])
    a_handler.set_subject("lAppUpdate: New Update(s) Alert")
    a_report.add_handler(a_handler)

    a_handler = report.FileHandler()
    a_handler.set_filename("./tempstore/report.html")
    a_handler.set_mode("a")
    a_report.add_handler(a_handler)

    a_handler = report.StreamHandler()
    a_handler.set_stream(sys.stderr)
    a_report.add_handler(a_handler)

    a_report.add_section(content_attributes)
    a_report.publish()

    return True


def test_ini_default():
    """
    Make a report based on default values stored in a ini file and publish it
    using available handlers (Mail, File and Stream).
    """
    a_report = report.Report()
    filename = os.path.join(os.path.dirname(__file__), "test_ini_default.ini")
    a_report.load_config(_load_config(filename), False)
    a_report.set_attributes(report_attributes)
    a_report.add_section(content_attributes)
    a_report.publish()

    return True


def test_ini_custom():
    """
    Make a report based on custom values stored in a ini file and publish it
    using available handlers (Mail, File and Stream).
    """
    a_report = report.Report()
    filename = os.path.join(os.path.dirname(__file__), "test_ini_custom.ini")
    a_report.load_config(_load_config(filename), False)
    a_report.add_section(content_attributes)
    a_report.publish()

    return True


def test_api_host_connect_error():
    """
    Use a non SMTP server (example.com)
    """
    result = True
    a_report = report.Report()
    a_report.set_template()
    a_report.set_attributes(report_attributes)

    a_handler = report.MailHandler()
    a_handler.set_host("example.com")
    a_handler.set_to_addresses("frederic.mezou@free.fr")
    a_report.add_handler(a_handler)
    a_report.add_section(content_attributes)

    try:
        a_report.publish()
    except smtplib.SMTPConnectError as err:
        print("Expected error", err)
    except:
        result = False
        print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
        traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
    else:
        result = False

    return result


def test_api_host_error():
    """
    Use a unknown hostname
    """
    result = True
    a_report = report.Report()
    a_report.set_template()
    a_report.set_attributes(report_attributes)

    a_handler = report.MailHandler()
    a_handler.set_host("smtp.example.invalid")
    a_handler.set_to_addresses("frederic.mezou@free.fr")
    a_report.add_handler(a_handler)
    a_report.add_section(content_attributes)

    try:
        a_report.publish()
    except socket.gaierror as err:
        print("Expected error", err)
    except:
        result = False
        print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
        traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
    else:
        result = False

    return result


def test_api_to_addr_error():
    """
    Use recipients invalid mail addresses
    """
    result = True
    a_report = report.Report()
    a_report.set_template()
    a_report.set_attributes(report_attributes)

    a_handler = report.MailHandler()
    a_handler.set_host("smtp.free.fr")
    a_handler.set_from_address("frederic.mezou@free.fr")
    a_handler.set_to_addresses("noreply@domain.invalid")
    a_report.add_handler(a_handler)
    a_report.add_section(content_attributes)

    try:
        a_report.publish()
    except smtplib.SMTPRecipientsRefused as err:
        print("Expected error", err)
    except:
        result = False
        print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
        traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
    else:
        result = False

    return result


def test_api_from_addr_error():
    """
    Use a sender unknown mail address
    """
    result = True
    a_report = report.Report()
    a_report.set_template()
    a_report.set_attributes(report_attributes)

    a_handler = report.MailHandler()
    a_handler.set_host("smtp.free.fr")
    a_handler.set_from_address("noreply@domain.invalid")
    a_handler.set_to_addresses("frederic.mezou@free.fr")
    a_report.add_handler(a_handler)
    a_report.add_section(content_attributes)

    try:
        a_report.publish()
    except smtplib.SMTPSenderRefused as err:
        print("Expected error", err)
    except:
        result = False
        print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
        traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
    else:
        result = False

    return result


def test_api_mail_folder_error():
    """
    Use a inaccessible path as a mail folder
    """
    result = True
    a_report = report.Report()
    a_report.set_template()
    a_report.set_attributes(report_attributes)

    a_handler = report.MailHandler()
    a_handler.set_host("smtp.free.fr")
    a_handler.set_to_addresses("frederic.mezou@free.fr")
    a_report.add_handler(a_handler)
    a_report.add_section(content_attributes)

    try:
        a_handler.set_sent_mail_folder("W:/Program Files/mailstore/sent")
        a_report.publish()
    except FileNotFoundError as err:
        print("Expected error", err)
    except:
        result = False
        print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
        traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
    else:
        result = False

    if result:
        try:
            a_handler.set_sent_mail_folder("C:/Program Files/mailstore")
            a_report.publish()
        except PermissionError as err:
            print("Expected error", err)
        except:
            result = False
            print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
            traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
        else:
            result = False

    if result:
        try:
            a_handler.set_pending_mail_folder("W:/Program Files/mailstore")
            a_report.publish()
        except FileNotFoundError as err:
            print("Expected error", err)
        except:
            result = False
            print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
            traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
        else:
            result = False

    if result:
        try:
            a_handler.set_pending_mail_folder("C:/Program Files/mailstore")
            a_report.publish()
        except PermissionError as err:
            print("Expected error", err)
        except:
            result = False
            print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
            traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
        else:
            result = False

    return result


def test_api_file_folder_error():
    """
    Use a inaccessible path for the file report
    """
    result = True
    a_report = report.Report()
    a_report.set_template()
    a_report.set_attributes(report_attributes)

    a_handler = report.FileHandler()
    a_handler.set_mode("a")
    a_report.add_handler(a_handler)

    try:
        a_handler.set_filename("W:/Program Files/report.html")
        a_report.publish()
    except FileNotFoundError as err:
        print("Expected error", err)
    except:
        result = False
        print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
        traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
    else:
        result = False

    if result:
        try:
            a_handler.set_filename("C:/Program Files/report.html")
            a_report.publish()
        except PermissionError as err:
            print("Expected error", err)
        except:
            result = False
            print("Unexpected error : ", sys.exc_info()[0], sys.exc_info()[1])
            traceback.print_tb(sys.exc_info()[2], file=sys.stdout)
        else:
            result = False

    return result


def final():
    """
    Test campaign completed
    """
    _logger.info("Test campaign completed")
    return True


def _load_config(filename):
    """
    Load the configuration from a configuration file (see [`config.parser`]
    (https://docs.python.org/3/library/configparser.html#module-configparser)

    The configuration is stored in a dictionary with the same structure as the
    configuration file.

    :param filename: is the full path name of the configuration file.
    :return: a dictionary containing the configuration.
    """
    config = configparser.ConfigParser()
    with open(filename) as file:
        config.read_file(file)

    config_dict = {}
    for section in config.sections():
        config_dict[section] = {}
        for option in config.options(section):
            config_dict[section][option] = config.get(section, option)

    return config_dict

# Declare the python module will be tested
# Each entry details the name and the expected version of the module.
modules = [
    [report, "0.1.0"]
]

# Declare the unitary function test to execute
# The False value specifies that the function test will be ignored.
tests = [
    [test_api_default, False],
    [test_multiple_report, True],
    [test_api_custom, False],
    [test_ini_default, False],
    [test_ini_custom, False],
    [test_api_host_connect_error, False],
    [test_api_host_error, False],
    [test_api_to_addr_error, False],
    [test_api_from_addr_error, False],
    [test_api_mail_folder_error, False],
    [test_api_file_folder_error, False],
    [final, True]
]

if __name__ == "__main__":
    checked = True

    content_attributes = {
        "name": "Dummy Product",
        "version": "0.1.0+dummy",
        "display_name": "Dummy Product (1.0.1)",
        "published": "2016-02-18",
        "target": "unified",
        "description": "Dummy product is a amazing tool to do nothing",
        "editor": "Example. inc",
        "web_site_location": "http://www.exemple.com",
        "icon": "",
        "announce_location": "http://www.example.com/news.txt",
        "feed_location": "http://www.example.com/feed.rss",
        "release_note": "http://download.exemple.com/dummy/release_note.html",
        "location": "http://download.exemple.com/dummy/installer.exe",
        "change_summary": "<ul><li>version 1.0.0 published on 2016-02-02</li><ul><li>a dummy feature</li><li>Small miscellaneous improvements and bugfixes</li></ul><li>version 0.1.0 published on 2015-02-02</li><ul><li>initial commit</li></ul></ul>",
        "installer": "./store/installer_0.1.0+dummy.exe",
        "file_size": 12345689,
        "secure_hash": ("sha256",
                        "4a404b0d09dfd3952107e314ab63262293b2fb0a4dc6837b57fb7274bd016865"),
        "silent_inst_args": "/silent",
        "std_inst_args": ""
    }
    report_attributes = {
        "title": "title of the report"  # not used
    }

    for module in modules:
        if module[0].__version__ != module[1]:
            msg = "Unexpected version module (expected {}, readed {}) for {}"
            print(msg.format(module[1], module[0].__version__, module[0]),
                  file=sys.stderr)
            sys.exit(1)

    for test in tests:
        if test[1]:
            print("###########################################################")
            print("test id :", test[0].__name__)
            doc = test[0].__doc__.splitlines()
            for line in doc:
                line = line.strip()
                if len(line):
                    print(line)
            print("-- Log and result -----------------------------------------")
            checked = test[0]()
            if not checked:
                print("Test '{}' failed.".format(test[0].__name__))
                break
            else:
                print("Test '{}' succeeded.".format(test[0].__name__))
