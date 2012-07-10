import json
import time
from decimal import Decimal
from datetime import datetime

from flask import make_response
from sqlobject import SQLObject
from sqlobject import connectionForURI, sqlhub
from sqlobject.dberrors import OperationalError

from beerlog.utils.importers import process_bjcp_styles, process_bt_database
from beerlog.models.admin import User, AuthToken
from beerlog.models.image import Image
from beerlog.models.brewery import Hop, Grain, Extract, HoppedExtract,\
                                   Yeast, Water, Misc, Mineral, Fining,\
                                   Flavor, Spice, Herb, \
                                   BJCPStyle, MashTun, BoilKettle,\
                                   EquipmentSet, MashProfile, MashStep,\
                                   MashStepOrder, Recipe, RecipeIngredient,\
                                   Inventory, BJCPCategory


def return_json(data):
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
    resp = make_response(data)
    resp.headers["Content-Type"] = "application/json"
    return resp

def sqlobject_to_dict(obj):
    obj_dict = {}
    cls_name = type(obj)
    for attr in vars(cls_name):
        if isinstance(getattr(cls_name, attr), property) and obj.exported(attr):
            attr_value = getattr(obj, attr)
            attr_class = type(attr_value)
            attr_parent = attr_class.__bases__[0]
            if isinstance(attr_value, Decimal):
                obj_dict[attr] = float(attr_value)
            elif isinstance(attr_value, datetime):
                #javascript? why?
                obj_dict[attr] = time.mktime(attr_value.timetuple())*1000
            elif isinstance(attr_value, list):
                dict_list = []
                for list_item in attr_value:
                    dict_list.append(sqlobject_to_dict(list_item))
                obj_dict[attr] = dict_list
            elif isinstance(attr_value, dict):
                dict_dict = {}
                for key, val in attr_value:
                    dict_dict[key] = sqlobject_to_dict(val)
                obj_dict[attr] = dict_dict
            elif attr_parent == SQLObject:
                obj_dict[attr] = sqlobject_to_dict(attr_value)
            else:
                obj_dict[attr] = attr_value

    return obj_dict

def register_api(view, endpoint, url, app, pk='user_id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

def init_db(config):
    tables = [User, Image, Hop, Grain, Extract, HoppedExtract, AuthToken,
              Yeast, Water, Misc, Mineral, Fining, Flavor, Spice, Herb,
              BJCPStyle, BJCPCategory,  MashTun, BoilKettle, EquipmentSet,
              MashProfile, MashStep, MashStepOrder, Recipe, RecipeIngredient,
              Inventory]
    for table in tables:
            table.createTable(ifNotExists=True)
            if table.__name__ == 'User':
              adef = config['ADMIN_USERNAME']
              admin = User(email=adef, first_name=adef,
                           last_name=adef, alias=adef)
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