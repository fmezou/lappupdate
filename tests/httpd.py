"""
This module implement a simple HTTP server designed for testing purpose.

It may use as a module by a third party offering a new GUI for example, or as a
script with the command line interface::

    python -m httpd

Synopsis
--------

``httpd.py``


Description
-----------
This HTTP server accepts some special requests and returns either an error code
or data with specific HTTP headers.
"""
import http.server
import os
import urllib.parse

from http import HTTPStatus


__author__ = "Frederic MEZOU"
__version__ = "0.1.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


class MockHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Mocker HTTP request handler.

    This handler overwrite the `SimpleHTTPRequestHandler.send_head` method to
    altering the HTTP Headers. For this, the following virtual resources are
    defined:

    * *error*: this resource returns the HTTP error spécified by the code
      parameter (/error?code=500 for example)
    * *nolength*: this resource return the content of default file (lorem.txt)
      with no Content-Length header.
    * *notype*: this resource return the content of default file (lorem.txt)
      with no Content-Type header.
    * *increaselen*: this resource return the content of default file (lorem.txt)
      with Content-Length header increased (the real content length do not
      change).
    * *decreaselen*: this resource return the content of default file (lorem.txt)
      with Content-Length header decreased (the real content length do not
      change).

    In other cases, this serves files from the current directory and any of its
    subdirectories (topic `http.server.SimpleHTTPRequestHandler` details the
    behaviour).
    """
    def send_head(self):
        """
        Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Returns:
            file object: A file object (which has to be copied to the outputfile
            by the caller unless the command was HEAD, and must be closed by the
            caller under all circumstances), or None, in which case the caller
            has nothing further to do.
        """
        # filter the path
        file = None
        actions = {
            "/error": self.do_error,
            "/nolength": self.do_no_length,
            "/notype": self.do_no_type,
            "/increaselen": self.do_increase_length,
            "/decreaselen": self.do_decrease_length
        }
        components = urllib.parse.urlsplit(self.path)
        if components.path in actions:
            action = actions[components.path]
            file = action(components.query)
        else:
            file = super().send_head()

        return file

    def do_error(self, query):
        """
        Error virtual resource handling.

        Args:
            query (str): This is the query component of the URI.

        Returns:
            file object: A file object (which has to be copied to the outputfile
            by the caller unless the command was HEAD, and must be closed by the
            caller under all circumstances), or None, in which case the caller
            has nothing further to do.
        """
        k, v = query.split("=")
        if k == "code":
            if v.isdigit():
                code = int(v)
                if code in self.responses:
                    self.send_error(int(v))
                else:
                    self.log_message("Unknown error code: %s", v)
                    self.send_error(HTTPStatus.BAD_REQUEST)
            else:
                self.log_message("Erroneous error code: %s", v)
                self.send_error(HTTPStatus.BAD_REQUEST)
        else:
            self.log_message("Unknown query %s", query)
            self.send_error(HTTPStatus.BAD_REQUEST)

        return None

    def do_no_length(self, query):
        """
        No_length virtual resource handling.

        Args:
            query (str): This is the query component of the URI.

        Returns:
            file object: A file object (which has to be copied to the outputfile
            by the caller unless the command was HEAD, and must be closed by the
            caller under all circumstances), or None, in which case the caller
            has nothing further to do.
        """
        file = None
        try:
            path = os.path.join(os.path.dirname(__file__), "lorem.txt")
            file = open(path, "rb")
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/plain")
        st = os.fstat(file.fileno())
        self.log_message("Content-Length header not set")
        self.send_header("Last-Modified", self.date_time_string(st.st_mtime))
        self.end_headers()

        return file

    def do_increase_length(self, query):
        """
        Increase_length virtual resource handling.

        Args:
            query (str): This is the query component of the URI.

        Returns:
            file object: A file object (which has to be copied to the outputfile
            by the caller unless the command was HEAD, and must be closed by the
            caller under all circumstances), or None, in which case the caller
            has nothing further to do.
        """
        file = None
        try:
            path = os.path.join(os.path.dirname(__file__), "lorem.txt")
            file = open(path, "rb")
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/plain")
        st = os.fstat(file.fileno())
        self.send_header("Content-Length", str(st.st_size*2))
        self.log_message("Content-Length header altered (%s vs %s)",
                         st.st_size//2, st.st_size)
        self.send_header("Last-Modified", self.date_time_string(st.st_mtime))
        self.end_headers()

        return file

    def do_decrease_length(self, query):
        """
        Decrease_length virtual resource handling.

        Args:
            query (str): This is the query component of the URI.

        Returns:
            file object: A file object (which has to be copied to the outputfile
            by the caller unless the command was HEAD, and must be closed by the
            caller under all circumstances), or None, in which case the caller
            has nothing further to do.
        """
        file = None
        try:
            path = os.path.join(os.path.dirname(__file__), "lorem.txt")
            file = open(path, "rb")
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/plain")
        st = os.fstat(file.fileno())
        self.send_header("Content-Length", str(st.st_size//2))
        self.log_message("Content-Length header altered (%s vs %s)",
                         st.st_size//2, st.st_size)
        self.send_header("Last-Modified", self.date_time_string(st.st_mtime))
        self.end_headers()

        return file

    def do_no_type(self, query):
        """
        No_type virtual resource handling.

        Args:
            query (str): This is the query component of the URI.

        Returns:
            file object: A file object (which has to be copied to the outputfile
            by the caller unless the command was HEAD, and must be closed by the
            caller under all circumstances), or None, in which case the caller
            has nothing further to do.
        """
        file = None
        try:
            path = os.path.join(os.path.dirname(__file__), "lorem.txt")
            file = open(path, "rb")
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        self.send_response(HTTPStatus.OK)
        st = os.fstat(file.fileno())
        self.send_header("Content-Length", str(st.st_size))
        self.log_message("Content-Type header not set")
        self.send_header("Last-Modified",
                         self.date_time_string(st.st_mtime))
        self.end_headers()

        return file


def main():
    """
    Main entry point
    """
    server_address = ('localhost', 53230)
    httpd = http.server.HTTPServer(server_address, MockHTTPRequestHandler)
    print("serving at", server_address)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
