from decimal import Decimal

from sqlobject import SQLObject

def sqlobject_to_dict(obj):
    obj_dict = {}
    cls_name = type(obj)
    for attr in vars(cls_name):
        if isinstance(getattr(cls_name, attr), property):
            attr_value = getattr(obj, attr)
            attr_class = type(attr_value)
            attr_parent = attr_class.__bases__[0]
            if isinstance(getattr(obj, attr), Decimal):
                obj_dict[attr] = float(getattr(obj, attr))
            elif isinstance(getattr(obj, attr), list):
                dict_list = []
                for list_item in getattr(obj, attr):
                    dict_list.append(sqlobject_to_dict(list_item))
                obj_dict[attr] = dict_list
            elif isinstance(getattr(obj, attr), dict):
                dict_dict = {}
                for key, val in getattr(obj, attr):
                    dict_dict[key] = sqlobject_to_dict(val)
                obj_dict[attr] = dict_dict
            elif attr_parent == SQLObject:
                obj_dict[attr] = sqlobject_to_dict(getattr(obj, attr))
            else:
                obj_dict[attr] = getattr(obj, attr)

    return obj_dict

def register_api(view, endpoint, url, pk='user_id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])