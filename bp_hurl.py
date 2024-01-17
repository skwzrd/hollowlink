from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy import delete, select, update

from bp_auth import AuthActions, auth, login_required
from configs import CONSTS
from db import generate_unique_token
from forms import HurlForm, get_fields
from limiter import limiter
from models import Hurl, db

bp_hurl = Blueprint("bp_hurl", __name__, template_folder="templates")


@bp_hurl.route("/hurl_create", methods=["GET", "POST"])
@login_required
@limiter.limit("20/day", methods=["POST"], error_message="Currently, users can only create 20 hurls per day.")
def hurl_create():
    form = HurlForm()

    if form.validate_on_submit():
        d = get_fields(Hurl, HurlForm, form)

        token = generate_unique_token()
        url = url_for("bp_visit.visit", token=token, pixel_name=d["pixel_name"])

        user_id = auth(AuthActions.get_user_id)
        hurl = Hurl(user_id=user_id, url=url, token=token, **d)

        db.session.add(hurl)
        db.session.flush()
        hurl_id = hurl.id
        db.session.commit()

        form.data.clear()

        flash("Hurl created.", "success")

        return redirect(url_for("bp_hurl.hurl_read", hurl_id=hurl_id))

    return render_template(
        "hurl_create.html", CONSTS=CONSTS, form=form, logged_in=auth(AuthActions.is_logged_in), is_admin=auth(AuthActions.is_admin)
    )


@bp_hurl.route("/hurl_edit/<int:hurl_id>", methods=["GET", "POST"])
@login_required
def hurl_edit(hurl_id):
    form = HurlForm()

    hurl = None
    user_id = auth(AuthActions.get_user_id)
    if user_id:
        hurl = db.session.scalar(select(Hurl).where(Hurl.id == hurl_id).where(Hurl.user_id == user_id))

    if not hurl:
        return redirect(url_for("bp_hurl.hurl_list"))

    form = HurlForm(obj=hurl)
    if form.validate_on_submit():
        d = get_fields(Hurl, HurlForm, form)

        d["url"] = url_for("bp_visit.visit", token=hurl.token, pixel_name=d["pixel_name"])

        db.session.execute(update(Hurl).where(Hurl.id == hurl.id).values(**d))

        flash("Hurl updated.", "success")
        db.session.commit()

        form.data.clear()
        return redirect(url_for("bp_hurl.hurl_list"))

    return render_template(
        "hurl_edit.html", CONSTS=CONSTS, form=form, hurl=hurl, logged_in=auth(AuthActions.is_logged_in), is_admin=auth(AuthActions.is_admin)
    )


@bp_hurl.route("/hurl/<int:hurl_id>")
@login_required
def hurl_read(hurl_id):
    hurl_visits = None
    user_id = auth(AuthActions.get_user_id)
    if user_id:
        hurl_visits = db.session.scalars(select(Hurl).where(Hurl.id == hurl_id).where(Hurl.user_id == user_id)).all()

    if hurl_visits and hurl_visits[0]:
        hurl = hurl_visits[0]
        visits = list(hurl.visits)
        return render_template(
            "hurl.html",
            CONSTS=CONSTS,
            hurl=hurl,
            visits=visits,
            logged_in=auth(AuthActions.is_logged_in),
            is_admin=auth(AuthActions.is_admin),
        )

    return redirect(url_for("bp_hurl.hurl_list"))


@bp_hurl.route("/hurl_delete/<int:hurl_id>", methods=["DELETE"])
@login_required
def hurl_delete(hurl_id):
    hurl = None
    user_id = auth(AuthActions.get_user_id)
    if user_id:
        hurl = db.session.scalar(select(Hurl).where(Hurl.id == hurl_id).where(Hurl.user_id == user_id))

    if hurl:
        db.session.delete(hurl)
        db.session.commit()

        hurl = db.session.scalar(select(Hurl).where(Hurl.id == hurl_id).where(Hurl.user_id == user_id))

        if not hurl:
            flash("Hurl deleted.", "success")
            return redirect(url_for("bp_hurl.hurl_list"))

    flash(f"Couldn't find hurl #{hurl.id} to delete.")
    return redirect(url_for("bp_hurl.hurl_list"))


@bp_hurl.route("/hurls")
@login_required
def hurl_list():
    hurls = None
    user_id = auth(AuthActions.get_user_id)
    if user_id:
        hurls = db.session.scalars(select(Hurl).where(Hurl.user_id == user_id)).all()

    for i, h in enumerate(hurls):
        hurls[i].__setattr__("read_count", len(h.visits))

    header = "Showing all hurls."
    return render_template(
        "hurl_list.html",
        CONSTS=CONSTS,
        hurls=hurls,
        header=header,
        logged_in=auth(AuthActions.is_logged_in),
        is_admin=auth(AuthActions.is_admin),
    )
