"""
This module defines functions and classes which implement a flexible progress
bar widget.

To date, the module provides only widgets for text user interfaces (i.e. for
a terminal).


Public Classes
--------------
This module is built around two main parts: the first one is the **manager**;
the second one is a collection of **widgets** which manages the way
by which the progression is going to be displayed.

The **manager** has only on public class.

===================================  ===================================
`ProgressIndicatorWidget`            ..
===================================  ===================================

To date, the module includes a number of **widgets** listed below in
alphabetical order. A handler is a derived class from the `BaseWidget`
class.

.. hlist::
    :columns: 2

    * :class:`DurationWidget`
    * :class:`ETAWidget`
    * :class:`IndeterminateProgressBarWidget`
    * :class:`PercentWidget`
    * :class:`PrefixedQuantityWidget`
    * :class:`PrefixedValueWidget`
    * :class:`ProgressBarWidget`
    * :class:`RateWidget`
    * :class:`ScrollingTextWidget`
    * :class:`SeparatorWidget`
    * :class:`SpinningWheelWidget`
    * :class:`ValueWidget`


Public Functions
----------------
This module has has a number of functions listed below in alphabetical order.

.. hlist::
    :columns: 2

    * :func:`isu_format_prefix`
    * :func:`new_download_throbber`
    * :func:`new_download_progress`
    * :func:`new_download_null`

"""

import logging
import time
import shutil
from collections import deque

__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "isu_format_prefix",
    "new_download_throbber",
    "new_download_progress",
    "new_download_null",
    "ProgressIndicatorWidget",
    "WidgetsCollection",
    "BaseWidget",
    "PercentWidget",
    "RateWidget",
    "ETAWidget",
    "DurationWidget",
    "ValueWidget",
    "PrefixedValueWidget",
    "PrefixedQuantityWidget",
    "ProgressBarWidget",
    "IndeterminateProgressBarWidget",
    "SpinningWheelWidget",
    "SeparatorWidget",
    "ScrollingTextWidget",
    "widget_classes_available",
]

# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html# configuring-logging-for-a-library
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
    msg = ">>> (value={}, unit={})"
    _logger.debug(msg.format(value, unit))
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

    result = "----" + unit
    r = float(value)
    for prefix in ["", "k", "M", "G", "T", "P", "E", "Z", "Y"]:
        if abs(r) < 1000.0:
            if abs(r) < 10.0:
                result = "{:>1.2f}\N{NBSP}{}{}".format(r, prefix, unit)
            elif abs(r) < 100.0:
                result = "{:>2.1f}\N{NBSP}{}{}".format(r, prefix, unit)
            else:
                result = "{:>4.0f}\N{NBSP}{}{}".format(r, prefix, unit)
            break
        else:
            r /= 1000.0
    else:
        result = ">999\N{NBSP}{}{}".format(prefix, unit)

    msg = "<<< ()={}"
    _logger.debug(msg.format(result))
    return result


def new_download_throbber(title=""):
    """
    Returns a throbber indicator to monitor a download process.

    This widget uses the following widget with a width equal to the number
    of columns of the terminal: :class:`ScrollingTextWidget`,
    :class:`SpinningWheelWidget`, :class:`PrefixedValueWidget`,
    :class:`RateWidget`, :class:`DurationWidget`.

    Args:
        title (str): The title of the download. This string is displayed as a
            scrolling text if its length exceeds the :attr:`~ScrollingTextWidget
            .size` attribute. The `None` value

    Return:
        ProgressIndicatorWidget: a progress indicator designed to monitor
        a download process.

    Raises:
        TypeError: Parameters type mismatch.
    """
    msg = ">>> (title={})"
    _logger.debug(msg.format(title))

    # check parameters type
    if title and not isinstance(title, str):
        msg = "title argument must be a class 'str' or None. not {0}"
        msg = msg.format(title.__class__)
        raise TypeError(msg)

    unit = "B"  # value are expressed in bytes...
    running = [
        ScrollingTextWidget(title),
        SeparatorWidget(": "),
        SpinningWheelWidget(),
        SeparatorWidget(" "),
        PrefixedValueWidget(unit),
        SeparatorWidget(" - "),
        RateWidget(unit),
        SeparatorWidget(" - "),
        DurationWidget()
    ]
    completion = [
        SeparatorWidget(title),
        SeparatorWidget(": "),
        PrefixedQuantityWidget(unit),
        SeparatorWidget(" received in "),
        DurationWidget(),
        SeparatorWidget(" ("),
        RateWidget(unit),
        SeparatorWidget(")"),
    ]

    progress_bar = ProgressIndicatorWidget()
    for w in running:
        progress_bar.add_widget(w)
    for w in completion:
        progress_bar.add_widget(w, True)

    msg = "<<< ()={}"
    _logger.debug(msg.format(progress_bar))
    return progress_bar


