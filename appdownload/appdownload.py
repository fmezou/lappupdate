"""Check and download applications' updates if any.

Usage
appdownload.py [-h] [-c | -d | -t] [--version]

optional arguments:
  -h, --help            show this help message and exit
  -c, --checkonly       check and report if applications' updates are
                        available without download it
  -d, --download        download applications' updates based on the last build
                        catalog (useful to recover a crashed application
                        storage)
  -t, --testconf        check an appdownload.ini configuration file for
                        internal correctness
  --configfile CONFIGFILE
                        The file specified contains the configuration details.
                        The information in this file includes application
                        catalog. See appdownload.ini for more information.
                        The default configuration file name is 'appdownload.ini'
                        located in the current working directory.
  --version             show program's version number and exit

Exit code
  0: no error
  1: an error occurred (error messages are print on stderr stream console
     and write in a log file.
  2: invalid argument. An argument of the command line isn't valid (see Usage).

Environment variables
The following environment variables affect the execution of this script:
#TODO:
"""


import argparse
import configparser

# from cots import adobeflashplayer


__author__ = "Frederic MEZOU"
__version__ = "0.3.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


class AppDownload:
    """Application class.

    Public instance variables
        None

    Public methods
        None

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None
    """
    def __init__(self, config_file=None):
        """constructor.

        Parameters
            config_file: Name of the configuration file. The name may be a
            partial one or a full path one.
        """
        self._config = None
        self._config_file = config_file

    def run(self):
        """run the AppDownload application.

        Parameters
            None
        """
        raise NotImplementedError

    def check(self):
        """check and report if applications' updates are available without
         download it.

        Parameters
            None
        """
        raise NotImplementedError

    def download(self):
        """download applications' updates based on the last build catalog.

        Parameters
            None
        """
        raise NotImplementedError

    def test_configuration(self):
        """check the configuration file for internal correctness.

        Parameters
            None
        """
        # raise NotImplementedError
        self._get_config()

    def _get_config(self):
        """get the configuration details from the configuration file.

        Parameters
            None
        """
        assert self._config_file is not None
        self._config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())
        self._config.read_file(self._config_file)
        print("Sections : ", self._config.sections())
        if self._config.sections():
            for app in self._config["app"]:
                print(app, ":", self._config["app"].getboolean(app))
                if self._config["app"].getboolean(app):
                    appsection = self._config[app]
                    for key in appsection:
                        print(key, ":", appsection[key])
        self._config_file.close()
        self._config_file = None

if __name__ == "__main__":
    # Entry point
    # Build the command line parser
    parser = argparse.ArgumentParser(
        description="Check and download applications\' updates if any.")
    general = parser.add_mutually_exclusive_group()
    general.add_argument("-c", "--checkonly", action="store_true",
                         help="check and report if applications' updates are "
                              "available without download it")
    general.add_argument("-d", "--download", action="store_true",
                         help="download applications' updates based on the "
                              "last build catalog (useful to recover a crashed "
                              "application storage)")
    general.add_argument("-t", "--testconf", action="store_true",
                         help="check an appdownload.ini configuration file for "
                              "internal correctness")
    parser.add_argument("--configfile", default="appdownload.ini",
                        type=argparse.FileType(mode='r'),
                        help="The file specified contains the configuration "
                             "details. The information in this file includes "
                             "application catalog. See appdownload.ini for "
                             "more information. The default configuration file "
                             "name is 'appdownload.ini' located in the current "
                             "working directory.")
    parser.add_argument("--version", action="version",
                        version="%(prog)s version " + __version__)

    # Parse and run.
    args = parser.parse_args()
    main_task = AppDownload(args.configfile)
    if args.checkonly:
        main_task.check()
    elif args.download:
        main_task.download()
    elif args.testconf:
        main_task.test_configuration()
    else:
        main_task.run()
