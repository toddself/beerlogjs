import json
import time
from decimal import Decimal
from datetime import datetime

from flask import make_response
from sqlobject import SQLObject
from sqlobject import connectionForURI, sqlhub
from sqlobject.dberrors import OperationalError, DuplicateEntryError

from beerlog.utils.importers import process_bjcp_styles, process_bt_database
from beerlog.models.admin import User, AuthToken, ResetToken
from beerlog.models.image import Image
from beerlog.models.brewery import Hop, Grain, Extract, HoppedExtract,\
                                   Yeast, Water, Misc, Mineral, Fining,\
                                   Flavor, Spice, Herb, \
                                   BJCPStyle, MashTun, BoilKettle,\
                                   EquipmentSet, MashProfile, MashStep,\
                                   MashStepOrder, Recipe, RecipeIngredient,\
                                   Inventory, BJCPCategory
from beerlog.models.blog import Entry, Tag
from beerlog.models.comment import Comment
import beerlog

def register_api(view, endpoint, url, app, pk='user_id', pk_type='int', alt_keys=None):
    def make_route(key_dict):
      key_type = key_dict['type']
      key_name = key_dict['name']
      if key_type in ['int', 'path', 'float']:
        fragment =  "<%s:%s>" % (key_type, key_name)
      else:
        fragment = "<%s>" % key_name
      return fragment

    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])
    if alt_keys:
        key_list = []
        for key in alt_keys:
            key_list.append(make_route(key))
        key_string = '/'.join(key_list)

        beerlog.app.logger.info("Adding additional GET rule for %s%s on %s" %
                                (url, key_string, endpoint))
        app.add_url_rule('%s%s' % (url, key_string), view_func=view_func,
                         methods=['GET'])


def init_db(config):
    tables = [User, Image, Hop, Grain, Extract, HoppedExtract, AuthToken,
              Yeast, Water, Misc, Mineral, Fining, Flavor, Spice, Herb,
              BJCPStyle, BJCPCategory,  MashTun, BoilKettle, EquipmentSet,
              MashProfile, MashStep, MashStepOrder, Recipe, RecipeIngredient,
              Inventory, ResetToken, Entry, Comment, Tag]
    for table in tables:
            table.createTable(ifNotExists=True)
            if table.__name__ == 'User':
              adef = config['ADMIN_USERNAME']
              try:
                  admin = User(email=adef, first_name=adef,
                               last_name=adef, alias=adef)
              except DuplicateEntryError:
                  admin = User.select(User.q.email==adef)[0]
              admin.set_pass(config['PASSWORD_SALT'], config['ADMIN_PASSWORD'])
              admin.admin = True


    process_bjcp_styles()
    process_bt_database()

def connect_db(config):
    connection = connectionForURI("%s%s%s" % (config['DB_DRIVER'],
                                              config['DB_PROTOCOL'],
                                              config['DB_NAME']))
    sqlhub.processConnection = connection
    init_db(config)