def new_download_progress(title=""):
    """
    Returns a progress indicator to monitor a download process.

    This widget uses the following widget with a width equal to the number
    of columns of the terminal: :class:`ScrollingTextWidget`,
    :class:`SpinningWheelWidget`, :class:`PrefixedValueWidget`,
    :class:`RateWidget`, :class:`DurationWidget`.

    Args:
        title (str): The title of the download. This string is displayed as a
            scrolling text if its length exceeds the :attr:`~ScrollingTextWidget
            .size` attribute

    Return:
        ProgressIndicatorWidget: a progress indicator designed to monitor
        a download process.

    Raises:
        TypeError: Parameters type mismatch.
    """
    msg = ">>> (title={})"
    _logger.debug(msg.format(title))

    # check parameters type
    if title and not isinstance(title, str):
        msg = "title argument must be a class 'str' or None. not {0}"
        msg = msg.format(title.__class__)
        raise TypeError(msg)

    unit = "B"  # value are expressed in bytes...
    running = [
        ScrollingTextWidget(title),
        SeparatorWidget(": "),
        PercentWidget(),
        SeparatorWidget(" "),
        ProgressBarWidget(),
        SeparatorWidget(" "),
        ValueWidget(unit),
        SeparatorWidget(" - "),
        RateWidget(unit),
        SeparatorWidget(" - "),
        ETAWidget()
    ]
    completion = [
        SeparatorWidget(title),
        SeparatorWidget(": "),
        PrefixedQuantityWidget(unit),
        SeparatorWidget(" received in "),
        DurationWidget(),
        SeparatorWidget(" ("),
        RateWidget(unit),
        SeparatorWidget(")"),
    ]

    progress_bar = ProgressIndicatorWidget()
    for w in running:
        progress_bar.add_widget(w)
    for w in completion:
        progress_bar.add_widget(w, True)

    msg = "<<< ()={}"
    _logger.debug(msg.format(progress_bar))
    return progress_bar


def new_download_null(title=""):
    """
    Returns a progress indicator to monitor a download process.

    This widget uses no widget. This is useful for very small downloads (a few
    kilobytes).

    Args:
        title (str): The title of the download. This string is not used, it is
            present only for the consistency with the other factory function.

    Return:
        ProgressIndicatorWidget: a progress indicator designed to monitor
        a download process.

    Raises:
        TypeError: Parameters type mismatch.
    """
    msg = ">>> (title={})"
    _logger.debug(msg.format(title))

    # check parameters type
    if title and isinstance(title, str):
        msg = "title argument must be a class 'str' or None. not {0}"
        msg = msg.format(title.__class__)
        raise TypeError(msg)

    progress_bar = ProgressIndicatorWidget()

    msg = "<<< ()={}"
    _logger.debug(msg.format(progress_bar))
    return progress_bar


