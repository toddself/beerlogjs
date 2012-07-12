import json
import time
from datetime import datetime

from bson import json_util
from flask.views import MethodView
from formencode.api import Invalid as InvalidData
from formencode import validators
from sqlobject import SQLObjectNotFound
from sqlobject.dberrors import DuplicateEntryError
from flask import request, make_response, g
from bs4 import BeautifulSoup

from beerlog.utils.wrappers import require_auth
from beerlog.views.base import APIBase
from beerlog.models.blog import Entry, Tag
from beerlog.models.comment import Comment

class UserEntryAPI(MethodView, APIBase):
    """ This class represents all the methods an authenticated user can perform
    with blog entries.

    endpoint: /rest/user/entry/
    methods: GET, POST, PUT, DELETE

    TODO: finish converting over to mongodb
    """

    decorators = [require_auth]
    allowed = ['get', 'post', 'put', 'delete']

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
            str_v = validators.String(min=1, max=255)
            body_v = validators.String(min=1)
            try:
                title = str_v.to_python(self.clean_html(data['title']))
            except InvalidData:
                self.return_400('bad title')
            try:
                body = body_v.to_python(self.clean_html(data['body']))
            except InvalidData:
                self.return_400('bad body')
            try:
                post_on = int(data['post_on'])
            except ValueError:
                post_on = time.mktime(datetime.utcnow().timetuple())
            draft = "false"
            if data['draft']:
                draft = "true"
            try:
                cleaned_tags = [self.clean_html(t) for t in data['tags']]
                tags = json.dumps([str_v.to_python(t) for t in cleaned_tags])
            except InvalidData:
                self.return_400('bad tag')

            entry  = {"title": title,
                      "body": body,
                      "post_on": post_on,
                      "author": g.user.id,
                      "draft": json.dumps(draft),
                      "tags": tags}

            g.db.posts.insert(entry)
            print entry

            return json.dumps(entry, default=json_util.default)
            # return self.send_201(entry)
        else:
            return self.send_400()

class AnonymousEntryAPI(MethodView, APIBase):
    """ This class provides only the get method.
        Without authentication, users should only be able
        to read content.

        endpoint: /rest/entry/
        methods: get
    """

    allowed = ['get',]

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