# Create a blueprint - a way to organize a group of related views and other code
# Rather than register views and other code directly with an application, they are registered with a blueprint.
# Then the blueprint is registered with the application when it is available in the factory function

# Blueprint #1 authentication functions
# 

import functools
from flask import (
    Blueprint, 
    flash, 
    g, 
    redirect, 
    render_template, 
    request, 
    # SECURITY session is a dict that stores data across requests. Flask securely signs the data, incl cookies sent to the browser so that it can’t be tampered with. At the beginning of each request, if a user is logged in their information should be loaded and made available to other views - see load_logged_in_user() fn
    session, 
    url_for
)
from werkzeug.security import check_password_hash,generate_password_hash
from hello_app.db import get_db

# Create Blueprint named 'auth'. Like the application obj the blueprint needs to know where it's defiend so __name__ is passed as the second argument. The url_prefix will be prepended to all the URLs associated with the blueprint.

bp = Blueprint('auth',__name__,url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST')) # when request TO /auth/register, it will call the register view and use the return value as the response 
def register():
    if request.method == 'POST': # user submitted the form so start validating the input
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # SECURITY FEATURE: The database library will take care of escaping the values to prevent SQL injection attack
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    # SECURITY FEATURE: Passwords should never be stored in database directly
                    (username, generate_password_hash(password)), 
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login")) # After storing the user, they are redirected to the login page. url_for() generates the URL for the login view based on its name. This is preferable to writing the URL directly as it allows you to change the URL later without changing all code that links to it. redirect() generates a redirect response to the generated URL.

        # If validation fails...
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST')) 
def login():
    if request.method == 'POST': 
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * from user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'],password):
            error = 'Incorrect password.'

        if error is None:
            session.clear() 
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
    return render_template('auth/login.html')
    #return render_template('blog/index.html') # No one will be able to log in...

@bp.before_app_request
def load_logged_in_user():
    """
    g.user lasts for the length of the request
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear() # remove user id from the session
    return redirect(url_for('auth.login'))


# Require authentication in other views
# A decorator can be used to check this for each view it’s applied to.
# Will be used in contact form/blog views
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view