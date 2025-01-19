import pytest
from hello_app.db import get_db


def test_index(client, auth):
    response = client.get('/')
    # When not logged in, each page shows links to log in or register.
    assert b"Log In" in response.data # 
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    # When logged in, there’s a link to log out.
    assert b'Log Out' in response.data 
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

# Incorrect user prevents post updates etc
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
# A user must be logged in to access the create, update, and delete views. The logged in user must be the author of the post to access update and delete, otherwise a 403 Forbidden status is returned. If a post with the given id doesn’t exist, update and delete should return 404 Not Found.
def test_login_required(client, path):
    response = client.post(path) #CLIENT is used to make requests to the application without running the server
    assert response.headers["Location"] == "/auth/login"

def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data

@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

# Delete
def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None

