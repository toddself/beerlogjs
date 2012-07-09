from functools import wraps

from flask import g, request, make_response
from sqlobject import SQLObjectNotFound

from beerlog.models.admin import User, AuthToken

def require_admin(callback):
    @require_auth
    @wraps(callback)
    def admin(*args, **kwargs):
        try:
            user = Users.get(session.get('user_id'))
            if user.admin:
                return callback(*args, **kwargs)
            else:
                flash("Admins only")
                return redirect(url_for('list_entries'))
        except SQLObjectNotFound:
            flash("You're not even logged in")
            return redirect(url_for('list_entries'))
    return admin

def require_auth(callback):
    @wraps(callback)
    def auth(*args, **kwargs):
        try:
            token = request.headers['Authorization']
            try:
                user = AuthToken.get(token=token)
            except SQLObjectNotFound:
                return make_response("Not authorized", 401)
            else:
                pass


        except IndexError:
            return make_response("Not authorized", 401)
    return auth

# def require_admin(callback):
#     @require_auth
#     @wraps(callback)