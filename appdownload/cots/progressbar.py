"""
This module defines functions and classes to offer some progress bar in text
mode for the console.

Classes
    TextProgressBar: Progress bar for console output.
    
Exceptions
    None

Functions
    isu_format_prefix: return a string using standard prefix for unit.
    isu_format_thousand: return a string using standard ISU thousand
    separator.

Constants
    None

"""

import logging
import time


__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "TextProgressBar",
    "isu_format_prefix",
    "isu_format_thousand"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def isu_format_prefix(value, unit):
    """
    Return a string using standard prefix for unit.

    The returned string represent the value in a compliant International
    System of Units format, which means with a prefix for unit.
    (see https://en.wikipedia.org/wiki/International_System_of_Units)

    Parameters
        :param value: is the value to format (may be a float or an integer.
        :param unit: is a string representing the unit of the value.

        :return: is a string representing value (5.75 MB for example).
    """
    # check parameters type
    if not (isinstance(value, int) or isinstance(value, float)):
        msg = "value argument must be a class 'int' or 'float'. not {0}"
        msg = msg.format(value.__class__)
        raise TypeError(msg)
    # check parameters type
    if not isinstance(unit, str):
        msg = "unit argument must be a class 'str'. not {0}"
        msg = msg.format(unit.__class__)
        raise TypeError(msg)

    mul_unit = " " + "" + unit
    result = "----" + unit
    r = float(value)
    for prefix in ["", "k", "M", "G", "T", "P", "E", "Z", "Y"]:
        mul_unit = " " + prefix + unit
        if r < 1000.0:
            if r < 10.0:
                result = ("{:>1.2f}" + mul_unit).format(r)
            elif r < 100.0:
                result = ("{:>2.1f}" + mul_unit).format(r)
            else:
                result = ("{:>4.0f}" + mul_unit).format(r)
            break
        else:
            r /= 1000.0
    else:
        result = ">999 " + mul_unit

    return result


def isu_format_thousand(value):
    """
    Return a string using standard ISU thousand separator.

    The returned string represent the value in a compliant International
    System of Units format, which means with a space for thousand separator.
    (see https://en.wikipedia.org/wiki/International_System_of_Units)

    Parameters
        :param value: is the value to format (may be a float or an integer).

        :return: is a string representing value (5 000 for example).
    """
    # check parameters type
    if not (isinstance(value, int) or isinstance(value, float)):
        msg = "value argument must be a class 'int' or 'float'. not {0}"
        msg = msg.format(value.__class__)
        raise TypeError(msg)

    if isinstance(value, int):
        result = ("{:>,d}".format(value)).replace(",", " ")
    else:
        result = ("{:>,f}".format(value)).replace(",", " ")

    return result


class TextProgressBar:
    """
    Progress bar for console output.

    Public instance variables
        None

    Public methods
        compute: compute the progress bar and print it.
        finish: compute the completion progress bar and return the computed
        string.

    Subclass API variables (i.e. may be use by subclass)
        None

    Subclass API Methods (i.e. must be overwritten by subclass)
        None
    """

    def __init__(self, max_len=-1):
        """
        Constructor.

        Parameters
            :param max_len: is a positive integer specifying the content length
            that the progress bar is going to represent. A negative number
            specify that the content length is unknown.
        """
        # check parameters type
        if not isinstance(max_len, int):
            msg = "max_len argument must be a class 'int'. not {0}"
            msg = msg.format(max_len.__class__)
            raise TypeError(msg)

        self._t0 = time.time()
        self._length = 0
        self._content_length = max_len
        self._t1 = 0.0

    def compute(self, length, content_length=-1):
        """
        Compute the progress bar and print it.

        The printed string match the following format:
        aaa% [==============================] lll,lll,lll,lll - rrrr XB/s - eta nn:nn:nn
        aaa: is the percentage of progress
        ===: is the bar graph of progress (step=1/30)
        lll,lll,lll,lll: is the number of received bytes
        rrrr: is the bytes rate where X represent a multiple of the unit bytes
        per second (G, M or k).
        nn:nn:nn: is the estimated time to achieve the download.

        note : to prevent the display flicking, the refresh period is limited to
        4 time per second.

        Parameters
            :param length: is a positive integer specifying the length of
                received data.
            :param content_length: is a positive integer specifying the content
            length that the progress bar is going to represent. A negative
            number specify that the content length is unknown.
        """
        # check parameters type
        if not isinstance(length, int):
            msg = "length argument must be a class 'int'. not {0}"
            msg = msg.format(length.__class__)
            raise TypeError(msg)

        if not isinstance(content_length, int):
            msg = "content_length argument must be a class 'int'. not {0}"
            msg = msg.format(content_length.__class__)
            raise TypeError(msg)

        self._content_length = content_length
        self._length = length

        last_refresh = time.time() - self._t1
        if last_refresh > 0.25:
            self._t1 = time.time()
            # compute the rate
            base_unit = "B/s"
            duration = int(time.time() - self._t0)
            if duration != 0 and length != 0:
                rate = isu_format_prefix(length / duration, base_unit)
            else:
                rate = "----" + " " + "" + base_unit

            # compute the eta
            eta = "--:--:--"
            if length <= self._content_length and length != 0:
                t = (self._content_length - length) / length * duration
                h = int(t // 3600)
                r = int(t % 3600)
                m = int(r // 60)
                s = int(r % 60)
                eta = "{:02d}:{:02d}:{:02d}".format(h, m, s)

            # compute the percent
            bargraph = ""
            percent = " --%"
            if length <= self._content_length != 0:
                p = length / self._content_length
                percent = "{:>4.0%}".format(p)
                bargraph = "[" + ("=" * int(p * 30)).ljust(30) + "]"

            # compute the length of received data
            receive = isu_format_thousand(length).rjust(15)

            progress = "{} {} {} - {} - eta {}".format(percent, bargraph,
                                                       receive, rate, eta)
            print("\r" + progress, end="")

    def finish(self):
        """
        Compute the completion progress bar and return the computed string.

        The returned string match the following format:
        llll XB received - rrrr XB/s in nn:nn:nn
        lll XB: is the number of received bytes where X represent a multiple
        of the unit byte(G, M or k).
        rrrr: is the bytes rate where X represent a multiple of the unit bytes
        per second (G, M or k).
        nn:nn:nn: is the time of downloading.

        Parameters

            :return: is a string representing the progress information.
        """
        # compute the length of received data
        receive = isu_format_prefix(self._length, "B")

        # compute the rate
        base_unit = "B/s"
        duration = int(time.time() - self._t0)
        if duration != 0 and self._length != 0:
            rate = isu_format_prefix(self._length / duration, base_unit)
        else:
            rate = "----" + " " + "" + base_unit

        # compute the time
        h = int(duration // 3600)
        r = int(duration % 3600)
        m = int(r // 60)
        s = int(r % 60)
        eta = "{:02d}:{:02d}:{:02d}".format(h, m, s)

        progress = "{} received - {} in {}".format(receive, rate, eta)
        progress = progress.ljust(80)  # to overwrite the previous progress bar
        print("\r" + progress)
        return progress
