import time
import json
from decimal import Decimal
from datetime import datetime

from sqlobject import DecimalCol, SQLObject
from sqlobject.col import pushKey

class JSONable(object):
    """ Mixin for SQLObject classes. Allows you to export the object
    as a JSON or dict representation, controlling the data returned
    from the call.

    You can either provide a list that enumerates the fields that
    are visible (meaning that all not listed are hidden) or enumerating
    fields that are hiddne (meaning that all not listed are visible)

    ex:
        private = ['password', 'last_login']

    would mean all fields that AREN'T password or last_login will be in the
    json representation

        exports = ['email', 'first_name', 'last_name']

    would mean all that all fields that AREN'T email, first_name nor last_name
    will be hidden from the json respresetation

    TODO: set up roles and allow views specific to users with a specified role

    """

    def to_dict(self, filter_fields=True):
        obj_dict = {}
        cls_name = type(self)
        for attr in vars(cls_name):
            prop = getattr(cls_name, attr)
            if isinstance(prop, property):
                if (filter_fields and self._export(attr)) or not filter_fields:
                    attr_value = getattr(self, attr)
                    attr_class = type(attr_value)
                    attr_parent = attr_class.__bases__[0]
                    if isinstance(attr_value, Decimal):
                        obj_dict[attr] = float(attr_value)
                    elif isinstance(attr_value, datetime):
                        #javascript? why?
                        time_tuple = attr_value.timetuple()
                        obj_dict[attr] = time.mktime(time_tuple)*1000
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

    def to_json(self, filter_fields=True):
        return json.dumps(self.to_dict(filter_fields))

    def _export(self, field):
        exported = True
        try:
            if field in self.exports:
                exported = True
            else:
                exported = False
        except AttributeError:
            exported = True

        try:
            if field in self.private:
               exported = False
        except AttributeError:
            exported = True

        return exported

class SGCol(DecimalCol):
    """ Stores Specific Gravity in a decimal column
    Size is fixed at 4, and the precision is set to 3

    ex: 1.045

    """

    def __init__(self, **kw):
        pushKey(kw, 'size', 4)
        pushKey(kw, 'precision', 3)
        super(DecimalCol, self).__init__(**kw)

class PercentCol(DecimalCol):
    """Stores percentages in a decimal column
    Size is fixed at 5, and the precision is set to 2.

    *nb* size is fixed at 5 to allow for 100.00%

    """

    def __init__(self, **kw):
        pushKey(kw, 'size', 5)
        pushKey(kw, 'precision', 2)
        super(DecimalCol, self).__init__(**kw)

class SRMCol(DecimalCol):
    """ Stores the Standard Reference Method color value in a decimal column
    Size is fixed at 5, precision is set to 1

    ex: 2.0, 300.5

    """

    def __init__(self, **kw):
        pushKey(kw, 'size', 5)
        pushKey(kw, 'precision', 1)
        super(DecimalCol, self).__init__(**kw)

class IBUCol(DecimalCol):
    """ Stores the International Bitterness Units value in a decimal column
    Size is fixed at 4, precision is set to 1

    ex: 2.0, 300.5

    """

    def __init__(self, **kw):
        pushKey(kw, 'size', 4)
        pushKey(kw, 'precision', 1)
        super(DecimalCol, self).__init__(**kw)

class BatchIsNotMaster(Exception):
    def __init__(self,value):
        self.value = value
    def __unicode__(self,value):
        return repr(self.value)

class AmountSetError(Exception):
    def __init__(self, value):
        self.value = value
    def __unicode__(self, value):
        return repr(self.value)