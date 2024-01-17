from enum import Enum
from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for
from sqlalchemy import select
from werkzeug.security import check_password_hash

from configs import CONSTS
from db import get_user_by_username
from forms import LoginForm
from limiter import limiter
from models import User, UserRole, db

bp_auth = Blueprint("bp_auth", __name__, template_folder="templates")


class AuthActions(Enum):
    is_logged_in = 1
    log_in = 2
    log_out = 3
    get_user_id = 4
    is_admin = 5


def auth(action: AuthActions, user_id=None):
    with current_app.app_context():
        if action == AuthActions.is_logged_in:
            return "user_id" in session

        if action == AuthActions.log_in and user_id:
            session["user_id"] = user_id
            return

        if action == AuthActions.log_out:
            session.clear()
            return

        if action == AuthActions.get_user_id:
            return session.get("user_id", None)

        if action == AuthActions.is_admin:
            user_id = auth(AuthActions.get_user_id)
            if user_id:
                user_id = db.session.scalar(select(User.id).where(User.id == user_id).where(User.role == UserRole.admin.value))
                if user_id:
                    return True
            return False

    raise ValueError(action, user_id)


def login_required(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if not auth(AuthActions.is_logged_in):
            flash("Login required", "danger")
            return redirect(url_for("bp_auth.login"))
        return fn(*args, **kwargs)

    return decorated_function


def logout_required(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if auth(AuthActions.is_logged_in):
            flash("Logout required", "danger")
            return redirect(url_for("bp_auth.logout"))
        return fn(*args, **kwargs)

    return decorated_function


def admin_required(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if not auth(AuthActions.is_admin):
            flash("Permission required", "danger")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)

    return decorated_function


@bp_auth.route("/login", methods=["GET", "POST"])
@limiter.limit("5/minute", methods=["POST"])
@limiter.limit("30/day", methods=["POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password_candidate = form.password.data

        user = get_user_by_username(username)
        if user:
            if check_password_hash(user.password, password_candidate):
                auth(AuthActions.log_in, user_id=user.id)

                flash("Login successful.", "success")
                return redirect(url_for("bp_hurl.hurl_list"))

        flash("Incorrect username or password.", "danger")

    return render_template(
        "login.html", form=form, CONSTS=CONSTS, logged_in=auth(AuthActions.is_logged_in), is_admin=auth(AuthActions.is_admin)
    )


@bp_auth.route("/logout", methods=["GET"])
@login_required
def logout():
    auth(AuthActions.log_out)
    flash("Logout successful.", "success")
    return redirect(url_for("bp_auth.login"))
