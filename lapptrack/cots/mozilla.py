"""
This module is the product handler of Mozilla products (Firefox, Thunderbird).
The `background_firefox` section gives more information about the installation
process and the update mechanism.

.. todo:: use the 6th schema

.. todo:: take into account only complete update

.. todo:: do an mozilla common class (add buildID) derived for firefox win 64
   fr, thunderbird win 64 fr avec OSsystem, local en attributs public


Public Classes
--------------
This module has only one public class.

===================================  ===================================
:class:`FirefoxHandler`              :class:`ThunderbirdHandler`
:class:`MozHandler`                  ..
===================================  ===================================
"""

import datetime
import logging
import re
import os
import tempfile
import urllib.error

from lxml import etree

from cots import core
from support import semver

__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"
__all__ = [
    "FirefoxHandler",
    "ThunderbirdHandler",
    "MozHandler"
]
# To make the module as versatile as possible, an nullHandler is added.
# see 'Configuring Logging for a Library'
# docs.python.org/3/howto/logging.html# configuring-logging-for-a-library
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class MozHandler(core.BaseProduct):
    """
    Base class for Mozilla product handler.

    This base class implements the common parts of the tracking mechanism for
    all Mozilla products. So most of information are in the :mod:`core` and
    more particularly in the `BaseProduct` class documentation. The information
    below focuses on the added value of this class.
    
    This base class is not designed to work as it is. The following attributes
    must be defined before calling any method:
     
    * :attr:`~cots.core.BaseProduct.name`
    * :attr:`~cots.core.BaseProduct.version`
    * :attr:`~cots.core.BaseProduct.target`
    * :attr:`~cots.mozilla.MozHandler.locale`
    * :attr:`~cots.mozilla.MozHandler.build_id`

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `get_origin`                         `is_update`
        ===================================  ===================================
    """
    #: dict: The list of the supported build target. Each entry is a 2-tuple
    #: containing the build target identifier et its display form.
    BUILD_TARGET = {
        "win": ("WINNT_x86-msvc", "x86"),
        "win64": ("WINNT_x86_64-msvc-x64", "x64")
    }

    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        super().__init__()

        #: str: The locale of the application as specified in the `Locale Codes
        #: <https://wiki.mozilla.org/L10n:Locale_Codes>`_ wiki page
        self.locale = ""
        #: str: The build ID of the application.
        self.build_id = ""

        msg = "<<< ()=None"
        _logger.debug(msg)

    def get_origin(self, version=None):
        """
        Get product information from the remote repository.

        Args:
            version (str): The version of the reference product (i.e. the
                deployed product). It'a string following the editor versioning
                rules.

        Returns:
            bool: True if the download of the file went well. In case of
            failure, the members are not modified and an error log is written.

        Raises:
            TypeError: Parameters type mismatch.
            ValueError: unsupported attributes values.
        """
        msg = ">>> (version={})".format(version)
        _logger.debug(msg)

        # check parameters type
        if version is not None and not isinstance(version, str):
            msg = "version argument must be a class 'str' or None. " \
                  "not {0}".format(version.__class__)
            raise TypeError(msg)

        if self.target in self.BUILD_TARGET:
            build_target, display_target = self.BUILD_TARGET[self.target]
        else:
            msg = "{} is not a supported target.".format(self.target)
            raise ValueError(msg)

        msg = "Fetching the latest product information since the version " \
              "{}".format(self.version)
        _logger.info(msg)
        result = True

        try:
            url = self._get_update_url()
            with tempfile.NamedTemporaryFile(delete=False) as file:
                local_filename = file.name
                core.retrieve_file(url, file)
        except urllib.error.URLError as err:
            msg = "Inaccessible resource: {} - " \
                  "url: {}".format(str(err), self.location)
            _logger.error(msg)
            result = False
        except (core.ContentTypeError, core.ContentLengthError,
                core.ContentError) as err:
            msg = "Unexpected content: {}".format(str(err))
            _logger.error(msg)
            result = False
        except ValueError as err:
            msg = "Internal error: {}".format(str(err))
            _logger.error(msg)
            result = False
        except OSError as err:
            msg = "OS error: {}".format(str(err))
            _logger.error(msg)
            result = False
        else:
            msg = "Catalog downloaded: '{0}'".format(local_filename)
            _logger.debug(msg)

        if result:
            try:
                t = etree.parse(local_filename) # parse the manifest file
            except:
                pass
            else:
                e = t.xpath("/updates/update")
                if len(e):
                    self.version = e[0].get("appVersion")
                    self.build_id = e[0].get("buildID")
                    self.release_note_location = e[0].get("detailsURL")

                    server = "download.mozilla.org"
                    self.location = \
                        "https://{server}/?product={product}-{version}" \
                        "&os={target}&lang={locale}".format(
                            server=server,
                            product=self.name,
                            version=self.version,
                            target=self.target,
                            locale=self.locale
                        )

                    self.display_name = "Mozilla {} {} ({} {})".format(
                        self.name.capitalize(),
                        self.version,
                        display_target,
                        self.locale
                    )
                    # The manifest file does not contain the release date (i.e
                    # date of publication on the Release channel). So the
                    # publication date is built from the build ID.
                    dt = datetime.datetime.strptime(self.build_id,
                                                    "%Y%m%d%H%M%S")
                    self.published = dt.isoformat()
                    self.change_summary = ""
                    self.file_size = -1
                    self.secure_hash = None
                    self.std_inst_args = ""
                    self.silent_inst_args = "-ms"

                    msg = "Latest product information fetched ({} published " \
                          "on {})".format(self.version, self.published)
                    _logger.info(msg)
                else:
                    msg = "No available update for Mozilla {} {}"\
                        .format(self.name.capitalize(), self.version)
                    _logger.info(msg)

        # clean up the temporary files
        try:
            os.remove(local_filename)
        except OSError:
            pass

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def is_update(self, product):
        """
        Return if this instance is an update of product.

        This method compare the version of the two product, and return the
        comparison result. The version numbers used by the editor are compliant
        with the semantic versioning specification 2.0.0 (see `support.semver`
        module)

        Args:
            product (BaseProduct): The reference product (i.e. the deployed one)

        Returns:
            bool: True if this instance is an update of the product specified
            by the `product` parameter.

        Raises:
            TypeError: Parameters type mismatch.
        """
        msg = ">>> (product={})"
        _logger.debug(msg.format(product))

        # check parameters type
        if not isinstance(product, MozHandler):
            msg = "product argument must be a class 'MozHandler'. not {0}"
            msg = msg.format(product.__class__)
            raise TypeError(msg)

        # comparison based on version number.
        result = True
        try:
            a = semver.SemVer(self.version)
            b = semver.SemVer(product.version)
        except ValueError as err:
            msg = "Internal error: current product version - {}"
            _logger.error(msg.format(str(err)))
            result = False
        else:
            result = bool(a > b)

        if result:
            msg = "It is an update ({} vs. {})."
            _logger.info(msg.format(self.version, product.version))
        else:
            msg = "{} is not an update."
            _logger.info(msg.format(self.version))

        msg = "<<< ()={}"
        _logger.debug(msg.format(result))
        return result

    def _get_update_url(self):
        """
        Return the update request URL for the Mozilla update servers.

        The handler is compliant with the version 6 of the request. The 
        section :ref:`background_firefox.update_request` details the URL
        parts. For now, the handler only supports the Windows version of Mozilla 
        products.
        
        To use
        
        Returns:
            str: the URL of update request.

        Raises:
            TypeError: Parameters type mismatch.
            ValueError: unsupported attributes values.
        """
        msg = ">>> ()"
        _logger.debug(msg)

        assert self.name, "Name attribute must be defined"
        assert self.version, "Version attribute must be defined"
        assert self.target, "Target attribute must be defined"
        assert self.build_id, "Build Id attribute must be defined"
        assert self.locale, "Locale attribute must be defined"

        if self.target in self.BUILD_TARGET:
            build_target, display_target = self.BUILD_TARGET[self.target]
        else:
            msg = "{} is not a supported target.".format(self.target)
            raise ValueError(msg)

        server = "aus5.mozilla.org"
        channel = "release"
        os_version = "Windows_NT%206.1"  # windows 7 min
        system_caps = "%20" # vs SSE
        distribution = "default"
        dist_version = "default"

        url = \
            "https://{server}/update/6/{product}/{version}/{build_id}/" \
            "{build_target}/{locale}/{channel}/{os_version}/" \
            "{system_capabilities}/{distribution}/{dist_version}" \
            "/update.xml?force=1".format(
                server=server,
                product=self.name,
                version=self.version,
                build_id=self.build_id,
                build_target=build_target,
                locale=self.locale,
                channel=channel,
                os_version=os_version,
                system_capabilities=system_caps,
                distribution=distribution,
                dist_version=dist_version
            )

        msg = "<<< ()={}"
        _logger.debug(msg.format(url))
        return url