class ProgressIndicatorWidget(object):
    """
    Progress indicator.

    This class is the manager of the `progress indicator`. This latter is a
    element of a textual user interface and it's made of a set of elementary
    widget such as a `progress bar <ProgressBarWidget>` or a `transfer rate
    indicator <RateWidget>` (see `widget_classes_available` to have the current
    list of available widgets.

    Args:
        width (int): The width of the progress indicator expressed in
            characters. The resulting string of the concatenation of strings
            returned by each widget is left justified in a string of length
            *width*. The `None` object means that the width will set to number
            of columns of the terminal.

    Raises:
        TypeError: Parameters type mismatch.

    **Public Methods**
        This class has a number of public methods listed below.

        .. hlist::
            :columns: 2

            * :class:`~ProgressIndicatorWidget.start`
            * :class:`~ProgressIndicatorWidget.update`
            * :class:`~ProgressIndicatorWidget.finish`
            * :class:`~ProgressIndicatorWidget.add_widget`

    **Using ProgressIndicatorWidget...**
        After created a class instance, you add one or more elementary widget to
        the progress indicator by calling the `add_widget` method. If this step
        is ignored, the progress indicator will be an empty string.
        After this step, you must call the `start` method to initialise the
        widget with the lowest and the highest value of the monitored quantity.
        At each change of the value, you call the `update` method to print the
        progress bar on the standard output (`sys.stdout`). When the task
        completed, you call the `finish` method.

        Example of fetching a file
            .. code-block:: python

                import urllib.request
                from support import progressindicator

                progress = progressindicator.ProgressIndicatorWidget(72)
                widget = progressindicator.SeparatorWidget(
                    symbol="python-3.5.1-docs-text.zip: "
                )
                progress.add_widget(widget)
                widget = progressindicator.PercentWidget()
                progress.add_widget(widget)
                widget = progressindicator.ProgressBarWidget()
                progress.add_widget(widget)

                widget = progressindicator.SeparatorWidget(
                    symbol="python-3.5.1-docs-text.zip: "
                )
                progress.add_widget(widget, True)
                widget = progressindicator.PrefixedQuantityWidget(symbol="B")
                progress.add_widget(widget, True)

                url = "https://docs.python.org/release/3.5.1/" \\
                      "archives/python-3.5.1-docs-text.zip"
                with urllib.request.urlopen(url) as stream:
                    content_length = int(stream.info()["Content-Length"])
                    length = 0
                    progress.start(length, content_length)
                    progress.update(length)
                    while True:
                        data = stream.read(1500)
                        if not data:
                            break
                        length += len(data)
                        progress.update(length)
                    progress.finish(length)
     """

    def __init__(self, width=None):
        msg = ">>> ()"
        _logger.debug(msg)

        # check parameters type
        if width and not isinstance(width, int):
            msg = "width argument must be a class 'int' or None. not {0}"
            msg = msg.format(width.__class__)
            raise TypeError(msg)

        #: `float`: The delay between two update of the display expressed in
        #: fraction of second. The default value is 8 times per seconds
        #: (0.125 s)
        self.refreshment_threshold = 1/8

        #: `int`: The width of the progress indicator expressed in characters.
        #: The resulting string of the concatenation of strings returned by each
        #: widget is left justified in a string of length *width*.
        self.width = width
        if self.width is None:
            self.width = shutil.get_terminal_size().columns

        self._t0 = 0.0  # Internal clock marking the starting point
        self._t1 = 0.0  # Internal clock marking the last refreshing point
        self._duration = 0.0
        self._dyn_range = 0.0
        self._offset = 0.0
        self._normal_value = 0.0

        # The maximum width of widget collection is set to the terminal size
        # minus one to take into account the carriage return (see `update`)
        self._running_widgets = WidgetsCollection(self.width - 1)
        self._completion_widgets = WidgetsCollection(self.width - 1)
        self._counter = 0

        msg = "<<< ()=None"
        _logger.debug(msg)

    def start(self, minimum=0.0, maximum=float("inf")):
        """
        Start the progress indicator widget.

        Args:
            minimum (int or float): The lowest value of the measured quantity.
            maximum (int or float): The highest value of the measured quantity.
                This value must be greater than the *minimum* parameter. The
                special value "inf" specify that the highest is unknown, so the
                relative widget will not be displayed.

        Raises:
            TypeError: Parameters type mismatch.
            ValueError: Unsupported attributes values
        """
        msg = ">>> (minimum={}, maximum={})"
        _logger.debug(msg.format(minimum, maximum))
        # check parameters type
        if not isinstance(minimum, (int, float)):
            msg = "minimum argument must be a class 'int or 'float'. not {0}"
            msg = msg.format(minimum.__class__)
            raise TypeError(msg)

        if not isinstance(maximum, (int, float)):
            msg = "maximum argument must be a class 'int or 'float'. not {0}"
            msg = msg.format(maximum.__class__)
            raise TypeError(msg)

        if minimum > maximum:
            msg = "maximum argument must be greater than the minimum argument"
            raise ValueError(msg)

        self._dyn_range = maximum - minimum
        self._offset = -minimum
        self._t0 = time.perf_counter()
        self._counter = 0

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, value):
        """
        Update the progress indicator widget

        note:
            To prevent the update flicking, the refresh period is limited (see
            `refreshment_threshold` attribute).

        Args:
            value (int or float): The current value of the monitored quantity.

        Raises:
            TypeError: Parameters type mismatch.
            ValueError: Unsupported attributes values
        """
        msg = ">>> (value={})"
        _logger.debug(msg.format(value))

        # assert self._t0, "No previous call to start"

        # check parameters type
        if not isinstance(value, (int, float)):
            msg = "value argument must be a class 'int' or 'float'. not {0}"
            msg = msg.format(value.__class__)
            raise TypeError(msg)

        # normalisation
        self._normal_value = (value + self._offset) / self._dyn_range
        if self._normal_value < 0 or self._normal_value > 1:
            msg = "value argument is out of range ({})"
            raise ValueError(msg.format(self._normal_value))

        last_refresh = time.perf_counter() - self._t1
        if last_refresh > self.refreshment_threshold:
            self._t1 = time.perf_counter()
            self._duration = time.perf_counter() - self._t0
            self._counter = self._counter + 1

            if self._running_widgets.widgets:
                items = ["\r"]
                for h in self._running_widgets.widgets:
                    items.append(h.update(self._normal_value, self._dyn_range,
                                          value, self._duration, self._counter))
                widget = "".join(items)
                widget = widget.ljust(self.width)
                print(widget, end="")

        msg = "<<< ()=None"
        _logger.debug(msg)

    def finish(self, value):
        """
        Compute the progress bar completion and return the computed string.

        Args:
            value (int or float): The last value of the monitored quantity.

        Return:
            str: A string representing the progress information.
        """
        msg = ">>> (value={})"
        _logger.debug(msg.format(value))

        # assert self._t0, "No previous call to start"

        # check parameters type
        if not isinstance(value, (int, float)):
            msg = "value argument must be a class 'int' or 'float'. not {0}"
            msg = msg.format(value.__class__)
            raise TypeError(msg)

        # normalisation
        self._normal_value = (value + self._offset) / self._dyn_range
        if self._normal_value < 0 or self._normal_value > 1:
            msg = "value argument is out of range"
            raise ValueError(msg)

        self._t1 = time.perf_counter()
        self._duration = time.perf_counter() - self._t0
        self._counter = self._counter + 1

        if self._completion_widgets.widgets:
            items = ["\r"]
            for h in self._completion_widgets.widgets:
                items.append(h.update(self._normal_value, self._dyn_range,
                                      value, self._duration, self._counter))
            widget = "".join(items)
            widget = widget.ljust(self.width)
        else:
            widget = ""
        print(widget)

        msg = "<<< ()={}"
        _logger.debug(msg.format(widget))
        return widget

    def add_widget(self, widget, is_completion=False):
        """
        Add an elementary widget to update the progress indicator widget.

        Args:
            widget (BaseWidget): The widget to add. It must be an instance of
                the `BaseWidget` class.
            is_completion (bool): `False` indicate that the widget will be added
                to the list of widget used when calling the 
                `ProgressIndicatorWidget.update` method

        Raises:
            TypeError: Parameters type mismatch.
            ValueError: Unsupported attributes values
        """
        msg = ">>> (widget={}, is_completion={})"
        _logger.debug(msg.format(widget, is_completion))

        # To prevent an overload of the :attr:`BaseWidget.size`, each widget
        # class instance must be unique.
        if widget in self._running_widgets.widgets:
            msg = "widget instance already exist in the running list"
            raise ValueError(msg)
        if widget in self._completion_widgets.widgets:
            msg = "widget instance already exist in the completion list"
            raise ValueError(msg)

        if is_completion:
            self._completion_widgets.add_widget(widget)
        else:
            self._running_widgets.add_widget(widget)

        msg = "<<< ()=None"
        _logger.debug(msg)


