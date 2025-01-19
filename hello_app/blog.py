from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flask import redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

from hello_app.auth import login_required
from hello_app.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    if g.user is None:
        return render_template('blog/index.html')
    else:
        if db.execute('SELECT * FROM user WHERE id = ? and is_admin = 1', (g.user['id'],)).fetchone() is not None : #user is admin
            posts = db.execute(
                'SELECT p.id, title, body, created, author_id, username'
                ' FROM post p JOIN user u ON p.author_id = u.id'
                ' ORDER BY created DESC'
            ).fetchall()
        else:
            posts = db.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id where p.is_private=0 or p.author_id = ?'
            ' ORDER BY created DESC', (g.user['id'],)
        ).fetchall()
        return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        is_private = request.form['is_private'] # TEST private
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, is_private)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], is_private)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# used by both update/delete views
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and (post['author_id'] != g.user['id'] or g.user['is_admin'] is False):
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))