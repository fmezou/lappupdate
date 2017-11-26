"""
This module defines a test suite for testing the `support.progressindicator`
module.
"""

import logging
import unittest
import locale
import os
import shutil

from support import progressindicator

__author__ = "Frederic MEZOU"
__version__ = "0.1.0"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "ProgressIndicatorTestCase"
]

# Modules to be tested use the logging facility, so a minimal
# configuration is set. To avoid side effects with the `unittest`
# console output, log entries are written in a file.
_filename = os.path.basename(os.path.splitext(__file__)[0])+".log"
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s, line %(lineno)d, in %(funcName)s - %(message)s",
    filename=_filename,
    filemode="a",
    level=logging.INFO)
_logger = logging.getLogger(__name__)


class ProgressIndicatorTestCase(unittest.TestCase):
    def setUp(self):
        _logger.info(53*"-")
        self.ranges = [
            (0, 2000000, 2000000),
            (0.0, 2000000.0, 2000000),
            (-1000000.0, 1000000.0, 2000000),
            (-2100000.0, -100000.0, 2000000),
            (0.0, float("inf"), 2000000)
        ]

    def tearDown(self):
        _logger.info(50*"-")

    def test0101_running_widget_use_case(self):
        # Regular use case
        _logger.info("Starting...")

        for widget in progressindicator.widgets_available:
            with self.subTest(widget=widget):
                progress_bar = progressindicator.ProgressIndicatorWidget(120)
                progress_bar.add_widget(
                    progressindicator.SeparatorWidget(symbol=repr(widget)),
                    False
                )
                progress_bar.add_widget(
                    widget(symbol="B"),
                    False
                )
                for floor, ceiling, max_count in self.ranges:
                    with self.subTest(floor=floor, ceiling=ceiling):
                        progress_bar.start(floor, ceiling)
                        i, c = floor, 0
                        while c < max_count:
                            progress_bar.update(i)
                            i += 1
                            c += 1
                        progress_bar.finish(i)
                del progress_bar
        _logger.info("Completed")

    def test0102_completion_widget_use_case(self):
        # Regular use case
        _logger.info("Starting...")

        for widget in progressindicator.widgets_available:
            with self.subTest(widget=widget):
                progress_bar = progressindicator.ProgressIndicatorWidget(120)
                progress_bar.add_widget(
                    progressindicator.SeparatorWidget(symbol=repr(widget)),
                    True
                )
                progress_bar.add_widget(
                    widget(symbol="B"),
                    True
                )
                for floor, ceiling, max_count in self.ranges:
                    with self.subTest(floor=floor, ceiling=ceiling):
                        progress_bar.start(floor, ceiling)
                        i, c = floor, 0
                        while c < max_count:
                            progress_bar.update(i)
                            i += 1
                            c += 1
                        progress_bar.finish(i)
                del progress_bar
        _logger.info("Completed")

    def test0103_download_progress_indicator(self):
        # Regular use case
        _logger.info("Starting...")

        progress_bar = progressindicator.new_download_progress_indicator()
        max_count = 2000000
        progress_bar.start(0, max_count)
        i = 0
        while i < max_count:
            progress_bar.update(i)
            i += 1
        progress_bar.finish(i)
        del progress_bar
        _logger.info("Completed")

    def test0104_download_throbber_indicator(self):
        # Regular use case
        _logger.info("Starting...")

        progress_bar = progressindicator.new_download_throbber_indicator()
        max_count = 2000000
        progress_bar.start(0, max_count)
        i = 0
        while i < max_count:
            progress_bar.update(i)
            i += 1
        progress_bar.finish(i)
        del progress_bar
        _logger.info("Completed")

    def test0105_use_case_null(self):
        # Regular use case
        _logger.info("Starting...")

        progress_bar = progressindicator.ProgressIndicatorWidget()
        floor, ceiling, max_count = self.ranges[0]
        progress_bar.start(floor, ceiling)
        i = floor
        while i < max_count:
            progress_bar.update(i)
            i += 1
        progress_bar.finish(i)
        _logger.info("Completed")

    def test0201_init_unexpected_type(self):
        # Unexpected type for parameters in the constructor
        _logger.info("Starting...")
        with self.assertRaises(TypeError) as err:
            progressindicator.ProgressIndicatorWidget("")
        _logger.error("Type error: {}".format(err.exception))
        _logger.info("Completed")

    def test0301_start_unexpected_type(self):
        # Unexpected type for parameters in the start method
        _logger.info("Starting...")
        ranges = [
            (1, ""),
            ("", -1),
        ]
        progress_bar = progressindicator.ProgressIndicatorWidget()
        for f, c in ranges:
            with self.subTest(floor=f, ceiling=c):
                with self.assertRaises(TypeError) as err:
                    progress_bar.start(f, c)
            _logger.error("Type error: {}".format(err.exception))
        _logger.info("Completed")

    def test0301_start_unexpected_type(self):
        # Unexpected type for parameters in the start method
        _logger.info("Starting...")
        progress_bar = progressindicator.ProgressIndicatorWidget()
        with self.assertRaises(ValueError) as err:
            progress_bar.start(10, 1)
        _logger.error("Value error: {}".format(err.exception))
        _logger.info("Completed")

    def test0401_update_unexpected_type(self):
        # Unexpected type for parameters in the update method
        _logger.info("Starting...")
        floor, ceiling, max_count = self.ranges[0]
        progress_bar = progressindicator.ProgressIndicatorWidget()
        progress_bar.start(floor, ceiling)
        with self.assertRaises(TypeError) as err:
            progress_bar.update("")
        _logger.error("Type error: {}".format(err.exception))
        _logger.info("Completed")

    def test0402_update_out_of_range(self):
        # Unexpected type for parameters in the update method
        _logger.info("Starting...")
        floor, ceiling, max_count = self.ranges[0]
        progress_bar = progressindicator.ProgressIndicatorWidget()
        progress_bar.start(floor, ceiling)
        with self.assertRaises(ValueError) as err:
            progress_bar.update(ceiling+max_count)
        _logger.error("Value error: {}".format(err.exception))
        with self.assertRaises(ValueError) as err:
            progress_bar.update(floor-max_count)
        _logger.error("Value error: {}".format(err.exception))
        _logger.info("Completed")

    def test0501_finish_unexpected_type(self):
        # Unexpected type for parameters in the finish method
        _logger.info("Starting...")
        floor, ceiling, max_count = self.ranges[0]
        progress_bar = progressindicator.ProgressIndicatorWidget()
        progress_bar.start(floor, ceiling)
        with self.assertRaises(TypeError) as err:
            progress_bar.finish("")
        _logger.error("Type error: {}".format(err.exception))
        _logger.info("Completed")

    def test0502_finish_out_of_range(self):
        # Unexpected type for parameters in the finish method
        _logger.info("Starting...")
        floor, ceiling, max_count = self.ranges[0]
        progress_bar = progressindicator.ProgressIndicatorWidget()
        progress_bar.start(floor, ceiling)
        with self.assertRaises(ValueError) as err:
            progress_bar.finish(ceiling+1)
        _logger.error("Value error: {}".format(err.exception))
        with self.assertRaises(ValueError) as err:
            progress_bar.finish(floor-1)
        _logger.error("Value error: {}".format(err.exception))
        _logger.info("Completed")

    def test0601_widget_in_double(self):
        # Add a widget already added (duplicate)
        _logger.info("Starting...")
        for completion in (True, False):
            with self.subTest(is_completion=completion):
                progress_bar = progressindicator.ProgressIndicatorWidget()
                widget = progressindicator.PercentWidget()
                progress_bar.add_widget(widget, completion)
                with self.assertRaises(ValueError) as err:
                    progress_bar.add_widget(widget, completion)
                _logger.error("Value error: {}".format(err.exception))
                with self.assertRaises(ValueError) as err:
                    progress_bar.add_widget(widget, not completion)
                _logger.error("Value error: {}".format(err.exception))
                del widget
                del progress_bar
        _logger.info("Completed")

    def test0602_too_large_progress_indicator(self):
        # Make a progress indicator which exceeds the terminal width
        _logger.info("Starting...")
        width=shutil.get_terminal_size().columns
        for completion in (True, False):
            with self.subTest(is_completion=completion):
                progress_bar = progressindicator.ProgressIndicatorWidget()
                widget = progressindicator.SeparatorWidget("#"*width)
                with self.assertRaises(ValueError) as err:
                    progress_bar.add_widget(widget, completion)
                _logger.error("Value error: {}".format(err.exception))
                with self.assertRaises(ValueError) as err:
                    progress_bar.add_widget(widget, not completion)
                _logger.error("Value error: {}".format(err.exception))
                del widget
                del progress_bar
        _logger.info("Completed")


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, "")
    unittest.main()
