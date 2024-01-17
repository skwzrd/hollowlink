from datetime import datetime
from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


class UserRole(Enum):
    admin = 1
    user = 2


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    created_datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_modified_datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(Integer, default=UserRole.user.value)

    hurls = relationship("Hurl", back_populates="user", cascade="all, delete")

    def __unicode__(self):
        return self.username


class Visit(db.Model):
    __tablename__ = "visit"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, index=True)
    x_forwarded_for = Column(String, index=True)
    remote_addr = Column(String, index=True)
    referrer = Column(String, index=True)
    content_md5 = Column(String)
    origin = Column(String)
    view_args = Column(String)
    scheme = Column(String)
    method = Column(String)
    root_path = Column(String)
    path = Column(String, index=True)
    query_string = Column(String)
    duration = Column(Float)
    start_datetime_utc = Column(DateTime(timezone=True))
    end_datetime_utc = Column(DateTime(timezone=True))
    user_agent = Column(String)
    x_forwarded_proto = Column(String)
    x_forwarded_host = Column(String)
    x_forwarded_prefix = Column(String)
    host = Column(String)
    connection = Column(String)
    accept = Column(String)
    accept_language = Column(String)
    accept_encoding = Column(String)
    dnt = Column(String)
    upgrade_insecure_requests = Column(String)
    sec_fetch_dest = Column(String)
    sec_fetch_mode = Column(String)
    sec_fetch_site = Column(String)
    sec_fetch_user = Column(String)
    headers = Column(String)
    cookies = Column(String)
    content_length = Column(Integer)

    hurl_id = Column(Integer, ForeignKey("hurl.id"), nullable=False, index=True)
    hurl = relationship("Hurl", back_populates="visits")

    def __unicode__(self):
        return f"Visit {self.id}: {self.x_forwarded_for}: {self.start_datetime_utc}"


class Hurl(db.Model):
    __tablename__ = "hurl"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, index=True)
    name = Column(String)
    pixel_name = Column(String)
    url = Column(String, nullable=False)
    created_datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_modified_datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    deleted_datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    user = relationship("User", back_populates="hurls")

    visits = relationship("Visit", back_populates="hurl", cascade="all, delete")

    def __unicode__(self):
        return f"Hurl {self.id}: {self.name}"


class Contact(db.Model):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    message = Column(String, nullable=False)
    created_datetime = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class Log(db.Model):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True, index=True)
    x_forwarded_for = Column(String, index=True)
    remote_addr = Column(String, index=True)
    referrer = Column(String, index=True)
    content_md5 = Column(String)
    origin = Column(String)
    scheme = Column(String)
    method = Column(String)
    path = Column(String, index=True)
    query_string = Column(String)
    duration = Column(Float)
    start_datetime_utc = Column(DateTime(timezone=True))
    end_datetime_utc = Column(DateTime(timezone=True))
    user_agent = Column(String)
    accept = Column(String)
    accept_language = Column(String)
    accept_encoding = Column(String)
    content_length = Column(Integer)


class Error(db.Model):
    __tablename__ = "error"
    id = Column(Integer, primary_key=True, index=True)
    status_code = Column(Integer)
    details = Column(String)
