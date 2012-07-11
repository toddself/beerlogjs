class APIBase(object):
    """Provides basic API functionality to method views"""

    def send_200(self, data):
        pass

    def send_201(self, data):
        pass

    def send_400(self, msg=""):
        pass

    def send_401(self, msg=""):
        resp = make_response('Not authorized: %s' % msg, 401)
        return resp

    def send_404(self, data):
        pass

    def send_405(self, allowed=[]):
        resp = make_response('Method not allowed', 405)
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