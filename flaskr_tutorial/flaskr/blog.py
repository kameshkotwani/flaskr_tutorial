from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username FROM post p JOIN user u ON p.author_id = u.id ORDER BY created DESC"
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# create

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        err = None
        if not title:
            err = "title is needed"
        elif not body:
            err = "body is needed"

        if err is not None:
            flash(err)
        # put into the sqlite database
        else:
            db = get_db()
            db.execute("INSERT INTO posts (title,body,author_id) VALUES (?,?,?)", (title, body, g.user['id']))
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')


# to check if the current blog is by the logged in user

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # TODO: try redirecting to login instead of throwing error
    if post is None:
        abort(404, f" Post {id} does not exist!")
    if check_author and post['author_id'] != g.user['id']:
        abort(403, f"Forbidden")

    return post


# update part
@bp.route('/<int:id>/update', methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        err = None
        if not title:
            err = "Title is required"
        if err is not None:
            flash(err)
        else:
            db = get_db()
            db.execute("UPDATE POST SET title  = ?,body=?  WHERE id = ?", (title, body, id))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ? ', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
