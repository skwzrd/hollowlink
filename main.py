import os
from datetime import datetime

from flask import Flask, flash, g, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap5
from werkzeug.middleware.proxy_fix import ProxyFix

from bp_admin import bp_admin
from bp_auth import AuthActions, auth, bp_auth
from bp_hurl import bp_hurl
from bp_user import bp_user
from bp_visit import bp_visit
from configs import CONSTS
from forms import ContactForm, get_fields
from init_database import build_db
from limiter import limiter
from models import Contact, Error, Log, db
from utils import make_path


def create_app():
    app = Flask(__name__)

    app.config.from_object(CONSTS)

    app.register_blueprint(bp_admin)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_user)
    app.register_blueprint(bp_hurl)
    app.register_blueprint(bp_visit)

    Bootstrap5(app)

    if CONSTS.REVERSE_PROXY:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)

    limiter.init_app(app)

    return app


app = create_app()


@app.errorhandler(404)
def not_found(e: Exception):
    error = Error(status_code=404, details=str(e))
    db.session.add(error)
    db.session.commit()
    return (
        render_template("error_404.html", CONSTS=CONSTS, logged_in=auth(AuthActions.is_logged_in), is_admin=auth(AuthActions.is_admin)),
        404,
    )


@app.errorhandler(500)
def internal_server_error(e):
    error = Error(status_code=500, details=str(e))
    db.session.add(error)
    db.session.commit()
    return (
        render_template("error_500.html", CONSTS=CONSTS, logged_in=auth(AuthActions.is_logged_in), is_admin=auth(AuthActions.is_admin)),
        500,
    )


@app.before_request
def before():
    g.start_datetime_utc = datetime.utcnow()

    if app.config["TESTING"]:
        database_path = make_path(app.config["DATABASE_FILE"])
        if not os.path.exists(database_path):
            with app.app_context():
                build_db()


@app.after_request
def after(response):
    g.end_datetime_utc = datetime.utcnow()

    log = Log(
        x_forwarded_for=request.headers.get("X-Forwarded-For", None),
        remote_addr=request.headers.get("Remote-Addr", None),
        referrer=request.referrer,
        content_md5=request.content_md5,
        origin=request.origin,
        scheme=request.scheme,
        method=request.method,
        path=request.path,
        query_string=request.query_string.decode(),
        duration=(g.end_datetime_utc - g.start_datetime_utc).total_seconds(),
        start_datetime_utc=g.start_datetime_utc,
        end_datetime_utc=g.end_datetime_utc,
        user_agent=request.user_agent.__str__(),
        accept=request.headers.get("Accept", None),
        accept_language=request.headers.get("Accept-Language", None),
        accept_encoding=request.headers.get("Accept-Encoding", None),
        content_length=request.content_length,
    )
    db.session.add(log)
    db.session.commit()

    return response


@app.route("/user_guide")
def user_guide():
    return render_template("user_guide.html", CONSTS=CONSTS, logged_in=auth(AuthActions.is_logged_in), is_admin=auth(AuthActions.is_admin))


@app.route("/", methods=["GET", "POST"])
@limiter.limit("3/day", methods=["POST"])
def index():
    form = ContactForm()

    if form.validate_on_submit():
        d = get_fields(Contact, ContactForm, form)
        db.session.add(Contact(**d))
        db.session.commit()
        form.data.clear()
        flash("Message received, thank you!", "success")
        return redirect(url_for("index"))

    return render_template(
        "index.html", CONSTS=CONSTS, form=form, logged_in=auth(AuthActions.is_logged_in), is_admin=auth(AuthActions.is_admin)
    )


if __name__ == "__main__" and CONSTS.TESTING:
    app.run(host=CONSTS.site_host, port=CONSTS.site_port, debug=CONSTS.TESTING)
