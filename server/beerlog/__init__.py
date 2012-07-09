from flask import Flask, make_response, request

from sqlobject import connectionForURI, sqlhub
from sqlobject.dberrors import OperationalError

from beerlog.utils.flaskutils import register_api
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

from beerlog.views.admin import UserAPI

app = Flask(__name__)
app.config.from_object('beerlog.settings')

register_api(UserAPI, "user_api", "/rest/user/", pk='user_id', pk_type='int', app=app)

def init_db(config):
    tables = [User, Image, Hop, Grain, Extract, HoppedExtract, AuthToken,
              Yeast, Water, Misc, Mineral, Fining, Flavor, Spice, Herb,
              BJCPStyle, BJCPCategory,  MashTun, BoilKettle, EquipmentSet,
              MashProfile, MashStep, MashStepOrder, Recipe, RecipeIngredient,
              Inventory]
    for table in tables:
        try:
            table.createTable()
            if table.__name__ == 'User':
              adef = config['ADMIN_USERNAME']
              admin = User(email=adef, first_name=adef, last_name=adef, alias=adef)
              admin.set_pass(config['PASSWORD_SALT'], config['ADMIN_PASSWORD'])
              admin.admin = True
        except OperationalError:
            pass


    process_bjcp_styles()
    process_bt_database()

def connect_db(config):
    connection = connectionForURI("%s%s%s" % (config['DB_DRIVER'],
                                              config['DB_PROTOCOL'],
                                              config['DB_NAME']))
    sqlhub.processConnection = connection
    init_db(config)

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
