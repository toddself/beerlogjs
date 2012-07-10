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
                    raise IndexError
            except SQLObjectNotFound:
                raise IndexError
        except (IndexError, KeyError):
            return make_response("Not authorized", 401)
    return auth