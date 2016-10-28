"""
This module defines functions and classes to offer progress bar widgets.

To date, the module provides text only widgets for the console.


Public Classes
--------------
This module has only one public class.


===================================  ===================================
`TextProgressBar`                    ..
===================================  ===================================


Public Functions
----------------
This module has has a number of functions listed below in alphabetical order.

===================================  ===================================
`isu_format_prefix`                  `isu_format_thousand`
===================================  ===================================


.. _International System of Units: https://en.wikipedia.org/wiki/
    International_System_of_Units
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

    The returned string represent the value in a compliant `International
    System of Units`_ format, which means with a prefix for unit.

    Args:
        value (int or float): The value to format.
        unit (str): The unit of the value.

    Return:
        str: a string representing the value ("5.75 MB" for example).

    Raises:
        TypeError: Parameters type mismatch.
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

    The returned string represent the value in a compliant `International
    System of Units`_ format, which means with a space for thousand separator.

    Args:
        value (int or float): The value to format.

    Return:
        str: a string representing value ("5 000" for example).

    Raises:
        TypeError: Parameters type mismatch.
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
    Progress bar for a console output.


    Args:
        max_len (int): A positive integer specifying the content length
            that the progress bar is going to represent. A negative number
            specify that the content length is unknown.


    **Public Methods**
        This class has a number of public methods listed below in alphabetical
        order.

        ===================================  ===================================
        `finish`                             `compute`
        ===================================  ===================================

    **Using TextProgressBar...**
        After created a class instance, you must call the `compute` method to
        print the progress bar on the standard output (`sys.stdout`) upon every
        change of the received length or the content length (typically after a
        reading of a data block from a stream) as shown in the below example.
        When the task completed, you must call the `finish` method which return
        a string summarizing the amount of computed data.

        Example of fetching a file
            .. code-block:: python

                import urllib.request
                import progressbar

                url  = "https://docs.python.org" \\
                       "/3/archives/python-3.5.1-docs-text.zip"
                with urllib.request.urlopen(url) as stream:
                    content_length = int(stream.info()["Content-Length"])
                    length = 0
                    progress_bar = progressbar.TextProgressBar(content_length)
                    progress_bar.compute(length, content_length)
                    while True:
                        data = stream.read(1024)
                        if not data:
                            break
                        length += len(data)
                        progress_bar.compute(length, content_length)
                    progress_bar.finish()
    """

    def __init__(self, max_len=-1):
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

        The printed string have the following content::

            aaa% [==============================] lll,lll,lll,lll - rrrr XB/s - eta nn:nn:nn

        where
            * ``aaa``: is the percentage of progress
            * ``===``: is the bar graph of progress (step=1/30)
            * ``lll,lll,lll,lll``: is the number of received bytes
            * ``rrrr``: is the bytes rate where X represent a multiple of the
              unit bytes per second (G, M or k).
            * ``nn:nn:nn``: is the estimated time to achieve the download.

        note:
            to prevent the display flicking, the refresh period is limited to
            4 times per second.


        Args:
            length (int): A positive integer specifying the length of
                received data.
            content_length (int): A positive integer specifying the content
                length that the progress bar is going to represent. A negative
                number specify that the content length is unknown.


        Raises:
            TypeError: Parameters type mismatch.
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
        Compute the progress bar completion and return the computed string.

        The returned string have the following content::

            llll XB received - rrrr XB/s in nn:nn:nn

        where
            * ``lll XB``: is the number of received bytes where X represent a
              multiple of the unit byte(G, M or k).
            * ``rrrr``: is the bytes rate where X represent a multiple of the
              unit bytes per second (G, M or k).
            * ``nn:nn:nn``: is the time of downloading.


        Return:
            str: A string representing the progress information.
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
