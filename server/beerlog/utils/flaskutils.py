# -*- coding: utf-8 -*-
"""
    beerlog.utils.flaskutils
    ~~~~~~~~~~~~

    Provides the :meth:`register_api` method which allows you to easily
    generate rules for the REST API, as well as the db init methods

    :copyright: (c) 2012 by Todd Kennedy
    :license: BSD, see LICENSE for more details.
"""

from sqlobject import SQLObject
from sqlobject import connectionForURI, sqlhub
from sqlobject.dberrors import DuplicateEntryError

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

def register_api(view, endpoint, url, app, pk='user_id', pk_type='int',
                 alt_keys=None):
    """Registers a MethodView derived class as a REST API by exposing the
       various HTTP verbs to the correct URL schemes.  Allows alternative
       GET access for specific objects outside of the primary key GET scheme.
       These are defined by the `alt_keys` list.

       `alt_keys` is a list that can contain either strings or lists of strings.
       If the data are strings, it will generate a single alternate GET URL
       scheme inferring the type from the data contained in those strings.

       If it's a list of strings, it will generate a new GET URL for each list
       of strings.

       Ex:

           alt_keys=['date', 'slug'] becomes: [url provided]/<date>/<slug>

           alt_keys=['float:value'] becomes: [url provided]/<float:value>

           alt_keys[['date', 'slug'], ['int:user_id', 'date', 'slug']] becomes:
              [url provided]/<date>/<slug>
              [url provided]/<int:user_id>/<date>/<slug>
    """

    def make_url_component(url_key):
        if ':' in url_key:
            (t, k) = url_key.split(':')
            if t in ['int', 'path', 'float']:
                component =  "<%s:%s>" % (t, k)
            else:
              raise ValueError('Unknown type: %s in %s' % (t, url_key))
        else:
            component = "<%s>" % url_key
        return component

    def make_relative_url(path_list):
        path = []
        for component in path_list:
            path.append(make_url_component(component))
        return "/".join(path)

    def add_routing_rule(url, relative_path, view_func, methods, endpoint):
        beerlog.app.logger.info("Adding rule for %s%s on %s exposing %s" %
                                (url, relative_path, endpoint, ",".join(methods)))
        app.add_url_rule("%s%s" % (url, relative_path), view_func=view_func,
                         methods=methods)

    # generate the default set of URL schemes
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

    # if there are alternative schemes provided, parse and add them
    if alt_keys and isinstance(alt_keys, list) and len(alt_keys) > 0:
        if isinstance(alt_keys[0], list):
            for key in alt_keys:
                add_routing_rule(url, make_relative_url(key), view_func,
                                 ['GET',], endpoint)
        else:
            add_routing_rule(url, make_relative_url(alt_keys), view_func,
                             ['GET',], endpoint)

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