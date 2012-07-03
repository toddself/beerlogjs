from flask import Flask, make_response, request

from sqlobject import OperationalError

from beerlog.utils.flaskutils import register_api
from beerlog.utils.importers import process_bjcp_style, process_bt_database
from beerlog.models.admin import User, Role
from beerlog.models.image import Image
from beerlog.models.brewery import Hop, Grain, Extract, HoppedExtract,\
                                   Yeast, Water, Misc, Mineral, Fining,\
                                   Flavor, Spice, Herb, BJCPStyle,\
                                   BJCPStyle, MashTun, BoilKettle,\
                                   EquipmentSet, MashProfile, MashStep,\
                                   MashStepOrder, Recipe, RecipeIngredient,\
                                   Inventory

app = Flask(__name__)
app.config.from_object('beerlog.settings')

def init_db(config):
    tables = [User, Image, Hop, Grain, Extract, HoppedExtract, AuthToken,
              Yeast, Water, Misc, Mineral, Fining, Flavor, Spice, Herb,
              BJCPStyle, BJCPCategory,  MashTun, BoilKettle, EquipmentSet,
              MashProfile, MashStep, MashStepOrder, Recipe, RecipeIngredient,
              Inventory, Role]
    for table in tables:
        try:
            table.createTable()
        except OperationalError:
            pass
    

    adef = config['ADMIN_USERNAME']
    admin = Users(email=adef, first_name=adef, last_name=adef, alias=adef)
    admin.set_pass(config['PASSWORD_SALT'], config['ADMIN_PASSWORD'])
    admin.admin = True
    # uncomment when you're sorted out your little permissions thingy
    # for role in config['SYSTEM_ROLES']:
    #     r = Role(name=role)
    # admin.addRole(config['SYSTEM_ROLES'].index(config['ADMIN']))

    process_bjcp_styles()
    process_bt_database()



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