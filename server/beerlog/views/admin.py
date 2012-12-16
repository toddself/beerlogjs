import hashlib
from datetime import datetime
from urllib import quote

from formencode.api import Invalid as InvalidData
from sqlobject import SQLObjectNotFound
from sqlobject.dberrors import DuplicateEntryError
from flask import request, g
from flask.views import MethodView
from flask_mail import Message

from beerlog.models.admin import User, AuthToken, ResetToken, generate_password
from beerlog.utils.wrappers import require_auth
from beerlog.settings import PASSWORD_SALT as salt
from beerlog.settings import SITE_URL, SITE_NAME
from beerlog.views.base import APIBase

class UserAPI(MethodView, APIBase):
    decorators = [require_auth]

    def get(self, user_id):
        if user_id is None:
            userlist = [user.dict() for user in User.select()]
            return self.send_200(userlist)
        else:
            try:
                user = User.get(user_id)
            except SQLObjectNotFound:
                return self.send_404()
            else:
                return self.send_200(user.json())

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
                return self.send_400(e)
            else:
                try:
                    user = User(email=email, first_name=first_name,
                                last_name=last_name, alias=alias)
                except DuplicateEntryError, e:
                    return self.send_400('e-mail exists')
                except InvalidData, e:
                    return self.send_400(e)

                else:
                    user.set_pass(salt, password)
                    return self.send_201(user.json())
        else:
            return self.send_400()

    def put(self, user_id):
        if user_id is not None:
            if request.json:
                try:
                    user = User.get(user_id)
                    if g.user != user or not g.user.admin:
                        return self.send_401('Not authorized')
                except SQLObjectNotFound:
                    return  self.send_404()
                else:
                    try:
                        data = request.json
                        email = data['email']
                        first_name = data['first_name']
                        last_name = data['last_name']
                        alias = data['alias']
                    except KeyError, e:
                        return self.send_400('%s is required' % e)
                    else:
                        user.set(email=email, first_name=first_name,
                                 last_name=last_name, alias=alias)
                        return self.send_200(user.json())

            else:
                return self.send_400('Content-Type must be application/json')
        else:
            return self.send_400('You must specify the ID of a user to change')

    def delete(self, user_id):
        if user_id is not None:
            if g.user.admin:
                user = User.get(user_id)
                user.delete(user_id)
                return self.send_200(user.json())
            else:
                return self.send_401()
        else:
            return self.send_400('You must specify the ID of a user to delete')

class LoginAPI(MethodView, APIBase):
    allowed = ['POST']

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
                    return self.send_200(user_dict)
                else:
                    raise SQLObjectNotFound
            except SQLObjectNotFound, IndexError:
                return self.send_401()
        else:
            return self.send_400('Bad request, JSON expected')

class PasswordAPI(MethodView, APIBase):
    decorators = [require_auth]
    allowed = ['put']

    def put(self, user_id):
        if user_id is not None:
            try:
                user = User.get(user_id)
            except SQLObjectNotFound:
                return self.send_404()

            if user != g.user or not g.user.admin:
                return self.send_401()
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
                        return self.send_400("%s is required" % e)
                    else:
                        reset_allowed = False
                        if old_pass and user.password == old_pass:
                            reset_allowed = True
                        else:
                            try:
                                t = ResetToken.select(ResetToken.q.token==tok)
                                t = t[0]
                            except (SQLObjectNotFound, IndexError):
                                return self.send_401()
                            if t.user == user and t.expires >= datetime.now():
                                reset_allowed = True
                        if reset_allowed and new_pass == confirm_pass:
                            user.set_pass(new_pass)
                            return self.send_200(user.json())
                        else:
                            return self.send_401()

class ResetPasswordAPI(MethodView, APIBase):
    allowed = ['post']

    def post(self):
        if request.json:
            try:
                email = request.json['email']
            except IndexError, e:
                return self.send_400("%s is required" % e)
            try:
                user = User.select(User.q.email==email)[0]
            except:
                return self.send_200({"success": True})
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

        return self.send_200("OK")

