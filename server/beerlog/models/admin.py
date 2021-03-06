import hashlib
import string
import random
import base64
from datetime import datetime, timedelta

import Crypto.Random
from sqlobject import *
from formencode import validators

from beerlog.models.image import Image
from beerlog.models.columns import JSONable
from beerlog.settings import PASSWORD_SALT, TOKEN_BYTES

class User(SQLObject, JSONable):
    private = ['password', 'admin' , 'created_on', 'last_modified',
               'last_login', 'active']
    first_name = UnicodeCol(length=128,
                            validator=validators.String(min=1, max=128),
                            extra_vars={"type": "string",
                                        "views": ["user", "admin"]})
    last_name = UnicodeCol(length=128,
                            validator=validators.String(min=1, max=128),
                            extra_vars={"type": "string",
                                        "views": ["user", "admin"]})
    email = UnicodeCol(length=255, unique=True, validator=validators.Email,
                       extra_vars={"type": "string",
                                   "views": ["user", "admin"]})
    alias = UnicodeCol(length=255, validator=validators.String(min=1, max=255),
                       extra_vars={"type": "string",
                                   "views": ["user", "admin"]})
    password = UnicodeCol(length=255, default="sdlfjskdfjskdfjsadf",
                          validator=validators.String(min=8, max=255),
                          extra_vars={"type": "string", "views": ["admin"]})
    created_on = DateTimeCol(default=datetime.now(),
                             extra_vars={"type": "datetime",
                                         "views": ["admin"]})
    last_modified = DateTimeCol(default=datetime.now(),
                                extra_vars={"type": "datetime",
                                            "views": ["admin"]})
    last_login = DateTimeCol(default=datetime.now(),
                             extra_vars={"type": "datetime",
                                         "views": ["admin", "owner"]})
    avatar = ForeignKey('Image', notNone=False, default=None,
                        extra_vars={"type": "sqlobject",
                                    "views": ["admin", "user"]})
    active = BoolCol(default=True,
                     extra_vars={"type": "boolean", "views": ["admin"]})
    admin = BoolCol(default=False,
                    extra_vars={"type": "boolean", "views": ["admin"]})

    def set_pass(self, salt, password_value):
        password = hashlib.sha256("%s%s" % (salt, password_value)).hexdigest()
        self._SO_set_password(password)

    def get_token(self):
        authtoken = AuthToken(user=self)
        return authtoken.new_token

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

def generate_password(cleartext):
    cyphertext = hashlib.sha256("%s%s" % (PASSWORD_SALT, cleartext))
    return cyphertext.hexdigest()

class AuthToken(SQLObject):
    user = ForeignKey('User')
    token = UnicodeCol(default=PASSWORD_SALT)
    expires_on = DateTimeCol(default=datetime.now()+timedelta(days=14))
    created_on = DateTimeCol(default=datetime.now())

    def _get_new_token(self):
        token =  base64.b64encode(Crypto.Random.get_random_bytes(TOKEN_BYTES))
        self._SO_set_token(token)
        return token

    def __str__(self):
        return "Token: %s, Expires: %s" % (self.token,
               self.expires_on.strftime('%Y-%m-%d %H:%M:%S'))

class ResetToken(SQLObject):
    user = ForeignKey('User')
    token = UnicodeCol(default=PASSWORD_SALT)
    expires = DateTimeCol(default=datetime.now()+timedelta(hours=4))

    def _get_token(self):
        token = base64.b64encode(Crypto.Random.get_random_bytes(TOKEN_BYTES))
        self._SO_set_token(token)
        return token

    def __str__(self):
        return "Token: %s, Expires: %s" % (self.token,
                self.expires_on.strftime('%Y-%m-%d %H:%M:%S'))