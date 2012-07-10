import json
import hashlib
from datetime import datetime

from sqlobject import SQLObjectNotFound
from flask import request, make_response
from flask.views import MethodView

from beerlog.models.admin import User, AuthToken
from beerlog.utils.wrappers import require_admin, require_auth
from beerlog.utils.flaskutils import sqlobject_to_dict, return_json
from beerlog.settings import PASSWORD_SALT as salt

class UserAPI(MethodView):


    def get(self, user_id):
        if user_id is None:
            userlist = [user.to_dict() for user in User.select()]
            return return_json(userlist)
        else:
            return return_json(User.get(user_id).to_json())

    def post(self):
        if request.json:
            # should not create user if this fails
            # needs to check data
            data = request.json
            email = data['email']
            password = data['password']
            first_name = data['first_name']
            last_name = data['last_name']
            alias = data['alias']
            user = User(email=email, first_name=first_name,
                        last_name=last_name, alias=alias)
            user.set_pass(salt, password)
            return return_json(sqlobject_to_dict(user))
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
                    user.last_login = datetime.now()
                    user_dict = sqlobject_to_dict(user)
                    user_dict['token'] = user.get_token()
                    return return_json(user_dict)
                else:
                    raise SQLObjectNotFound
            except SQLObjectNotFound, IndexError:
                return make_response("Not authorized", 401)
        else:
            return make_response('Bad request', 400)