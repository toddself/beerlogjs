from flask import Flask, make_response, request
from flask_debugtoolbar import DebugToolbarExtension
from flask.views import MethodView
from pymongo import Connection

app = Flask(__name__)
app.config.from_object('beerlog.settings')
toolbar = DebugToolbarExtension(app)

class UserAPI(MethodView):
    
    def get(self, user_id):
        if user_id is None:
            return 'all users'
        else:
            return 'user: %s' % user_id
            
    def post(self):
        return 'created new user'
    
    def put(self, user_id):
        if user_id is not None:
            return 'updating user %s' % user_id
        
    def delete(self, user_id):
        if user_id is not None:
            return 'deleteing user %s' % user_id


def register_api(view, endpoint, url, pk='user_id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

register_api(UserAPI, 'user_api', '/rest/user/')

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