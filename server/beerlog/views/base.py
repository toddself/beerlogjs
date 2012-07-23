# -*- coding: utf-8 -*-
"""
    beerlog.views.base
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
        return ''.join(BeautifulSoup(text).findAll(text=True))

    def send_status_code(self, code, msg=""):
        beerlog.app.logger.info('sending response %s' % code)
        return make_response(msg, code)

    def mk_msg(self, msg):
        if msg:
            msg = ": %s" % msg
        return msg

    def ensure_json(self, data):
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        return data

    def send_200(self, data, mime_type="application/json"):
        beerlog.app.logger.info("sending 200")
        if "json" in mime_type:
            data = self.ensure_json(data)
        resp = self.send_status_code(200, data)
        resp.headers["Content-Type"] = mime_type
        return resp

    def send_201(self, data, mime_type="application/json"):
        if "json" in mime_type:
            data = self.ensure_json(data)
        resp = self.send_status_code(201, data)
        resp.headers["Content-Type"] = mime_type
        return resp

    def send_400(self, msg=""):
        return self.send_status_code(400, "Bad request%s" % self.mk_msg(msg))

    def send_401(self, msg=""):
        return self.send_status_code(401, "Not Authorized%s", self.mk_msg(msg))

    def send_404(self, msg=""):
        return send_status_code(404, "Not found%s" % self.mk_msg(msg))

    def send_405(self, msg=""):
        resp = self.send_status_code(405,
                                     "Method not allowed%s" % self.mk_msg(msg))
        resp.headers['Allow'] = ",".join([m.upper() for m in self.allowed])
        return resp

    def get(self, item_id):
        return self.send_405()

    def post(self):
        return self.send_405()

    def put(self, item_id):
        return self.send_405()

    def delete(self, item_id):
        return self.send_405()