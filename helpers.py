#if the user session is active it will directly login the user without the need to login again and again

from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            #redirecting to login in the case user session NOT ACTIVE
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
