import json

from flask.views import MethodView

from beerlog.models.admin import User, AuthToken
from beerlog.utils.wrappers import require_admin, require_auth
from beerlog.utils.flaskutils import sqlobject_to_dict

class UserAPI(MethodView):

    def get(self, user_id):
        if user_id is None:
            return json.dumps([sqlobject_to_dict(user) for user in User.select()])
        else:
            return json.dumps(sqlobject_to_dict(User.get(id=user_id)))

    def post(self):
        pass

    def put(self, user_id):
        if user_id is not None:
            return 'updating user %s' % user_id

    def delete(self, user_id):
        if user_id is not None:
            return 'deleteing user %s' % user_id