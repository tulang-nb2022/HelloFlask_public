import os
from flask import Flask, render_template
import datetime 

from .kmeans import *
import json

# TEST private post
from flask import redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__) # Flask instance named app
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # Load the instance config (if it exists) when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize the db
    from . import db
    db.init_app(app)
    # There should now be a flaskr.sqlite file in the instance folder in your project
   
    # Create admin user
    with app.app_context():
        # db.get_db().execute('ALTER TABLE user ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0') #Only at initialization
        admin_user = db.get_db().execute(
                'SELECT * from user WHERE is_admin = 1'
            ).fetchone()
        if admin_user is None:
            if os.getenv("ADMIN_USERNAME") is not None and os.getenv("ADMIN_PASSWORD") is not None:
                hashed_password = generate_password_hash(os.getenv("ADMIN_PASSWORD"))
                username = os.getenv("ADMIN_USERNAME")
                db.get_db().execute(
                    "INSERT INTO user (username, password, is_admin) VALUES (?, ?, ?)",
                    (username,hashed_password,1), )
                db.get_db().commit()
                print(f"Admin user '{username}' created successfully.")
            else:
                print(f"Admin user exists")
        else:
            print(f"Admin user not created")
 
        # Table updates
        # Add column is_private to post table
        # db.get_db().execute('ALTER TABLE post ADD COLUMN is_private BOOLEAN NOT NULL DEFAULT 0')
        
    from . import auth
    app.register_blueprint(auth.bp) # The authentication blueprint will have views to register new users and to log in and log out.

    # Import and register the blueprint from the factory using app.register_blueprint()
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/',endpoint='index')

    @app.route('/resume')
    def resume():
        # Render the resume page
        # NOTE: needs to stay here
        return render_template('resume.html')

    # machine learning
    @app.route("/project1ml")
    def project1ml(data_path='./data/'): # The function name must match as the url endpoint
        result_dict = kmeans.cluster_customers(data_path)

        parsed = json.loads(json.dumps({
            "data_path":data_path,
            "silhouette":result_dict["silhouette"],
            "completeness":result_dict["silhouette"]
        }))
        some_string = json.dumps(parsed, indent=4)    
        return render_template('project1ml.html',some_string=some_string)


    return app

app = create_app()



