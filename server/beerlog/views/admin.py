import json
import hashlib

from sqlobject import SQLObjectNotFound
from flask import request, make_response
from flask.views import MethodView

from beerlog.models.admin import User, AuthToken
from beerlog.utils.wrappers import require_admin, require_auth
from beerlog.utils.flaskutils import sqlobject_to_dict
from beerlog.settings import PASSWORD_SALT as salt

class UserAPI(MethodView):


    def get(self, user_id):
        if user_id is None:
            return json.dumps([sqlobject_to_dict(user) for user in User.select()])
        else:
            return json.dumps(sqlobject_to_dict(User.get(id=user_id)))

    def post(self):
        if request.json:
            pass
        else:
            return make_response('Bad request', 400)

    def put(self, user_id):
        if user_id is not None:
            return 'updating user %s' % user_id

    def delete(self, user_id):
        if user_id is not None:
            return 'deleteing user %s' % user_id

class LoginAPI(MethodView):


    def send_405(self):
        resp = make_response('Method not allowed', 405)
        resp.headers['Allow'] = 'POST'
        return resp

    def get(self, user_id):
        return self.send_405()

    def delete(self, user_id):
        return self.send_405()

    def put(self, user_id):
        return self.send_405()

    def post(self):
        if request.json:
            email = request.json['email']
            password = request.json['password']

            try:
                salted = hashlib.sha256("%s%s" % (salt, password)).hexdigest()
                user = User.select(User.q.email==email)[0]
                if user.password == salted:
                    token = {"token": user.get_token()}
                    return json.dumps(token)
                else:
                    raise SQLObjectNotFound
            except SQLObjectNotFound, IndexError:
                return make_response("Not authorized", 401)
        else:
            return make_response('Bad request', 400)