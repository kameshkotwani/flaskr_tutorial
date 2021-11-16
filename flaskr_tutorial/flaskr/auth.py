import functools
from flask import (Blueprint, redirect, flash, g, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# creating a register route
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        err = None
        if not username:
            err = "username is required"
        elif not password:
            err = "password is required"

        if err is None:
            try:
                db.execute("INSERT INTO user (username,password) VALUES (? ,?) ",
                           (username, generate_password_hash(password)))
                db.commit()
            except db.IntegrityError:
                err = f"{username} already exists!"
            else:
                return redirect(url_for('auth.login'))
            flash(err)

    return render_template("auth/register.html")


# this is a login route
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        err = None
        # fetch the user from the database
        user = db.execute(
            "SELECT * FROM user WHERE username=?", (username,)
        ).fetchone()

        # checking if the user exists
        if user is None:
            err = "Incorrect username"
        elif not check_password_hash(user['password'], password):
            err = "Incorrect Password"

        if err is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(err)
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
