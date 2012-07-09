import hashlib
import string
import random
from datetime import datetime, timedelta

from sqlobject import *

from beerlog.models.image import Image
from beerlog.settings import PASSWORD_SALT

class User(SQLObject):
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
    # role = RelatedJoin('Role')
    admin = BoolCol(default=False)

    def set_pass(self, salt, password_value):
        password = hashlib.sha256("%s%s" % (salt, password_value)).hexdigest()
        self._SO_set_password(password)

    def _get_memberships(self):
        return self.role.memberships()

    def _get_token(self):
        authtoken = AuthToken(user=self)
        return authtoken.token

def generate_password(cleartext):
    cyphertext = hashlib.sha256("%s%s" % (PASSWORD_SALT, cleartext))
    return cyphertext.hexdigest()


# class Role(SQLObject):
#     name = UnicodeCol(length=128)
#     user = RelatedJoin('Users')
#     memberships= RelatedJoin('Role',
#                              joinColumn='master_role',
#                              otherColumn='sub_role',
#                              addRemoveName='Membership',
#                              intermediateTable='role_to_role_relations',
#                              createRelatedTable=True)

#     def _get_memeberships(self):
#         return self.memberships + [self,]

class AuthToken(SQLObject):
    user = ForeignKey('User')
    token = UnicodeCol()
    expires = DateTimeCol(default=datetime.now()+timedelta(14))

    def _get_token(self):
        chars = string.ascii_uppercase + string.digits
        token =  ''.join(random.choice(chars) for x in range(25))
        _SO_set_token(self, token)
        return token