from datetime import datetime
from functools import wraps

from flask import g, request, make_response
from sqlobject import SQLObjectNotFound

from beerlog.models.admin import User, AuthToken

def require_auth(callback):
    @wraps(callback)
    def auth(*args, **kwargs):
        try:
            token = request.headers['Authorization']
            try:
                auth_token = AuthToken.select(AuthToken.q.token==token)[0]
                user = auth_token.user
                if auth_token.expires >= datetime.now() and user.active:
                    g.user = user
                    return callback(*args, **kwargs)
                else:
                    return make_response("Not authorized: token expired", 401)
            except (IndexError, SQLObjectNotFound):
                return make_response("Not authorized: invalid token", 401)
        except KeyError:
            return make_response("Not authorized: %s" % request.headers['Authorization'], 401)
    return auth