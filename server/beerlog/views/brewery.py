# -*- coding: utf-8 -*-
"""
    beerlog.views.brewery
    ~~~~~~~~~~~~

    Implements all models for the Beer making stuff

    :copyright: (c) 2012 by Todd Kennedy
    :license: BSD, see LICENSE for more details.
"""

from formencode.api import Invalid as InvalidData
from sqlobject import SQLObjectNotFound
from sqlobject.dberrors import DuplicateEntryError
from flask import request, g
from flask.views import MethodView

from beerlog.models.brewery import *
from beerlog.utils.wrappers import require_auth
from beerlog.views.base import APIBase

class UserHopAPI(MethodView, APIBase):
    decorators = [require_auth]

    allowed = ['get', 'put', 'post', 'delete']

    def get(self, hop_id, hop_name=None):
        if hop_id:
            try:
                h = Hop.get(hop_id)
            except SQLObjectNotFound:
                return self.send_404();
            else:
                return self.send_200(h.dict())
        elif hop_name:
            try:
                h = Hop.select(Hop.q.name==hop_name)[0]
            except (SQLObjectNotFound, IndexError):
                return self.send_404()
            else:
                return self.send_200(h.dict())
        else:
            return self.send_200([h.dict() for h in Hop.select()])

    def put(self, hop_id):
        pass

    def delete(self, hop_id):
        pass

    def post(self):
        pass

class AnonymousHopAPI(MethodView, APIBase):
    allowed= ['get']

    def get(self, hop_id, hop_name=None):
        if hop_id:
            try:
                h = Hop.get(hop_id)
            except SQLObjectNotFound:
                return self.send_404();
            else:
                return self.send_200(h.dict())
        elif hop_name:
            try:
                h = Hop.select(Hop.q.name==hop_name)[0]
            except (SQLObjectNotFound, IndexError):
                return self.send_404()
            else:
                return self.send_200(h.dict())
        else:
            return self.send_200([h.dict() for h in Hop.select()])