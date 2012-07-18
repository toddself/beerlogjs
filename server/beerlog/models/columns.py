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

    def dict(self, view):
        return_dict = {}
        cls = type(self)
        props = [p for p in vars(cls) if isinstance(getattr(cls, p), property)]
        columns = type(e).sqlmeta.columns
        for prop in props:
            try:
                # this means it's not a piece of derrived data nor is it a
                # related object
                column = columns[prop]
            except KeyError:
                # this means it's a related object or a piece of derrived data
                # if it's derrived data, we'll worry about it then, if it's
                # a related object, we'll use it's `dict` method. if it's a list
                # we'll iterate over the items and use their `dict` methods
            else:
                # this is just plain old data to convert.  we only care about
                # the datatypes that `json.dumps` can't convert itself
                if column.type == 'datetime':
                    pass
                elif column.type == 'sqlobject':
                    pass
                elif column.type == 'decimal':
                    pass
                elif column.type == ''
                    pass


    def to_dict(self, filter_fields=True):
        beerlog.app.logger.info('in to dict')
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
                        beerlog.app.logger.info('Decimal value %s' % attr_value)
                        obj_dict[attr] = float(attr_value)
                        beerlog.app.logger.info(obj_dict)
                    elif isinstance(attr_value, datetime):
                        #javascript? why?
                        beerlog.app.logger.info("Datetime value")
                        time_tuple = attr_value.timetuple()
                        obj_dict[attr] = time.mktime(time_tuple)*1000
                        beerlog.app.logger.info(obj_dict)
                    elif isinstance(attr_value, list):
                        beerlog.app.logger.info("list value %s" % attr_value)
                        dict_list = []
                        for list_item in attr_value:
                            dict_list.append(self.to_dict(filter_fields))
                        obj_dict[attr] = dict_list
                        beerlog.app.logger.info(obj_dict)
                    elif isinstance(attr_value, dict):
                        beerlog.app.logger.info("dict value %s" % attr_value)
                        dict_dict = {}
                        for key, val in attr_value:
                            dict_dict[key] = val.to_dict(filter_fields)
                        obj_dict[attr] = dict_dict
                        beerlog.app.logger.info(obj_dict)
                    # elif attr_parent == SQLObject:
                    #     beerlog.app.logger.info("sqlobject %s" % attr_value)
                    #     obj_dict[attr] = attr_value.to_dict(filter_fields)
                    #     beerlog.app.logger.info(obj_dict)
                    else:
                        obj_dict[attr] = attr_value
                        beerlog.app.logger.info(obj_dict)

        return obj_dict

    def to_json(self, filter_fields=True):
        beerlog.app.logger.info('in to json')
        return json.dumps(self.to_dict(filter_fields))


    # def to_json(self, role):
    #     try:
    #         fields = getattr(self.exports, role)
    #     except AttributeError:
    #         try:
    #             fields = getattr(self.exports, "default")
    #         except AttributeError:
    #             return json.dumps('')

    #     for field in fields:
    #         data = getattr(self, field)





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