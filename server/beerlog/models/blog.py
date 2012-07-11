import re
from datetime import datetime

from sqlobject import *
from formencode import validators

from beerlog.models.comments import Comment

class Entry(SQLObject, JSONable):
    private = ['draft', 'deleted', 'created_on']
    title = UnicodeCol(length=255, validator=validators.String(min=1,max=255))
    body = UnicodeCol(validator=validators.String(min=1))
    tags = RelatedJoin('Tag')
    slug = UnicodeCol(length=255, default="",
                    validator=validators.String(min=1, max=255))
    post_on = DateTimeCol(default=datetime.now())
    created_on = DateTimeCol(default=datetime.now())
    last_modified = DateTimeCol(default=datetime.now())
    draft = BoolCol(default=False)
    author = ForeignKey('Users')
    deleted = BoolCol(default=False)

    def _set_title(self, value):
        self._SO_set_title(value)
        self._SO_set_slug(get_slug_from_title(value))

    def _get_comment_count(self):
        return len(list(Comment.select(AND(Comment.q.comment_type=="Entry", Comment.q.comment_object==self.id))))

    def _get_comments(self):
        return list(Comment.select(AND(Comment.q.comment_type=="Entry", Comment.q.comment_object==self.id)))

class Tag(SQLObject, JSONable):
    name = UnicodeCol(length=255, validator=validators.String(min=1, max=255))
    entries = RelatedJoin('Entry')

def get_slug_from_title(title):
    return re.sub('[^A-Za-z0-9-]', '', re.sub('\s','-', title)).lower()