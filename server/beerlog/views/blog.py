# -*- coding: utf-8 -*-
"""
    beerlog.views.blog
    ~~~~~~~~~~~~

    Implements all views for the Entry and Tag APIs

    :copyright: (c) 2012 by Todd Kennedy
    :license: BSD, see LICENSE for more details.
"""

import json
import time
from datetime import datetime, timedelta
from subprocess import Popen, STDOUT, PIPE

from flask.views import MethodView
from formencode.api import Invalid as InvalidData
from formencode import validators
from sqlobject import SQLObjectNotFound
from sqlobject.dberrors import DuplicateEntryError
from flask import request, make_response, g
from bs4 import BeautifulSoup
from sqlobject import AND, OR

import beerlog
from beerlog.utils.wrappers import require_auth
from beerlog.views.base import APIBase
from beerlog.models.blog import Entry, Tag
from beerlog.models.comment import Comment

class UserTagAPI(MethodView, APIBase):
    """This class represents all the methods an authenticated user can perform
    with tags.  There is no anonymous version of this class.

        endpoint: /rest/user/tag/
        available methods: GET, POST, PUT, DELETE
    """

    decorators = [require_auth]
    allowed = ['get', 'post', 'put', 'delete']

    pass


class UserEntryAPI(MethodView, APIBase):
    """ This class represents all the methods an authenticated user can perform
    with blog entries.

    endpoint: /rest/user/entry/
    methods: GET, POST, PUT, DELETE

    """

    decorators = [require_auth]
    allowed = ['get', 'post', 'put', 'delete']

    def entry_from_json(self, json_data):
        try:
            title = self.clean_html(data['title'])
            converter = beerlog.app.config['PANDOC_PATH']
            cmd = [converter, '--strict', '-r', 'html', '-t', 'markdown']
            body_converter = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            body = body_converter.communicate(input=data['body'])
        except IndexError:
            return False

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
        return {"title": title, "body": body, "author": author,
                "post_on": post_on, "draft": draft}

    def deserialize_tags(self, tag_list):
        tags = []
        for t in tag_list:
            t = self.clean_html(t)
            beerlog.app.logger.info("Adding tag: %s" % t)
            try:
                tag = Tag.select(Tag.q.name==t)[0]
            except (SQLObjectNotFound, IndexError):
                tag = Tag(name=t)
            finally:
                tags.append(tag)

        return tags

    def get(self, entry_id=None, date=None, slug=None):
        beerlog.app.logger.info("GET /rest/user/entry/: %s %s %s" %
                                (entry_id, date, slug))
        if entry_id:
            try:
                beerlog.app.logger.info('Returning info for %s' % entry_id)
                entry = Entry.get(entry_id)
                return self.send_200(entry.dict())
            except SQLObjectNotFound:
                return self.send_404()
        elif date and slug:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                next_day = date_obj+timedelta(days=1)
            except ValueError:
                return self.send_400('Date not in YYYY-MM-DD format')
            try:
                entry = Entry.select(AND(OR(Entry.q.post_on<next_day,
                                            Entry.q.post_on>date_obj),
                                         Entry.q.slug==slug))[0]
            except (SQLObjectNotFound, IndexError):
                return self.send_404()
            else:
                beerlog.app.logger.info('Entry %s' % entry)
                return self.send_200(entry.dict())
        else:
            try:
                return self.send_200([e.dict() for e in Entry.select()])
            except SQLObjectNotFound:
                return self.send_404()

    def put(self, entry_id):
        if entry_id is not None:
            try:
                entry = Entry.get(entry_id)
            except SQLObjectNotFound:
                return self.send_404()

            if g.user != entry.user or not g.user.admin:
                return self.send_401()
            else:
                if request.json:
                    data = self.entry_from_json(request.json)
                    try:
                        if data:
                            entry.title = data.title
                            entry.body = data.body
                            entry.draft = data.draft
                            entry.post_on = data.post_on
                            for t in entry.tags:
                                t.removeTag(t)
                            for t in self.deserialize_tags(request.json['tags']):
                                t.addTag(t)
                        else:
                            raise InvalidData
                    except InvalidData:
                        return self.send_400("Missing required fields")
                    else:
                        return self.send_200(entry.dict())
                else:
                    return self.send_400('JSON required')
        else:
            return self.send_404()

    def delete(self, entry_id):
        if entry_id is not None:
            try:
                entry = Entry.get(entry_id)
            except SQLObjectNotFound:
                return self.send_404()
            if g.user != entry.user or g.user.admin:
                return self.send_401()
            else:
                entry.delete(entry_id)
                return self.send_200(entry.dict())
        else:
            return self.send_404()

    def post(self):
        beerlog.app.logger.info('request data: %s' % request.data)
        if request.json:
            try:
                data = self.get_entry_from_json(request.json)
                if data:
                    entry = Entry(data)
                else:
                    return self.send_400("Missing required fields")

            except InvalidData, e:
                beerlog.app.logger.critical('Validation failed %s')
                return self.send_400(e)
            else:
                beerlog.app.logger.info("Entry created: %s" % entry)
                for t in self.deserialize_tags(request.json['tags']):
                    entry.addTag(t)

                beerlog.app.logger.info("JSON: %s" % entry.dict())
                return self.send_201(entry.dict())
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
                return self.send_200(entry.dict())
            except SQLObjectNotFound:
                return self.send_404()
        else:
            try:
                return self.send_200([entry.dict() for e in Entry.select()])
            except SQLObjectNotFound:
                return self.send_404()