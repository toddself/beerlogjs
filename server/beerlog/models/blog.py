import re
from datetime import datetime

from sqlobject import *
from formencode import validators

from beerlog.models.admin import User
from beerlog.models.comment import Comment
from beerlog.models.columns import JSONable

class Entry(SQLObject, JSONable):
    title = UnicodeCol(length=255, validator=validators.String(min=1,max=255),
                       extra_vars={"type": "string",
                                   "views": ["user", "admin"]})
    body = UnicodeCol(validator=validators.String(min=1),
                      extra_vars={"type": "string",
                                  "views": ["user", "admin"]})
    tags = RelatedJoin('Tag')
      # ,
      #                  extra_vars={"type": "sqlobject",
      #                              "views": ["user", "admin"]})
    slug = UnicodeCol(length=255, default="", validator=validators.String(),
                      extra_vars={"type": "string", "views": ["admin"]})
    post_on = DateTimeCol(default=datetime.now(),
                          extra_vars={"type": "datetime",
                                      "views": ["admin", "user"]})
    created_on = DateTimeCol(default=datetime.now(),
                             extra_vars={"type": "datetime",
                                         "views": ["admin"]})
    last_modified = DateTimeCol(default=datetime.now(),
                                extra_vars={"type": "datetime",
                                            "views": ["admin"]})
    draft = BoolCol(default=False,
                    extra_vars={"type": "boolean",
                                "views": ["admin"]})
    author = ForeignKey('User')
    # ,
    #                     extra_vars={"type": "sqlobject",
    #                                 "views": ["user", "admin"]})
    deleted = BoolCol(default=False,
                      extra_vars={"type": "boolean",
                                  "views": ["admin"]})

    def _set_title(self, value):
        self._SO_set_title(value)
        self._SO_set_slug(get_slug_from_title(value))

    def _get_comment_count(self):
        return len(list(Comment.select(AND(Comment.q.comment_type=="Entry",
                                           Comment.q.comment_object==self.id))))

    def _get_comments(self):
        return list(Comment.select(AND(Comment.q.comment_type=="Entry",
                                       Comment.q.comment_object==self.id)))

    def __str__(self):
        return "%s" % self.title

class Tag(SQLObject, JSONable):
    no_recurse = ['entries']
    name = UnicodeCol(length=255, validator=validators.String(min=1, max=255),
                      extra_vars={"type": "string", "views": ["user", "admin"]})
    entries = RelatedJoin('Entry')

    def __str__(self):
        return self.name

def get_slug_from_title(title):
    return re.sub('[^A-Za-z0-9-]', '', re.sub('\s','-', title)).lower()