class WidgetsCollection(object):
    """
    Widgets collection

    Args:
        max_length (int): The authorised maximum length of the widgets string
            expressed in characters. This string is the concatenation of strings
            returned by each widget. The addition of a widget (see
            :meth:`add_widget`), whose length makes the length of the widgets
            string exceeding the *max_length*, raises an `ValueError` exception.

    Raises:
        TypeError: Parameters type mismatch.
        ValueError: Unsupported attributes values
    """
    def __init__(self, max_length):
        msg = ">>> (max_length={})"
        _logger.debug(msg.format(max_length))

        # check parameters type
        if not isinstance(max_length, int):
            msg = "max_length argument must be a class 'int'. not {0}"
            msg = msg.format(max_length.__class__)
            raise TypeError(msg)
        elif max_length < 0:
            msg = "max_length argument must be a positive integer (vs {})"
            msg = msg.format(max_length)
            raise TypeError(msg)

        #: `list`: The widgets list.
        self.widgets = []

        self._max_length = max_length

        msg = "<<< ()=None"
        _logger.debug(msg)

    def add_widget(self, widget):
        """
        Add an elementary widget to the collection.

        Args:
            widget (BaseWidget): The widget to add. It must be an instance of
                the `BaseWidget` class.

        Raises:
            TypeError: Parameters type mismatch.
            ValueError: Unsupported attributes values
        """
        # check parameters type
        msg = ">>> (widget={})"
        _logger.debug(msg.format(widget))

        # check parameters type
        if not isinstance(widget, BaseWidget):
            msg = "widget argument must be a class 'BaseWidget'"
            raise TypeError(msg)

        self.widgets.append(widget)

        # adjust the size of each variable-size widget
        size = 0
        var_size_widgets = []
        for w in self.widgets:
            if not w.is_fixed_size:
                var_size_widgets.append(w)
            else:
                size += w.size
        msg = "Progress indicator fixed size is {}/{}"
        _logger.debug(msg.format(size, self._max_length))
        if var_size_widgets:
            remain = int((self._max_length - size) / len(var_size_widgets))
            for w in var_size_widgets:
                w.size = remain
                size += w.size
                msg = "Resize the widget {} to {}"
                _logger.debug(msg.format(w.__class__, w.size))
        else:
            msg = "No widget to resize"
            _logger.debug(msg.format(widget))

        if size > self._max_length:
            msg = "Widget size exceeded the maximum length"
            raise ValueError(msg)

        msg = "<<< ()=None"
        _logger.debug(msg)


