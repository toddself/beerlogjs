from flask.views import MethodView

from beerlog.models.admin import User, AuthToken, Application
from beerlog.utils.wrappers import require_admin, require_auth

class UserAPI(MethodView):
    decorators = [require_auth]
    
    
    def get(self, user_id):
        if user_id is None:
            
        else:

            
    def post(self):
        return 'created new user'
    
    def put(self, user_id):
        if user_id is not None:
            return 'updating user %s' % user_id
        
    def delete(self, user_id):
        if user_id is not None:
            return 'deleteing user %s' % user_id


