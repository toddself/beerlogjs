from flask import MethodView
from formencode.api import Invalid as InvalidData
from sqlobject import SQLObjectNotFound
from sqlobject.dberrors import DuplicateEntryError
from flask import request, make_response, g

from beerlog.utils.wrappers import require_auth
from beerlog.views.base import APIBase
from beerlog.models.blog import Entry, Tag
from beerlog.models.comment import Comment

class UserEntryAPI(MethodView, APIBase):
    decorators = [require_auth]
    pass

class AnonymousEntryAPI(MethodView, APIBase):


    def get(self, entry_id):
        if entry_id is not None:
            pass
        else:
            pass