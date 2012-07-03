from flask import Flask, make_response, request
from flask_debugtoolbar import DebugToolbarExtension

from beerlog.utils.flaskutils import register_api

app = Flask(__name__)
app.config.from_object('beerlog.settings')
toolbar = DebugToolbarExtension(app)

register_api(UserAPI, 'user_api', '/rest/user/')
register_api(AuthAPI, 'auth_api', '/rest/auth/')

@app.before_request
def before_request():
    connect_db(app.config)

@app.teardown_request
def teardown_request(exception):
    pass



# debugging!
@app.route('/')
def index():
    if app.debug:
        with open('../client/index.html') as f:
            index = f.read()
        return index

@app.route('/js/<string:filename>')
@app.route('/js/vendor/<string:filename>')
def vendor(filename):
    if app.debug:
        path = request.path
        with open('../client'+path) as f:
            script = f.read()
        response = make_response(script)
        response.headers['Content-Type'] = 'application/javascript'
        return response