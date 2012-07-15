import json
import time
from datetime import datetime

from flask.views import MethodView
from formencode.api import Invalid as InvalidData
from formencode import validators
from sqlobject import SQLObjectNotFound
from sqlobject.dberrors import DuplicateEntryError
from flask import request, make_response, g
from bs4 import BeautifulSoup
import beerlog

from beerlog.utils.wrappers import require_auth
from beerlog.utils.flaskutils import sqlobject_to_dict as so2d
from beerlog.views.base import APIBase
from beerlog.models.blog import Entry, Tag
from beerlog.models.comment import Comment

class UserEntryAPI(MethodView, APIBase):
    """ This class represents all the methods an authenticated user can perform
    with blog entries.

    endpoint: /rest/user/entry/
    methods: GET, POST, PUT, DELETE

    """

    decorators = [require_auth]
    allowed = ['get', 'post', 'put', 'delete']

    def get(self, entry_id):
        if entry_id is not None:
            try:
                beerlog.app.logger.info('Returning info for %s' % entry_id)
                entry = Entry.get(entry_id)
                return self.send_200(so2d(entry, False))
            except SQLObjectNotFound:
                return self.send_404()
        else:
            try:
                return self.send_200([so2d(e, False) for e in Entry.select()])
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
                return self.send_200(so2d(entry, False))
        else:
            return self.send_404()

    def post(self):
        beerlog.app.logger.info('request data: %s' % request.data)
        if request.json:
            data = request.json
            title = self.clean_html(data['title'])
            body = self.clean_html(data['body'])
            author = g.user

            try:
                post_on = datetime.fromtimestamp(int(data['post_on'])/1000)
            except (KeyError, ValueError):
                beerlog.app.logger.warn('post_on invalid or not specified')
                post_on = datetime.now()

            try:
                draft = data['draft']
            except KeyError:
                beerlog.app.logger.warn('draft not specified, using False')
                draft = False

            try:
                entry = Entry(title=title, body=body, post_on=post_on,
                              draft=draft, author=author)
            except InvalidData, e:
                beerlog.app.logger.critical('Validation failed %s')
                return self.send_400(e)
            else:
                beerlog.app.logger.info("Entry created: %s" % entry)
                for t in data['tags']:
                    t = self.clean_html(t)
                    beerlog.app.logger.info("Adding tag: %s" % t)
                    try:
                        tag = Tag.select(Tag.q.name==t)[0]
                    except (SQLObjectNotFound, IndexError):
                        tag = Tag(name=t)
                    finally:
                        entry.addTag(tag)

                beerlog.app.logger.info("JSON: %s" % so2d(entry, False))
                return self.send_201(so2d(entry, False))
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
                return return_json(so2d(entry))
            except SQLObjectNotFound:
                return self.send_404()
        else:
            try:
                return self.send_200([e.to_dict() for e in Entry.select()])
            except SQLObjectNotFound:
                return self.send_404()