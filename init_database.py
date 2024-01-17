from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from configs import CONSTS
from models import Contact, Hurl, User, UserRole, Visit, db


def build_db():
    """Init and testing, together."""

    engine = create_engine(CONSTS.SQLALCHEMY_DATABASE_URI)
    db.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.commit()

    admin1 = User(
        first_name="admin",
        last_name="admin",
        username=CONSTS.admin_username,
        description="admin",
        email=CONSTS.admin_username,
        password=generate_password_hash(CONSTS.admin_password),
        role=UserRole.admin.value,
    )

    visit1 = Visit(
        token="token1",
        duration=1.9,
        start_datetime_utc=datetime.utcnow(),
        path="path1",
        query_string="query_string1",
        user_agent="user_agent1",
        headers="headers1",
        content_length="content_length1",
    )

    hurl1 = Hurl(token="token1", name="name1", pixel_name="pixel_name1", url="url1", user=admin1, visits=[visit1])

    contact1 = Contact(
        name="name1",
        email="email1",
        message="message1",
    )

    session.add_all([admin1, contact1, hurl1])
    session.commit()

    hurls = session.scalars(select(Hurl)).all()
    hurl = hurls[0]

    assert len(hurls) == 1
    assert hurl.id == hurl1.id
    assert hurl.user.username == CONSTS.admin_username
    assert hurl.visits[0].token == hurl1.token
    assert len(hurl.visits) == 1

    contact_name = session.scalar(select(Contact.name))
    assert contact_name == contact1.name

    session.delete(contact1)
    session.delete(hurl)
    session.commit()

    hurls = session.scalars(select(Hurl)).all()
    assert len(hurls) == 0


if __name__ == "__main__":
    build_db()
