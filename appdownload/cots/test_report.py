# Reserved for test
# This module is used as a script only for testing the report module.

import logging
import sys
import configparser
import os

import report

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
    a_handler.set_mail_sent_folder("./mailstore/sent")
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


test_set = [
    [test_api_default, False],
    [test_api_custom, False],
    [test_ini_default, False],
    [test_ini_custom, False],
    [final, True]
]

if __name__ == "__main__":
    checked = True

    content_attributes = {
        "name": "Dummy Product",
        "editor": "Dummy Company, SA",
        "description": "Dummy product is a amazing tool to do nothing",
        "version": "0.1.0+dummy",
        "url": "http://download.exemple.com/dummy/installer.exe",
        "installer": "./store/installer_0.1.0+dummy.exe",
        "release_note": "http://download.exemple.com/dummy/release_note.html",
        "published": "2016-02-18",
        "file_size": 12345689
    }
    report_attributes = {
        "title": "title of the report"  # not used
    }

    for test in test_set:
        if test[1]:
            print("###########################################################")
            print("test id :", test[0].__name__)
            doc = test[0].__doc__.splitlines()
            for line in doc:
                line = line.strip()
                if len(line):
                    print(line)
            print("-----------------------------------------------------------")
            checked = test[0]()
            if not checked:
                break