class FirefoxWinHandler(MozHandler):
    """
    Firefox product handler.

    This concrete class implements the tracking mechanism for the Mozilla 
    Firefox product (Windows version). So most of information are in the 
    :mod:`core` and more particularly in the `BaseProduct` class documentation. 
    The information below focuses on the added value of this class.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `get_origin`                         `is_update`
        ===================================  ===================================

    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        super().__init__()

        # Default value
        #  - General -
        self.name = "firefox"
        self.display_name = ""
        self.version = "42.0"
        self.published = ""
        #  - Details -
        self.target = "win"
        self.description = "Firefox is a free and open-source web browser " \
                           "available under the Mozilla Public License"
        self.editor = "Mozilla Foundation"
        self.web_site_location = "https://www.mozilla.org/firefox"
        self.icon = ""
        self.announce_location = ""
        self.feed_location = ""
        self.release_note_location = ""
        # - Change summary -
        self.change_summary = ""
        # - Installer
        self.location = ""
        self.installer = ""
        self.file_size = -1
        self.secure_hash = None
        self.silent_inst_args = "-ms"
        self.std_inst_args = ""
        # - Mozilla -
        self.build_id = "20151029151421"
        self.locale = "fr"

        msg = "<<< ()=None"
        _logger.debug(msg)


class FirefoxWin64Handler(MozHandler):
# since the 42.0 (2/nov/2015)
    """
    Firefox product handler.
    
    This concrete class implements the tracking mechanism for the Mozilla 
    Firefox product (Windows 64 bits version). So most of information are in the 
    :mod:`core` and more particularly in the `BaseProduct` class documentation. 
    The information below focuses on the added value of this class.
    
    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.
    
        ===================================  ===================================
        `get_origin`                         `is_update`
        ===================================  ===================================
    
    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        super().__init__()

        # Default value
        #  - General -
        self.name = "firefox"
        self.display_name = ""
        self.version = "42.0"
        self.published = ""
        #  - Details -
        self.target = "win64"
        self.description = "Firefox is a free and open-source web browser " \
                           "available under the Mozilla Public License"
        self.editor = "Mozilla Foundation"
        self.web_site_location = "https://www.mozilla.org/firefox"
        self.icon = ""
        self.announce_location = ""
        self.feed_location = ""
        self.release_note_location = ""
        # - Change summary -
        self.change_summary = ""
        # - Installer
        self.location = ""
        self.installer = ""
        self.file_size = -1
        self.secure_hash = None
        self.silent_inst_args = "-ms"
        self.std_inst_args = ""
        # - Mozilla -
        self.build_id = "20151029151421"
        self.locale = "fr"

        msg = "<<< ()=None"
        _logger.debug(msg)


