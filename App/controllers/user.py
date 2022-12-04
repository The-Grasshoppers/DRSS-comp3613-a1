from App.models import User, Staff, Admin
from App.database import db


# Creates a new user given their username, password and access level
def create_user(username, password, access=1):
    new_user = User(username=username, password=password)
    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except:
        return None


# Creates a new admin given their username and password
def create_admin(username, password):
    new_admin = Admin(username=username, password=password)
    try:
        db.session.add(new_admin)
        db.session.commit()
        return new_admin
    except:
        return None


# Creates a new staff given their username, password
def create_staff(username, password):
    new_staff = Staff(username=username, password=password)
    try:
        db.session.add(new_staff)
        db.session.commit()
        return new_staff
    except:
        return None


# Gets a user by their username
def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


# Gets admin by their username
def get_admin_by_username(username):
    return Admin.query.filter_by(username=username).first()


# Gets staff by their username
def get_staff_by_username(username):
    return Staff.query.filter_by(username=username).first()


# Gets a user by their id
def get_user(id):
    return User.query.get(id)


# Gets an admin by their id
def get_admin(id):
    return Admin.query.get(id)


# Gets a staff by their id
def get_staff(id):
    return Staff.query.get(id)


# Gets all users that have a certain access level
def get_users_by_access(access):
    return User.query.filter_by(access=access).all()


# Gets all users in the database
def get_all_users():
    return User.query.all()


# Gets all admins in the database
def get_all_admins():
    return Admin.query.all()


# Gets all staff in the database
def get_all_staff():
    return Staff.query.all()


# Gets all users and returns them as a JSON object
def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    return [user.to_json() for user in users]


# Gets all admins and returns them as a JSON object
def get_all_admins_json():
    admins = Admin.query.all()
    if not admins:
        return []
    return [admin.to_json() for admin in admins]


# Gets all staff and returns them as a JSON object
def get_all_staff_json():
    staffs = Staff.query.all()
    if not staffs:
        return[]
    return [staff.to_json() for staff in staffs]


# Updates a user's username given their id and username
def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        db.session.add(user)
        return db.session.commit()
    return None


def update_admin(id, username):
    user = get_admin(id)
    if user:
        user.username = username
        db.session.add(user)
        return db.session.commit()
    return None

def update_staff(id, username):
    user = get_staff(id)
    if user:
        user.username = username
        db.session.add(user)
        return db.session.commit()
    return None


# Deletes a user given their id
def delete_user(id):
    user = get_user(id)
    if user:
        db.session.delete(user)
        return db.session.commit()
    return None

def delete_admin(id):
    user = get_admin(id)
    if user:
        db.session.delete(user)
        return db.session.commit()
    return None

def delete_staff(id):
    user = get_staff(id)
    if user:
        db.session.delete(user)
        return db.session.commit()
    return None
