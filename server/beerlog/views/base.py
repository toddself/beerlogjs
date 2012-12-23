# -*- coding: utf-8 -*-
"""
    APIBase
    ~~~~~~~~~~~~

    Defines APIBase which provides:
         :meth:`clean_html`: removes all mark up from text
         :meth:`send_status_code`: sends a response object and HTTP status code
         :meth:`mk_msg`: formats a message for response
         :meth:`ensure_json`: makes sure dict & list are converted to json
         :meth:`send_*`: shortcut for sending a specific status and body

    This class also implements the basic requirments of the
    :meth:`flask.view.Methodview` class, and should be used as a mixin
    for that Class. By default returns a valid HTTP 405 response with no
    methods listed in the `ALLOWED` header. Defining a custom `allowed` list
    as a parameter on the class will explain to the :meth:`send_405` shortcut
    which methods this particular API supports

    :copyright: (c) 2012 by Todd Kennedy
    :license: BSD, see LICENSE for more details.
"""
import json

from flask import make_response
from bs4 import BeautifulSoup

import beerlog

class APIBase(object):
    allowed = []
    """Provides basic API functionality to method views"""

    def clean_html(self, text):
        """
            Returns all the text strings from an HTML file,
            stripping all HTML tags
        """
        return ''.join(BeautifulSoup(text).findAll(text=True))

    def send_status_code(self, code, msg=""):
        """
            Returns a response with a specific HTTP status code
        """
        return make_response(msg, code)

    def make_markdown(self, text):
        """
            Takes HTML as input and returns santized Markdown for storage in a
            database
        """
        converter = 'PATH_TO_PANDOC'
        cmd = [converter, '--strict', '-r', 'html', '-t', 'markdown']
        text_converter = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        markdown = text_converter.communicate(input=text)
        return self.clean_html(markdown)

    def mk_msg(self, msg):
        """
            Format a message
        """
        if msg:
            msg = ": %s" % msg
        return msg

    def ensure_json(self, data):
        """
            If the data isn't JSON and can be converted to JSON,
            convert it.
        """
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        return data

    def send_200(self, data, mime_type="application/json"):
        """ Return HTTP 200 with the object requested """
        if "json" in mime_type:
            data = self.ensure_json(data)
        resp = self.send_status_code(200, data)
        resp.headers["Content-Type"] = mime_type
        return resp

    def send_201(self, data, mime_type="application/json"):
        """ Return HTTP 201 (for POST) with the object created """
        if "json" in mime_type:
            data = self.ensure_json(data)
        resp = self.send_status_code(201, data)
        resp.headers["Content-Type"] = mime_type
        return resp

    def send_400(self, msg=""):
        """ Error out on a bad request """
        return self.send_status_code(400, "Bad request%s" % self.mk_msg(msg))

    def send_401(self, msg=""):
        """ Error out for bad credentials """
        return self.send_status_code(401, "Not Authorized%s", self.mk_msg(msg))

    def send_404(self, msg=""):
        """ Error out on a bad URL """
        return send_status_code(404, "Not found%s" % self.mk_msg(msg))

    def send_405(self, msg=""):
        """ Error out with a bad HTTP method """
        resp = self.send_status_code(405,
                                     "Method not allowed%s" % self.mk_msg(msg))
        resp.headers['Allow'] = ",".join([m.upper() for m in self.allowed])
        return resp

    def get(self, item_id):
        """ Shorthand default """
        return self.send_405()

    def post(self):
        """ Error out on a bad request """
        return self.send_405()

    def put(self, item_id):
        """ Error out on a bad request """
        return self.send_405()

    def delete(self, item_id):
        """ Error out on a bad request """
        return self.send_405()