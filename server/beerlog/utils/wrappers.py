from functools import wraps

from flask import g, request, make_response

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
            g.token = request.headers['Authorization'].split(' ')[1]
        except IndexError:
            return make_response("Not authorized", 401)
    return auth
    
def require_admin(callback):
    @require_auth
    @wraps(callback)
