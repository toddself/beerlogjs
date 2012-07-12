from flask.views import MethodView
from formencode.api import Invalid as InvalidData
from sqlobject import SQLObjectNotFound
from sqlobject.dberrors import DuplicateEntryError
from flask import request, make_response, g
from bs4 import BeautifulSoup

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
                return self.send_404()
        else:
            try:
                return make_json([e.to_dict(False) for e in Entry.select()])
            except SQLObjectNotFound:
                return self.send_404()

    def put(self, entry_id):
        pass

    def delete(self, entry_id):
        if entry_id is not None:
            try:
                entry = Entry.get(entry_id)
            except SQLObjectNotFound:
                return self.send_404()
            if g.user != entry.user:
                return self.send_401()
            else:
                entry.delete(entry_id)
                return self.send_200(entry.to_json(False))
        else:
            return self.send_404()

    def post(self):
        if request.json:
            data = request.json
            title = data['title']
            body = ''.join(BeautifulSoup(data['body']).findAll(text=True))
            try:
                post_on = datetime.fromtimestamp(int(data['post_on']))
            except ValueError:
                pass
            author = g.user
            draft = False
            if data['draft']:
                draft = True

            tags = data['tags']
        else:
            return self.send_400()

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
                return self.send_404()
        else:
            try:
                return self.send_200([e.to_dict() for e in Entry.select()])
            except SQLObjectNotFound:
                return self.send_404()