class BaseWidget(object):
    """
    Base class for all elementary widget.

    Args:
        symbol (str): The symbol of the unit.

    **Public Methods**
        This class has only one public method listed below.

        ===================================  ===================================
        :meth:`~BaseWidget.update`           ..
        ===================================  ===================================


    **Methods to Override**
        This class is a abstract class, so the following method must be
        overridden.

        ===================================  ===================================
         :meth:`~BaseWidget.update`          ..
        ===================================  ===================================
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))

        # check parameters type
        if not isinstance(symbol, str):
            msg = "symbol argument must be a class 'str'. not {0}"
            msg = msg.format(symbol.__class__)
            raise TypeError(msg)

        #: `bool`: The `True` value indicates that the widget have a fixed size
        #: specifying by the :attr:`size`. The `False` value indicates that the
        #: widget have a variable size. In that case, the size take into account
        #: the number of columns of the terminal.
        self.is_fixed_size = True
        #: `str`: the unit symbol of the measured quantity.
        self.symbol = symbol
        #: `int`: size of the widget expressed in characters.
        self.size = 0

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Update the elementary widget

        Args:
            normal_value (float): The normalised value of the progression. This
                value is between 0 and 1.
            dyn_range (float): The dynamics range of the
                monitored quantity. 
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        raise NotImplementedError


class PercentWidget(BaseWidget):
    """
    Widget to update the percentage of progress

    The printed string have the following content: ``nnn%`` where ``nnn``
    is the percentage of progress

    Args:
        symbol (str): The symbol of the unit. This string is not used in this
            context, because a percentage have no unit.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `int`: size of the widget expressed in characters.
        self.size = 4

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Display the elementary widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        if normal_value <= 0.0 or normal_value > 1.0:
            result = " --%"
        else:
            result = "{:>4.0%}".format(normal_value)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class RateWidget(BaseWidget):
    """
    Widget to update the rate of progress

    The printed string have the following content: ``rrrr XU/s`` where ``rrrr``
    is the rate. ``X`` represent a multiple of the unit (G, M or k) and ``U`` is
    the unit symbol.

    Args:
        symbol (str): The symbol of the unit.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `str`: the unit symbol of the rate value. By default, the rate is
        #:  expressed in unit per second.
        self.symbol = "{}/s".format(symbol)
        #: `int`: the size of the widget expressed in characters.
        self.size = 4 + 1 + 1 + len(self.symbol)

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Display the elementary widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        # update the rate
        if not duration:
            result = "---- {}".format(self.symbol)
        else:
            v = normal_value * dyn_range / duration
            result = isu_format_prefix(v, self.symbol)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class ETAWidget(BaseWidget):
    """
    Widget to update the estimated time to achieve the operation.

    The printed string have the following content: ``eta hh:mm:ss`` where
    ``hh:mm:ss`` is the estimated time to achieve the operation expressed in
    hour, minute and second.

    Args:
        symbol (str): The symbol of the unit. This string is not used in this
            context, because a time expression have no unit.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `int`: the size of the widget expressed in characters.
        self.size = 12

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Display the elementary widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        if normal_value <= 0.0 or normal_value > 1.0:
            result = "eta --:--:--"
        else:
            t = (1 / normal_value - 1) * duration
            h = int(t // 3600)
            r = int(t % 3600)
            m = int(r // 60)
            s = int(r % 60)
            result = "eta {:02d}:{:02d}:{:02d}".format(h, m, s)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class DurationWidget(BaseWidget):
    """
    Widget to update the operation duration.

    The printed string have the following content: ``hh:mm:ss`` where
    ``hh:mm:ss`` is the operation duration expressed in hour, minute and second.

    Args:
        symbol (str): The symbol of the unit. This string is not used in this
            context, because a time expression have no unit.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `int`: the size of the widget expressed in characters.
        self.size = 8

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Display the elementary widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        h = int(duration // 3600)
        r = int(duration % 3600)
        m = int(r // 60)
        s = int(r % 60)
        result = "{:02d}:{:02d}:{:02d}".format(h, m, s)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class ValueWidget(BaseWidget):
    """
    Widget to update the real value.

    The printed string have the following content: ``lll,lll,lll,lll U`` where
    ``lll,lll,lll,lll`` is the value of the progress and ``U`` is the unit
    symbol. The formatter uses the current locale setting to insert the
    appropriate number separator characters (see :mod:`string` module).

    Args:
        symbol (str): The symbol of the unit.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `str`: the unit symbol of the measured quantity.
        self.symbol = symbol
        #: `int`: the size of the widget expressed in characters.
        self.size = 15 + 1 + len(self.symbol)

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Display the elementary widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        # update the length of received data
        result = "{:>15n}\N{NBSP}{}".format(value, self.symbol)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class PrefixedValueWidget(BaseWidget):
    """
    Widget to update the real value using standard prefix for unit.

    The printed string have the following content: ``nnn XU`` where ``nnn``
    is a multiple of the value. ``X`` represent a multiple of the unit
    (G, M or k) and ``U`` is the unit symbol.

    Args:
        symbol (str): The symbol of the unit.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `str`: the unit symbol of the measured quantity.
        self.symbol = symbol
        #: `int`: the size of the widget expressed in characters.
        self.size = 4 + 1 + 1 + len(self.symbol)

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Display the elementary widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        result = isu_format_prefix(value, self.symbol)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class PrefixedQuantityWidget(BaseWidget):
    """
    Widget to update the monitored quantity using standard prefix for unit.

    The printed string have the following content: ``nnn XU`` where ``nnn``
    is a multiple of the value. ``X`` represent a multiple of the unit
    (G, M or k) and ``U`` is the unit symbol.

    Args:
        symbol (str): The symbol of the unit.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `str`: the unit symbol of the measured quantity.
        self.symbol = symbol
        #: `int`: the size of the widget expressed in characters.
        self.size = 4 + 1 + 1 + len(self.symbol)

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Display the elementary widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        v = normal_value * dyn_range
        result = isu_format_prefix(v, self.symbol)

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class ProgressBarWidget(BaseWidget):
    """
    Progress bar widget.

    This class implement a `progress bar` widget.

    The printed string have the following content:
    ``[==============              ]`` where ``=`` is a step of the progression.

    Args:
        symbol (str): The symbol of the unit. This string is not used in this
            context, because a *progress bar* have no unit.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `bool`: The `False` value indicates that the widget have a fixed size
        #: specifying by the :attr:`size`. The `True` value indicates that the
        #: widget have a variable size. In that case, the size take into account
        #: the number of columns of the terminal.
        self.is_fixed_size = False
        #: `str`: the unit symbol of the measured quantity.
        self.symbol = symbol
        #: `int`: the size of the widget expressed in characters.
        self.size = 0

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Update the Progress bar widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        if normal_value <= 0.0 or normal_value > 1.0:
            v = 0
        else:
            v = round(normal_value * (self.size-2))
        s = "="*v
        result = "["+s.ljust(self.size-2)+"]"

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class IndeterminateProgressBarWidget(BaseWidget):
    """
    Indeterminate progress bar widget.

    This class implement an indeterminate `progress bar` widget.

    The printed string have the following content:
    ``[ ****       ]`` where ``****`` is a maker moving from right to left.

    Args:
        symbol (str): The symbol of the unit. This string is not used in this
            context, because a *progress bar* have no unit.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `bool`: The `False` value indicates that the widget have a fixed size
        #: specifying by the :attr:`size`. The `True` value indicates that the
        #: widget have a variable size. In that case, the size take into account
        #: the number of columns of the terminal.
        self.is_fixed_size = False
        #: `str`: the unit symbol of the measured quantity.
        self.size = 0

        self._pattern = ""
        self._queue = deque(maxlen=4)

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Update the Progress bar widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        self._pattern = (self.size-2)*" "
        c = counter % len(self._pattern)
        s = self._pattern[:c]+"*"+self._pattern[c+1:]
        self._queue.append(s)

        # flatten the layers
        s = ""
        for i in range(0, len(self._pattern)):
            sub = self._pattern[i]
            for j in self._queue:
                if j[i] is not self._pattern[i]:
                    sub = j[i]
            s = s + sub
        result = "[" + s + "]"

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class SpinningWheelWidget(BaseWidget):
    """
    Spinning wheel widget.

    This class implement a `throbber` widget.

    Args:
        symbol (str): The symbol of the unit. This string is not used in this
            context, because a *spinning wheel* have no unit.
    """
    _CHARS = ("|", "/", "-", "\\")

    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `int`: the size of the widget expressed in characters.
        self.size = 3

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Update the Progress bar widget

        Args:
            normal_value (float): The normalized value of the monitored
                quantity. This value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (float): The number of seconds since the starting point
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))
        
        result = "[" + self._CHARS[counter % len(self._CHARS)] + "]"

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class SeparatorWidget(BaseWidget):
    """
    Widget to display a separator.

    Args:
        symbol (str): The separator.
    """
    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `str`: the separator.
        self.symbol = symbol
        #: `int`: the size of the widget expressed in characters.
        self.size = len(symbol)

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Display the elementary widget

        Args:
            normal_value (float): The normalized value of the progress. This
                value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (int): The number of seconds since the start
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        result = self.symbol

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


