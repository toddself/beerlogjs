import hashlib
import string
import random
import base64
from datetime import datetime, timedelta

import Crypto.Random
from sqlobject import *

from beerlog.models.image import Image
from beerlog.models.columns import JSONable
from beerlog.settings import PASSWORD_SALT, TOKEN_BYTES

class User(SQLObject, JSONable):
    private = ['password', 'admin' , 'created_on', 'last_modified',
               'last_login', 'active']
    first_name = UnicodeCol(length=128)
    last_name = UnicodeCol(length=128)
    email = UnicodeCol(length=255, unique=True)
    alias = UnicodeCol(length=255)
    password = UnicodeCol(length=255, default="sdlfjskdfjskdfjsadf")
    created_on = DateTimeCol(default=datetime.now())
    last_modified = DateTimeCol(default=datetime.now())
    last_login = DateTimeCol(default=datetime.now())
    avatar = ForeignKey('Image', notNone=False, default=None)
    active = BoolCol(default=True)
    admin = BoolCol(default=False)

    def set_pass(self, salt, password_value):
        password = hashlib.sha256("%s%s" % (salt, password_value)).hexdigest()
        self._SO_set_password(password)

    def get_token(self):
        authtoken = AuthToken(user=self)
        return authtoken.token

def generate_password(cleartext):
    cyphertext = hashlib.sha256("%s%s" % (PASSWORD_SALT, cleartext))
    return cyphertext.hexdigest()

class AuthToken(SQLObject):
    user = ForeignKey('User')
    token = UnicodeCol(default=PASSWORD_SALT)
    expires = DateTimeCol(default=datetime.now()+timedelta(14))

    def _get_token(self):
        token =  base64.b64encode(Crypto.Random.get_random_bytes(TOKEN_BYTES))
        self._SO_set_token(token)
        return token