import flask_login
from flask_jwt import JWT
from App.models import User, Staff, Admin


def authenticate(username, password):
    staff = Staff.query.filter_by(username=username).first()
    if staff and staff.check_password(password):
        return staff
    admin= Admin.query.filter_by(username=username).first()
    if admin and admin.check_password(password):
        return admin
    return None

# Payload is a dictionary which is passed to the function by Flask JWT
def identity(payload):
    user = Staff.query.get(payload["identity"])
    if user:
        return user
    return Admin.query.get(payload["identity"])


def login_user(user, remember):
    return flask_login.login_user(user, remember=remember)


def logout_user():
    flask_login.logout_user()


def setup_jwt(app):
    return JWT(app, authenticate, identity)
