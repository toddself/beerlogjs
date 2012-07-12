import json
from flask import make_response

class APIBase(object):
    """Provides basic API functionality to method views"""

    def send_status_code(self, code, msg=""):
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

    def send_405(self, allowed=[], msg=""):
        resp = self.send_status_code(405,
                                     "Method not allowed%s" % self.mk_msg(msg))
        resp.headers['Allow'] = ",".join([method.upper() for method in allowed])
        return resp

    def get(self, item_id):
        return self.send_405()

    def post(self):
        return self.send_405()

    def put(self, item_id):
        return self.send_405()

    def delete(self, item_id):
        return self.send_405()