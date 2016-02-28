"""
This module defines a test suite for testing the core module.
"""

import logging
import os

import core

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s - %(name)s [%(funcName)s] - %(message)s",
        level=logging.WARNING)
    logger = logging.getLogger(__name__)
    checked = True

    # non variant
    url = "https://addons.cdn.mozilla.net/user-media/addons/1865/" \
          "adblock_plus-2.7-fx+sm+tb+an.xpi"
    dir_name = "../tempstore/"
    # Test 1 :
    ctype = "application/x-xpinstall"
    clength = 989188
    chash = (
        "sha256",
        "c1ef9d41e122ceb242facab8755219a8ffa9b8a15321c352d0e95e1ac9994c2a"
    )
    try:
        filename = core.retrieve_file(url, dir_name,
                                      content_type=ctype,
                                      content_length=clength,
                                      content_hash=chash)
    except core.Error as error:
        checked = False
        msg = "..Unexpected exception - {} - args : {}"
        logger.error(msg.format(error, error.args))
    else:
        pass
    print("Test #1 {}verified".format("" if checked else "not "))

    # Test 2 :
    try:
        filename = core.retrieve_file(url, dir_name)
    except core.Error as error:
        checked = False
        msg = "..Unexpected exception - {} - args : {}"
        logger.error(msg.format(error, error.args))
    else:
        pass
    print("Test #2 {}verified".format("" if checked else "not "))

    # - Unsupported hash -------------------------------------------------------
    chash = ("md6", "")
    try:
        filename = core.retrieve_file(url, dir_name,
                                      content_hash=chash)
    except core.Error as error:
        msg = "..Unexpected exception - {} - args : {}"
        logger.error(msg.format(error, error.args))
    else:
        pass
    print("Test Unsupported hash {}verified".format("" if checked else "not "))

    # - Bad hash ---------------------------------------------------------------
    chash = (
        "sha256",
        "c1ef9d41e122ceb242facab8755219a8ffa9b8a15321c352d0e95e1ac9994c2b"
    )
    try:
        filename = core.retrieve_file(url, dir_name,
                                      content_hash=chash)
    except core.UnexpectedContentError as error:
        pass
    else:
        checked = False
        msg = "..Bad hash must be rejected"
        logger.error(msg.format(error, error.args))
    print("Test Bad hash {}verified".format("" if checked else "not "))

    # - Bad content length------------------------------------------------------
    clength = 9891
    try:
        filename = core.retrieve_file(url, dir_name,
                                      content_length=clength)
    except core.UnexpectedContentLengthError as error:
        pass
    else:
        checked = False
        msg = "..Bad content length must be rejected"
        logger.error(msg.format(error, error.args))
    print("Test content length {}verified".format("" if checked else "not "))

    # - Bad content type------------------------------------------------------
    ctype = "unknown/vnd"
    try:
        filename = core.retrieve_file(url, dir_name,
                                      content_type=ctype)
    except core.UnexpectedContentTypeError as error:
        pass
    else:
        checked = False
        msg = "..Bad content type must be rejected"
        logger.error(msg.format(error, error.args))
    print("Test content type {}verified".format("" if checked else "not "))

    # - unknown content length (no header)--------------------------------------
    # no known url