from datetime import datetime
from functools import wraps

from flask import g, request, make_response
from sqlobject import SQLObjectNotFound

import beerlog
from beerlog.models.admin import User, AuthToken

def require_auth(callback):
    @wraps(callback)
    def auth(*args, **kwargs):
        try:
            token = request.headers['Authorization']
        except KeyError:
            beerlog.app.logger.warn("No authorization header")
            return make_response("Not authorized", 401)
        else:
            beerlog.app.logger.info('Recieved token: %s' % token)
            try:
                auth_token = AuthToken.select(AuthToken.q.token==token)[0]
            except (IndexError, SQLObjectNotFound):
                return make_response("Not authorized: invalid token", 401)
            else:
                user = auth_token.user
                beerlog.app.logger.info(auth_token)
                if auth_token.expires_on >= datetime.now() and user.active:
                    beerlog.app.logger.info('Token valid for %s' % user.email)
                    g.user = user
                    return callback(*args, **kwargs)
                else:
                    return make_response("Not authorized: token expired", 401)
    return auth