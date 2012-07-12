from flask.views import MethodView
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

    def get(self, entry_id):
        if entry_id is not None:
            try:
                entry = Entry.get(entry_id)
                return return_json(entry.to_json(False))
            except SQLObjectNotFound:
                return make_response('Not found', 404)
        else:
            try:
                return make_json([e.to_dict(False) for e in Entry.select()])
            except SQLObjectNotFound:
                return make_response('Not found', 404)

    def put(self, entry_id):
        pass

    def delete(self, entry_id):
        if entry_id is not None:
            try:
                entry = Entry.get(entry_id)
            except SQLObjectNotFound:
                return make_response("Not found", 404)
            if g.user != entry.user:
                return make_response("Not authorized", 401)
            else:
                entry.delete(entry_id)
                return make_json(entry.to_json(False))
        else:
            return make_response("Not found", 404)

    def post(self):
        pass

class AnonymousEntryAPI(MethodView, APIBase):
    """ This class provides only the get method.
        Without authentication, users should only be able
        to read content.
    """

    def get(self, entry_id):
        if entry_id is not None:
            try:
                entry = Entry.get(entry_id)
                return return_json(entry.to_json())
            except SQLObjectNotFound:
                return make_response('Not found', 404)
        else:
            try:
                return make_json([e.to_dict() for e in Entry.select()])
            except SQLObjectNotFound:
                return make_response('Not found', 404)