class ThunderbirdWinHandler(MozHandler):
    """
    Firefox product handler.

    This concrete class implements the tracking mechanism for the Mozilla 
    Firefox product (Windows 64 bits version). So most of information are in the 
    :mod:`core` and more particularly in the `BaseProduct` class documentation. 
    The information below focuses on the added value of this class.

    **Overridden Methods**
        This class is a concrete class, so the overridden methods are listed
        below in alphabetical order.

        ===================================  ===================================
        `get_origin`                         `is_update`
        ===================================  ===================================

    """
    def __init__(self):
        msg = ">>> ()"
        _logger.debug(msg)
        super().__init__()

        # Default value
        #  - General -
        self.name = "thunderbird"
        self.display_name = ""
        self.version = "1.0"
        self.published = ""
        #  - Details -
        self.target = "win"
        self.description = "Firefox is a free and open-source web browser " \
                           "available under the Mozilla Public License"
        self.editor = "Mozilla Foundation"
        self.web_site_location = "https://www.mozilla.org/thunderbird"
        self.icon = ""
        self.announce_location = ""
        self.feed_location = ""
        self.release_note_location = ""
        # - Change summary -
        self.change_summary = ""
        # - Installer
        self.location = ""
        self.installer = ""
        self.file_size = -1
        self.secure_hash = None
        self.silent_inst_args = "-ms"
        self.std_inst_args = ""
        # - Mozilla -
        self.build_id = "0"
        self.locale = "fr"

        msg = "<<< ()=None"
        _logger.debug(msg)
