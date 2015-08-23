"""Check and download applications' updates if any.

Usage
appdownload.py [-h] [-c | -d | -t] [--version]

optional arguments:
  -h, --help       show this help message and exit
  -c, --checkonly  check and report if applications' updates are available
                   without download it
  -d, --download   download applications' updates based on the last build
                   catalog (useful to recover a crashed application storage)

  -t, --testconf   check an appdownload.ini configuration file for internal
                   correctness
  --version        show program's version number and exit

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

# from cots import adobeflashplayer


__author__ = "Frederic MEZOU"
__version__ = "0.3.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


class AppDownload:
    def __init__(self):
        pass

    def run(self):
        raise NotImplementedError

    def check(self):
        raise NotImplementedError

    def download(self):
        raise NotImplementedError

    def test_configuration(self):
        raise NotImplementedError


# Entry point
# Build the command line parser
parser = argparse.ArgumentParser(
    description="Check and download applications\' updates if any.")
general = parser.add_mutually_exclusive_group()
general.add_argument("-c", "--checkonly", action="store_true",
                     help="check and report if applications' updates are available without"
                          " download it")
general.add_argument("-d", "--download", action="store_true",
                     help="download applications' updates based on the last build catalog"
                          " (useful to recover a crashed application storage)")
general.add_argument("-t", "--testconf", action="store_true",
                     help="check an appdownload.ini configuration file for internal correctness")
parser.add_argument("--version", action="version", version="%(prog)s version "+ __version__)

# Parse and run.
args = parser.parse_args()
maintask = AppDownload()
if args.checkonly:
    rc = maintask.check()
elif  args.download:
    rc = maintask.download()
elif  args.testconf:
    rc = maintask.test_configuration()
else:
    rc = maintask.run()