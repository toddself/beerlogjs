from decimal import Decimal
from datetime import datetime

from sqlobject import SQLObject

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
                obj_dict[attr] = attr_value.strftime('%Y-%m-%d')
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