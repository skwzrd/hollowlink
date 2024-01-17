import json
import os
import re
from datetime import datetime

from flask import Blueprint, abort, g, request, send_from_directory
from sqlalchemy import select

from models import Hurl, Visit, db
from utils import make_path

bp_visit = Blueprint("bp_visit", __name__, template_folder="templates")


def create_visit(token):
    g.end_datetime_utc = datetime.utcnow()

    visit = Visit(
        token=token,
        x_forwarded_for=request.headers.get("X-Forwarded-For", None),
        remote_addr=request.headers.get("Remote-Addr", None),
        referrer=request.referrer,
        content_md5=request.content_md5,
        origin=request.origin,
        view_args=json.dumps(request.view_args),
        scheme=request.scheme,
        method=request.method,
        root_path=request.root_path,
        path=request.path,
        query_string=request.query_string.decode(),
        duration=(g.end_datetime_utc - g.start_datetime_utc).total_seconds(),
        start_datetime_utc=g.start_datetime_utc,
        end_datetime_utc=g.end_datetime_utc,
        user_agent=request.user_agent.__str__(),
        x_forwarded_proto=request.headers.get("X-Forwarded-Proto", None),
        x_forwarded_host=request.headers.get("X-Forwarded-Host", None),
        x_forwarded_prefix=request.headers.get("X-Forwarded-Prefix", None),
        host=request.headers.get("Host", None),
        connection=request.headers.get("Connection", None),
        accept=request.headers.get("Accept", None),
        accept_language=request.headers.get("Accept-Language", None),
        accept_encoding=request.headers.get("Accept-Encoding", None),
        dnt=request.headers.get("Dnt", None),
        upgrade_insecure_requests=request.headers.get("Upgrade-Insecure-Requests", None),
        sec_fetch_dest=request.headers.get("Sec-Fetch-Dest", None),
        sec_fetch_mode=request.headers.get("Sec-Fetch-Mode", None),
        sec_fetch_site=request.headers.get("Sec-Fetch-Site", None),
        sec_fetch_user=request.headers.get("Sec-Fetch-User", None),
        cookies=json.dumps(request.cookies),
        content_length=request.content_length,
    )
    return visit


@bp_visit.route("/static/images/<string:token>/<string:pixel_name>.gif", methods=["GET"])
def visit(token, pixel_name):
    path = make_path("static", "images")

    pattern = "^[a-zA-Z0-9]{1,64}$"
    if re.fullmatch(pattern, token) is None:
        abort(404)

    visit = create_visit(token)

    hurl = db.session.scalar(select(Hurl).where(Hurl.token == token).where(Hurl.is_active == True))
    if not hurl:
        return abort(404)

    hurl.visits.extend([visit])
    db.session.add(hurl)
    db.session.commit()

    file_name = f"{pixel_name}.gif"

    if os.path.isfile(os.path.join(path, file_name)):
        return send_from_directory(path, file_name)

    return send_from_directory(path, "main.gif")