class ScrollingTextWidget(BaseWidget):
    """
    Widget to display a scrolling text.

    Args:
        symbol (str): The text.
    """

    def __init__(self, symbol=""):
        msg = ">>> (symbol={})"
        _logger.debug(msg.format(symbol))
        super().__init__(symbol)

        #: `str`: The text.
        self.symbol = symbol
        #: `int`: The size of the widget expressed in characters.
        self.size = 15

        self._is_scrolling = False
        if len(symbol) > self.size:
            self._is_scrolling = True
            self.symbol = symbol + ".     "

        msg = "<<< ()=None"
        _logger.debug(msg)

    def update(self, normal_value, dyn_range, value, duration, counter):
        """
        Display the elementary widget

        Args:
            normal_value (float): The normalized value of the progress. This
                value is between 0 and 1.
            dyn_range (float): The normalized maximum value of the
                monitored quantity.
            value (float): The real value of the progress
            duration (int): The number of seconds since the start
            counter (int): The number of call of the method. This counter may be
                useful to animate a `throbber`.

        Returns:
            str: a human readable string.
        """
        msg = ">>> (normal_value={}, dyn_range={}, " \
              "value={}, duration={}, counter={})"
        _logger.debug(msg.format(normal_value, dyn_range,
                                 value, duration, counter))

        if self._is_scrolling:
            pos = counter % len(self.symbol)
            result = (self.symbol[pos:] + self.symbol[:pos])[:self.size]
        else:
            result = self.symbol

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result


#: list: A set containing the class of the widget supported by this module on
#: all platforms.
widget_classes_available = [
    PercentWidget,
    RateWidget,
    ETAWidget,
    DurationWidget,
    ValueWidget,
    PrefixedValueWidget,
    PrefixedQuantityWidget,
    ProgressBarWidget,
    IndeterminateProgressBarWidget,
    SpinningWheelWidget,
    SeparatorWidget,
    ScrollingTextWidget,
]