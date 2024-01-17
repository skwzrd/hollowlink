from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy import insert, select, update
from werkzeug.security import generate_password_hash

from bp_auth import AuthActions, auth, login_required, logout_required
from configs import CONSTS
from forms import NewUserForm, UserForm, get_fields
from limiter import limiter
from models import User, db

bp_user = Blueprint("bp_user", __name__, template_folder="templates")


@bp_user.route("/user_create", methods=["GET", "POST"])
@logout_required
@limiter.limit("10/day", methods=["POST"])
def user_create():
    form = NewUserForm()

    if form.validate_on_submit():
        form.password.data = generate_password_hash(form.password.data)

        d = get_fields(User, NewUserForm, form)
        username = d["username"].strip()

        existing_username = db.session.scalar(select(User.username).where(User.username == username))
        if existing_username:
            flash("That username is already taken. Please choose another username.", "warning")
            form.username.data = ""  # clear username in form
        else:
            db.session.execute(insert(User).values(**d))
            db.session.commit()

            flash(f'User account "{username}" created.', "success")
            form.data.clear()
            return redirect(url_for("bp_auth.login"))

    return render_template(
        "user_create.html", CONSTS=CONSTS, form=form, logged_in=auth(AuthActions.is_logged_in), is_admin=auth(AuthActions.is_admin)
    )


@bp_user.route("/user", methods=["GET"])
@login_required
def user():
    user_id = auth(AuthActions.get_user_id)
    user = db.session.scalar(select(User).where(User.id == user_id))
    if user.id:
        return redirect(url_for("bp_user.user_edit", user_id=user.id))

    return redirect(url_for("bp_auth.login"))


@bp_user.route("/user_edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_edit(user_id):
    user_id = auth(AuthActions.get_user_id)
    user = db.session.scalar(select(User).where(User.id == user_id))

    if not user:
        flash("Please log in to edit your profile.")
        return redirect(url_for("bp_auth.login"))

    form = UserForm(obj=user)

    if form.validate_on_submit():
        if form.password.data != "":
            form.password.data = generate_password_hash(form.password.data)
            d = get_fields(User, UserForm, form)
        else:
            d = get_fields(User, UserForm, form)
            d.pop("password")  # password not changed

        db.session.execute(update(User).where(User.id == user.id).values(**d))
        db.session.commit()

        flash("User updated.", "success")
        form.data.clear()

    return render_template(
        "user_edit.html", CONSTS=CONSTS, form=form, user=user, logged_in=auth(AuthActions.is_logged_in), is_admin=auth(AuthActions.is_admin)
    )
