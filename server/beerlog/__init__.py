# -*- coding: utf-8 -*-
"""
    beerlog
    ~~~~~~~~~~~~

    Set up the `app` object

    :copyright: (c) 2012 by Todd Kennedy
    :license: BSD, see LICENSE for more details.
"""

import logging
from logging import Formatter
from os.path import join as fjoin

from flask import Flask, make_response, request, g
from werkzeug.utils import secure_filename
from flaskext.mail import Mail

from beerlog.utils.flaskutils import register_api, init_db, connect_db
from beerlog.views.admin import UserAPI, LoginAPI, PasswordAPI, ResetPasswordAPI
from beerlog.views.blog import AnonymousEntryAPI, UserEntryAPI, UserTagAPI

# app setup
app = Flask(__name__)
app.config.from_object('beerlog.settings')
file_handler = logging.FileHandler(app.config['LOG_FILE'])
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'))

if app.config['DEBUG']:
    file_handler.setLevel(logging.INFO)
else:
    file_handler.setLevel(logging.WARN)

app.logger.addHandler(file_handler)

# register rest endpoints
## admin functions
register_api(UserAPI, "user_api", "/rest/user/", pk='user_id',
             pk_type='int', app=app)
register_api(LoginAPI, "login_api", "/rest/login/", pk='user_id',
             pk_type='int', app=app)
register_api(PasswordAPI, "password_api", "/rest/password", pk="user_id",
             pk_type="int", app=app)
register_api(ResetPasswordAPI, "reset_pass_api", "/rest/password_reset/",
             pk="user_id", pk_type="int", app=app)

## blog functions
register_api(AnonymousEntryAPI, "anon_entry_api", "/rest/entry/", pk="entry_id",
             pk_type="int", app=app, alt_keys=[['date', 'slug'], ['tag_name']])
register_api(UserEntryAPI, "user_entry_api", "/rest/user/entry/", pk="entry_id",
             pk_type="int", app=app, alt_keys=[['date', 'slug'], ['tag_name']])
register_api(UserTagAPI, "user_tag_api", "/rest/user/tag/", pk="tag_id",
             pk_type="int", app=app, alt_keys=['tag_name'])



# make sure we've got a database...
@app.before_request
def before_request():
    connect_db(app.config)
    g.mail = Mail(app)

@app.teardown_request
def teardown_request(exception):
    pass

##########################################
# debugging!
@app.route('/')
def index():
    if app.debug:
        with open(fjoin('client', 'src', 'index.html')) as f:
            index = f.read()
        return index

@app.route('/js/<string:filename>')
@app.route('/js/vendor/<string:filename>')
def vendor(filename):
    if app.debug:
        if "vendor" in request.path:
            filename = fjoin('vendor', secure_filename(filename))
        else:
            filename = secure_filename(filename)

        with open(fjoin('client', 'src', 'js', filename)) as f:
            script = f.read()
        response = make_response(script)
        response.headers['Content-Type'] = 'application/javascript'
        return response
