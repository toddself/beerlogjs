import hashlib
from datetime import datetime
from urllib import quote

from formencode.api import Invalid as InvalidData
from sqlobject import SQLObjectNotFound
from sqlobject.dberrors import DuplicateEntryError
from flask import request, make_response, g
from flask.views import MethodView
from flaskext.mail import Message

from beerlog.models.admin import User, AuthToken, ResetToken, generate_password
from beerlog.utils.wrappers import require_auth
from beerlog.utils.flaskutils import sqlobject_to_dict, return_json
from beerlog.settings import PASSWORD_SALT as salt
from beerlog.settings import SITE_URL, SITE_NAME

class UserAPI(MethodView):
    decorators = [require_auth]

    def get(self, user_id):
        if user_id is None:
            userlist = [user.dict() for user in User.select()]
            return return_json(userlist)
        else:
            try:
                user = User.get(user_id)
            except SQLObjectNotFound:
                return make_response('Not found', 404)
            else:
                return return_json(user.json())

    def post(self):
        if request.json:
            try:
                data = request.json
                email = data['email']
                password = data['password']
                first_name = data['first_name']
                last_name = data['last_name']
                alias = data['alias']
            except KeyError, e:
                return make_response('Bad Request: %s is required' % e, 400)
            else:
                try:
                    user = User(email=email, first_name=first_name,
                                last_name=last_name, alias=alias)
                except DuplicateEntryError, e:
                    return make_response('Bad request: e-mail exists', 400)
                except InvalidData, e:
                    return make_response('Bad Request: %s' % e, 400)

                else:
                    user.set_pass(salt, password)
                    return return_json(user.json())
        else:
            msg = 'Bad request: Content-Type must be application/json'
            return make_response(msg, 400)

    def put(self, user_id):
        if user_id is not None:
            if request.json:
                try:
                    user = User.get(user_id)
                    if g.user != user or not g.user.admin:
                        return make_response('Not authorized %s' % user.email,
                                             401)
                except SQLObjectNotFound:
                    return  make_response('Not found', 404)
                else:
                    try:
                        data = request.json
                        email = data['email']
                        first_name = data['first_name']
                        last_name = data['last_name']
                        alias = data['alias']
                    except KeyError, e:
                        msg = 'Bad Request: %s is required' % e
                        return make_response(msg, 400)
                    else:
                        user.set(email=email, first_name=first_name,
                                 last_name=last_name, alias=alias)
                        return return_json(user.json())

            else:
                msg = 'Bad request: Content-Type must be application/json'
                return make_response(msg, 400)
        else:
            msg = 'You must specify the ID of a user to change'
            return make_response(msg, 400)

    def delete(self, user_id):
        if user_id is not None:
            if g.user.admin:
                user = User.get(user_id)
                user.delete(user_id)
                return return_json(user.json())
            else:
                return make_response('Not authorized', 401)
        else:
            msg = 'You must specify the ID of a user to delete'
            return make_response(msg, 400)

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
                    user_dict = user.dict()
                    user_dict['token'] = user.get_token()
                    return return_json(user_dict)
                else:
                    raise SQLObjectNotFound
            except SQLObjectNotFound, IndexError:
                return make_response("Not authorized", 401)
        else:
            return make_response('Bad request, JSON expected', 400)

class PasswordAPI(MethodView):
    decorators = [require_auth]


    def get(self, user_id):
        return self.send_405()

    def post(self):
        return self.send_405()

    def put(self, user_id):
        if user_id is not None:
            try:
                user = User.get(user_id)
            except SQLObjectNotFound:
                return make_response('Not found', 404)

            if user != g.user or not g.user.admin:
                return make_response('Not authorized', 401)
            else:
                if request.json:
                    try:
                        try:
                            old_pass = request.json['old_password']
                            old_pass = generate_password(old_pass)
                            tok = None
                        except IndexError:
                            old_pass = None
                            tok = request.json['reset_token']
                        new_pass = request.json['new_password']
                        confirm_pass = request.json['confirm_pass']
                    except IndexError, e:
                        return make_response("Bad request: %s is required" % e,
                                             400)
                    else:
                        reset_allowed = False
                        if old_pass and user.password == old_pass:
                            reset_allowed = True
                        else:
                            try:
                                t = ResetToken.select(ResetToken.q.token==tok)
                                t = t[0]
                            except (SQLObjectNotFound, IndexError):
                                return make_response('Not authorized', 401)
                            if t.user == user and t.expires >= datetime.now():
                                reset_allowed = True
                        if reset_allowed and new_pass == confirm_pass:
                            user.set_pass(new_pass)
                            return return_json(user.json())
                        else:
                            return make_response('Not authorized', 401)

    def delete(self, user_id):
        return self.send_405()

class ResetPasswordAPI(MethodView):

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
            try:
                email = request.json['email']
            except IndexError, e:
                return make_response("Bad request: %s is required" % e, 400)
            try:
                user = User.select(User.q.email==email)[0]
            except:
                return make_response(json.dumps({"success": True}), 200)
            token = ResetToken(user=user)
            msg = Message("Password Reset",
                          sender=(SITE_NAME, "no-reply@%s" % SITE_URL),
                          recipients=[email])
            message = """
            Hello!
            You (hopefully) have requested a password reset for your account at
            {site_name}. In order to complete this reset, please visit:

            {site_url}/reset/?{enc_token}
            """

            msg.body = message.format(site_name=SITE_NAME, site_url=SITE_URL,
                                      enc_token=quote(token.token))
            g.mail.send(msg)

            return make_response(json.dumps({"success": True}), 200)

