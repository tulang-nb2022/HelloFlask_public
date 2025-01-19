# Assume using factory functions
import sqlite3

import click
from flask import current_app, g #current_app can be used when using an application factory


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db() # Returns the database conn

    with current_app.open_resource('schema.sql') as f: #open_resource relative to flaskr package
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables.
    """
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """
    Register close_db and init_db_command with the app instance (otherwise wont be used by app).
    When init-db has been registered with the app, it can be called using the flask command, i.e. flask --app flaskr init-db
    However, since you’re using a factory function, that instance isn’t available when writing the functions. Instead, write a function that takes an application and does the registration.


    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command) # Adds a new command that can be called with the flask command



