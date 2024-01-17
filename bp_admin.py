from flask import Blueprint, render_template
from sqlalchemy import select

from bp_auth import AuthActions, admin_required, auth
from configs import CONSTS
from models import Contact, Hurl, User, db

bp_admin = Blueprint("bp_admin", __name__, template_folder="templates")


@bp_admin.route("/admin_users", methods=["GET"])
@admin_required
def admin_users():
    items = db.session.scalars(select(User).order_by(User.id))
    attributes = ["id", "username", "created_datetime"]
    header = "Showing all site users."
    return render_template(
        "admin_item.html",
        CONSTS=CONSTS,
        items=items,
        attributes=attributes,
        header=header,
        logged_in=auth(AuthActions.is_logged_in),
        is_admin=auth(AuthActions.is_admin),
    )


@bp_admin.route("/admin_contacts", methods=["GET"])
@admin_required
def admin_contacts():
    items = db.session.scalars(select(Contact).order_by(Contact.id)).all()
    attributes = ["id", "name", "email", "message"]
    header = f"Showing all site messages."
    return render_template(
        "admin_item.html",
        CONSTS=CONSTS,
        items=items,
        attributes=attributes,
        header=header,
        logged_in=auth(AuthActions.is_logged_in),
        is_admin=auth(AuthActions.is_admin),
    )


@bp_admin.route("/admin_hurls", methods=["GET"])
@admin_required
def admin_hurls():
    items = db.session.scalars(select(Hurl).order_by(Hurl.id)).all()

    for i, h in enumerate(items):
        items[i].__setattr__("read_count", len(h.visits))

    attributes = ["id", "user_id", "read_count", "name", "created_datetime"]
    header = "Showing all site hurls."
    return render_template(
        "admin_item.html",
        CONSTS=CONSTS,
        items=items,
        attributes=attributes,
        header=header,
        logged_in=auth(AuthActions.is_logged_in),
        is_admin=auth(AuthActions.is_admin),
    )
