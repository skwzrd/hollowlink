import secrets

from sqlalchemy import select

from configs import CONSTS
from models import Hurl, User, db


def get_user_by_username(username):
    return db.session.scalar(select(User).where(User.username == username))


def generate_unique_token():
    all_tokens = get_all_tokens()
    while True:
        new_token = secrets.token_hex(CONSTS.token_length)
        if new_token in all_tokens:
            continue
        break
    return new_token


def get_all_tokens():
    tokens = db.session.scalars(select(Hurl.token).distinct()).all()
    return tokens
