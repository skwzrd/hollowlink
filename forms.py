from flask_sqlalchemy.model import Model
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms.fields import BooleanField, EmailField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from db import get_user_by_username


def get_fields(model: Model, form: FlaskForm, submitted_form: FlaskForm):
    """
    Return a Dict that only contains keys found in our WTForm declarations.
    We do this so users can't sneak in form fields like roles, created dates, etc.
    For extra precaution, we also make sure the form field is in our model.
    """
    d = {}
    form_keys = set(form.__dict__.keys())
    model_keys = set(model.__mapper__.columns.keys())
    submitted_form_keys = set(submitted_form._fields.keys())

    fields = form_keys.intersection(model_keys)

    for field in fields:
        if field not in model_keys and not field.startswith("_"):
            raise ValueError(field)

        if field in submitted_form_keys:
            d[field] = submitted_form[field].data
        else:
            raise ValueError(field)

    return d


V_OPTIONAL = [Optional()]


def validate_whitespace(form, field):
    stripped = field.data.strip()
    if len(stripped) != len(field.data):
        raise ValidationError("Data is padded with whitespace.")


class ContactForm(FlaskForm):
    name = StringField(validators=V_OPTIONAL, description="Optional")
    email = StringField(validators=V_OPTIONAL, description="Optional")
    message = TextAreaField(validators=[InputRequired(), Length(4, 1024)])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    first_name = StringField(validators=V_OPTIONAL, description="Optional")
    last_name = StringField(validators=V_OPTIONAL, description="Optional")
    description = TextAreaField(validators=V_OPTIONAL, description="Optional")
    email = EmailField(validators=V_OPTIONAL, description="Optional")
    password = PasswordField(validators=V_OPTIONAL, description="Optional")
    submit = SubmitField("Save")


class NewUserForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=32), validate_whitespace], description="Required")
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=256)])
    submit = SubmitField("Create")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=32)])
    password = PasswordField(validators=[InputRequired(), Length(max=256)])
    submit = SubmitField("Log in")

    def validate_password(self, field):
        user = get_user_by_username(self.username.data)

        # fail fast
        if not user or not user.username or not user.password:
            raise ValidationError("Incorrect Credentials")

        if not check_password_hash(user.password, self.password.data):
            raise ValidationError("Incorrect Credentials")


class HurlForm(FlaskForm):
    name = StringField(
        validators=[InputRequired(), Length(min=1, max=256)],
        description="This is field is only used to label your Hurl since the generated Hurl may be difficult to remember.",
    )
    is_active = BooleanField(
        validators=V_OPTIONAL,
        default=True,
        description="This field must be checked in order for tracking to begin. If disabled, requests to the resource will return 404 responses.",
    )
    pixel_name = StringField(
        label="Tracking pixel name",
        validators=[InputRequired(), Length(min=1, max=256)],
        default="logo",
        description="This option is available so you can make the tracking pixel appear more innocuous.",
    )

    submit = SubmitField("Submit")
