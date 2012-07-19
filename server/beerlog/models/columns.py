import time
import json
from decimal import Decimal
from datetime import datetime

from sqlobject import DecimalCol, SQLObject
from sqlobject.col import pushKey

import beerlog

class JSONable(object):
    """ Mixin for SQLObject classes. Allows you to export the object
    as a JSON or dict representation, controlling the data returned
    from the call.

    You can either provide a list that enumerates the fields that
    are visible (meaning that all not listed are hidden) or enumerating
    fields that are hidden (meaning that all not listed are visible)

    ex:
        private = ['password', 'last_login']

    would mean all fields that AREN'T password or last_login will be in the
    json representation

        exports = ['email', 'first_name', 'last_name']

    would mean all that all fields that AREN'T email, first_name nor last_name
    will be hidden from the json respresetation

    TODO: set up roles and allow views specific to users with a specified role

    """


    def dict(self, view=None):
        return_dict = {}
        cls = type(self)
        props = [p for p in vars(cls) if isinstance(getattr(cls, p), property)]
        columns = type(self).sqlmeta.columns
        for prop in props:
            if hasattr(self, 'no_recurse'):
                no_recurse = self.no_recurse
            else:
                no_recurse = []
            if prop not in no_recurse:
                attr = getattr(self, prop)
                try:
                    # this means it's not a piece of derrived data nor is it a
                    # related object
                    column = columns[prop]
                except KeyError:
                    # this means it's a related object or a piece of derrived data
                    # if it's derrived data, we'll worry about it then, if it's
                    # a related object, we'll use it's `dict` method. if it's a list
                    # we'll iterate over the items and use their `dict` methods
                    if isinstance(attr, list):
                        value = [o.dict() for o in attr]
                    elif SQLObject in type(attr).__bases__ and hasattr(attr, "dict"):
                        value = attr.dict()
                    else:
                        value = attr
                else:
                    try:
                        c_type = column.type
                    except AttributeError:
                        value = None
                    else:
                        # this is just plain old data to convert.  we only care about
                        # the datatypes that `json.dumps` can't convert itself
                        if c_type == 'datetime':
                            value = time.mktime(attr.timetuple())*1000
                        elif c_type == 'sqlobject' and hasattr(attr, "dict"):
                            value = attr.dict()
                        elif c_type == 'decimal':
                            value = float(attr)
                        else:
                            value = attr
                if value:
                    return_dict[prop] = value
        return return_dict

    def json(self, view=None):
        return json.dumps(self.dict(view))

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