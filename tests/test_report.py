"""
This module defines a test suite for testing the report module.
"""

import logging
import sys
import configparser
import os
import smtplib
import socket
import unittest

# Modules to be tested are located in another directory. So the Module Search
# Path is modified for including the root of theses modules.
pathname = os.path.join(os.path.dirname(__file__), os.pardir, "lapptrack")
sys.path.append(os.path.abspath(pathname))

from support import report


__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


class TestReport(unittest.TestCase):
    def setUp(self):
        # Modules to be testes use the logging facility, so a minimal
        # configuration is set.
        logging.basicConfig(
            filename=os.path.splitext(__file__)[0]+".log",
            filemode="w",
            format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
            level=logging.ERROR)
        _logger = logging.getLogger(__name__)

        self.content_attributes = {
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
            "release_note": "http://download.exemple.com/dummy/"
                            "release_note.html",
            "location": "http://download.exemple.com/dummy/installer.exe",
            "change_summary": "<ul>"
                              "<li>version 1.0.0 published on 2016-02-02</li>"
                              "<ul>"
                              "<li>a dummy feature</li>"
                              "<li>Small miscellaneous improvements and "
                              "bugfixes</li>"
                              "</ul>"
                              "<li>version 0.1.0 published on 2015-02-02</li>"
                              "<ul>"
                              "<li>initial commit</li>"
                              "</ul>"
                              "</ul>",
            "installer": "./store/installer_0.1.0+dummy.exe",
            "file_size": 12345689,
            "secure_hash": ("sha256",
                            "4a404b0d09dfd3952107e314ab632622"
                            "93b2fb0a4dc6837b57fb7274bd016865"),
            "silent_inst_args": "/silent",
            "std_inst_args": ""
        }
        self.report_attributes = {
            "title": "title of the report"  # not used
        }

    def tearDown(self):
        pass

    def test_api_default(self):
        """
        Make a report based on default values and publish it using available
        handlers (Mail, File and Stream)
        """
        a_report = report.Report()
        a_report.set_template()
        a_report.set_attributes(self.report_attributes)
    
        a_handler = report.MailHandler()
        a_handler.set_host("smtp.free.fr")
        a_handler.set_to_addresses("frederic.mezou@free.fr")
        a_report.add_handler(a_handler)
    
        a_handler = report.FileHandler()
        a_handler.set_filename("../~store/report.html")
        a_report.add_handler(a_handler)
    
        a_handler = report.StreamHandler()
        a_report.add_handler(a_handler)
    
        a_report.add_section(self.content_attributes)
        a_report.publish()

    def test_multiple_report(self):
        """
        Make reports using multiple templates based on default values and write
        it in files.
        """
        a_report = report.Report()
        a_report.set_template()
        a_report.set_attributes(self.report_attributes)
    
        a_handler = report.FileHandler()
        a_handler.set_filename("../~store/report.html")
        a_report.add_handler(a_handler)
    
        a_report.add_section(self.content_attributes)
        a_report.publish()
    
        a_report.set_template("../lapptrack/support/report_template.txt")
        a_handler.set_filename("../~store/report.txt")
        a_report.publish()

    def test_api_custom(self):
        """
        Make a report based on custom values and publish it using available
        handlers (Mail, File and Stream). Customised values are set with API
        """
        a_report = report.Report()
        a_report.set_template()
        a_report.set_attributes(self.report_attributes)
    
        a_handler = report.MailHandler()
        a_handler.set_host("smtp.free.fr", 25)
        a_handler.set_from_address("lappupdate.mezou@free.fr")
        a_handler.set_sent_mail_folder("../~store/mails/sent")
        a_handler.set_pending_mail_folder("../~store/mails/pending")
        a_handler.set_to_addresses(["frederic.mezou@free.fr",
                                    "maskeudennou@free.fr"])
        a_handler.set_subject("lAppUpdate: New Update(s) Alert")
        a_report.add_handler(a_handler)
    
        a_handler = report.FileHandler()
        a_handler.set_filename("../~store/report.html")
        a_handler.set_mode("a")
        a_report.add_handler(a_handler)
    
        a_handler = report.StreamHandler()
        a_handler.set_stream(sys.stderr)
        a_report.add_handler(a_handler)
    
        a_report.add_section(self.content_attributes)
        a_report.publish()

    def test_ini_default(self):
        """
        Make a report based on default values stored in a ini file and publish it
        using available handlers (Mail, File and Stream).
        """
        a_report = report.Report()
        filename = os.path.join(os.path.dirname(__file__), "test_ini_default.ini")
        a_report.load_config(self._load_config(filename), False)
        a_report.set_attributes(self.report_attributes)
        a_report.add_section(self.content_attributes)
        a_report.publish()

    def test_ini_custom(self):
        """
        Make a report based on custom values stored in a ini file and publish it
        using available handlers (Mail, File and Stream).
        """
        a_report = report.Report()
        filename = os.path.join(os.path.dirname(__file__), "test_ini_custom.ini")
        a_report.load_config(self._load_config(filename), False)
        a_report.add_section(self.content_attributes)
        a_report.publish()

    def test_api_host_connect_error(self):
        """
        Use a non SMTP server (example.com)
        """
        a_report = report.Report()
        a_report.set_template()
        a_report.set_attributes(self.report_attributes)
    
        a_handler = report.MailHandler()
        a_handler.set_host("example.com")
        a_handler.set_to_addresses("frederic.mezou@free.fr")
        a_report.add_handler(a_handler)
        a_report.add_section(self.content_attributes)

        with self.assertRaises(smtplib.SMTPConnectError):
            a_report.publish()

    def test_api_host_error(self):
        """
        Use a unknown hostname
        """
        a_report = report.Report()
        a_report.set_template()
        a_report.set_attributes(self.report_attributes)
    
        a_handler = report.MailHandler()
        a_handler.set_host("smtp.example.invalid")
        a_handler.set_to_addresses("frederic.mezou@free.fr")
        a_report.add_handler(a_handler)
        a_report.add_section(self.content_attributes)
    
        with self.assertRaises(socket.gaierror):
            a_report.publish()

    def test_api_to_addr_error(self):
        """
        Use recipients invalid mail addresses
        """
        a_report = report.Report()
        a_report.set_template()
        a_report.set_attributes(self.report_attributes)
    
        a_handler = report.MailHandler()
        a_handler.set_host("smtp.free.fr")
        a_handler.set_from_address("frederic.mezou@free.fr")
        a_handler.set_to_addresses("noreply@domain.invalid")
        a_report.add_handler(a_handler)
        a_report.add_section(self.content_attributes)
    
        with self.assertRaises(smtplib.SMTPRecipientsRefused):
            a_report.publish()

    def test_api_from_addr_error(self):
        """
        Use a sender unknown mail address
        """
        a_report = report.Report()
        a_report.set_template()
        a_report.set_attributes(self.report_attributes)
    
        a_handler = report.MailHandler()
        a_handler.set_host("smtp.free.fr")
        a_handler.set_from_address("noreply@domain.invalid")
        a_handler.set_to_addresses("frederic.mezou@free.fr")
        a_report.add_handler(a_handler)
        a_report.add_section(self.content_attributes)
    
        with self.assertRaises(smtplib.SMTPSenderRefused):
            a_report.publish()

    def test_api_mail_folder_error(self):
        """
        Use a inaccessible path as a mail folder
        """
        a_report = report.Report()
        a_report.set_template()
        a_report.set_attributes(self.report_attributes)
    
        a_handler = report.MailHandler()
        a_handler.set_host("smtp.free.fr")
        a_handler.set_to_addresses("frederic.mezou@free.fr")
        a_report.add_handler(a_handler)
        a_report.add_section(self.content_attributes)
    
        with self.assertRaises(FileNotFoundError):
            a_handler.set_sent_mail_folder("W:/Program Files/mailstore/sent")
            a_report.publish()

        with self.assertRaises(PermissionError):
            a_handler.set_sent_mail_folder("C:/Program Files/mailstore")
            a_report.publish()

        with self.assertRaises(FileNotFoundError):
            a_handler.set_pending_mail_folder("W:/Program Files/mailstore")
            a_report.publish()

        with self.assertRaises(PermissionError):
            a_handler.set_pending_mail_folder("C:/Program Files/mailstore")
            a_report.publish()

    def test_api_file_folder_error(self):
        """
        Use a inaccessible path for the file report
        """
        a_report = report.Report()
        a_report.set_template()
        a_report.set_attributes(self.report_attributes)
    
        a_handler = report.FileHandler()
        a_handler.set_mode("a")
        a_report.add_handler(a_handler)
    
        with self.assertRaises(FileNotFoundError):
            a_handler.set_filename("W:/Program Files/report.html")
            a_report.publish()

        with self.assertRaises(PermissionError):
            a_handler.set_filename("C:/Program Files/report.html")
            a_report.publish()

    def _load_config(self, filename):
        """
        Load the configuration from a configuration file (see [`config.parser`]
        (https://docs.python.org/3/library/configparser.html# module-configparser)

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


if __name__ == '__main__':
    unittest.main()
