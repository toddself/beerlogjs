from datetime import datetime

from sqlobject import *
from formencode import validators

class Comment(SQLObject, JSONable):
    private = ['ip_address', 'comment_object', 'comment_type']
    body = UnicodeCol(validator=validators.String(min=1))
    posted_by_name = UnicodeCol(length=128,
                                validator=validators.String(min=1, max=128))
    posted_by_email = UnicodeCol(length=255,
                                 validator=validators.String(min=1, max=255))
    posted_on = DateTimeCol(default=datetime.now())
    ip_address = UnicodeCol(length=15,
                            validator=validators.String(min=15, max=15))
    comment_object = IntCol(default=0, validator=validators.Int())
    comment_type = UnicodeCol(default=None)