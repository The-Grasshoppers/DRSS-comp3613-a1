from flask import Blueprint, render_template, jsonify, send_from_directory
from flask_jwt import jwt_required, current_identity
from flask import request
import flask_login
from flask_jwt import JWT

from App.controllers import (
    create_user,
    create_admin,
    create_staff,
    get_user,
    get_admin,
    get_staff,
    get_all_users,
    get_all_admins,
    get_all_staff,
    get_all_users_json,
    get_all_admins_json,
    get_all_staff_json,
    get_users_by_access,
    delete_user,
    get_user_by_username,
    get_staff_by_username,
    get_admin_by_username,
    login_user,
    authenticate
)

user_views = Blueprint("user_views", __name__, template_folder="../templates")


@user_views.route("/users", methods=["GET"])
def get_user_page():
    users = get_all_users()
    return render_template("users.html", users=users)


@user_views.route("/static/users", methods=["GET"])
def static_user_page():
    return send_from_directory("static", "static-user.html")


@user_views.route("/identify", methods=["GET"])
@jwt_required()
def identify_user_action():
    return jsonify(
        {
            "message": f"username: {current_identity.username}, id : {current_identity.id}"
        }
    )


# Sign up route
@user_views.route("/api/users", methods=["POST"])
def signup_action():
    data = request.get_json() 
    if get_user_by_username(data["username"]):
        return jsonify({"message": "Username taken."}), 400
    user = create_user(
        username=data["username"], password=data["password"], access=data["access"]
    )
    if user:
        return jsonify({"message": f"user {data['username']} created"}), 201
    return jsonify({"message": "User not created"}), 400

# Get all users route for Postman
# Must be an admin to access this route
@user_views.route("/api/users", methods=["GET"])
@jwt_required()
def get_users_action():
    if current_identity.is_admin():
        users = get_all_users_json()
        return jsonify(users), 200
    return jsonify({"message": "Access denied"}), 403

# Get user by id route
# Must be an admin to access this route
@user_views.route("/api/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_action(user_id):
    if not current_identity.is_admin():
        return jsonify({"message": "Access denied"}), 403
    user = get_user(user_id)
    if user:
        return jsonify(user.to_json()), 200
    return jsonify({"message": "User not found"}), 404


# Delete user route
# Must be an admin to access this route
@user_views.route("/api/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user_action(user_id):
    if not current_identity.is_admin():
        return jsonify({"message": "Access denied"}), 403
    user = get_user(user_id)
    if user:
        delete_user(user_id)
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"message": "User not found"}), 404


# Get user by access level route
# Must be an admin to access this route
@user_views.route("/api/users/access/<string:access>", methods=["GET"])
@jwt_required()
def get_user_by_access_action(access):
    if not current_identity.is_admin():
        return jsonify({"message": "Access denied"}), 403
    users = get_users_by_access(access_level)
    if users:
        return jsonify([user.to_json() for user in users]), 200
    return jsonify({"message": "No users found"}), 404

#POSTMAN ROUTES

# Staff Log in route for Postman
@user_views.route("/api/staff-login", methods=['GET'])
def staff_login_action():
    data=request.form
    username= request.args.get('username')
    password= request.args.get('password')
    staff=authenticate(username,password)
    if staff and get_staff(staff.id):
        return jsonify({"message":"Logged in"}), 200
    return jsonify({"message": "Incorrect username or password"}), 401


# Admin Log in route for Postman
@user_views.route("/api/admin-login", methods=["POST", "GET"])
def admin_login_action():
    #if request.method == "POST":
    data=request.get_json()
    admin = get_admin_by_username(data["username"])
    if admin and admin.check_password(data["password"]):
        login_user(admin)
        return jsonify({ "message":f"Log in successful! Welcome, {current_user.username}!"}), 200
    return jsonify({"message": "Incorrect username or password"}), 401
    #return jsonify({"message": "User not logged in"}), 400

# Staff Sign up route for Postman 
@user_views.route("/api/staff-signup", methods=['GET'])
def staff_signup():
    data=request.form
    username= request.args.get('username')
    password= request.args.get('password')
    user = create_staff(username=username, password=password)
    if user:
        return jsonify({"message": f"user {username} created"}), 201
    else:
        return jsonify({"message": "User not created"}), 400

#Admin Sign up route for Postman
@user_views.route("/api/admin-signup", methods=['GET'])
def admin_signup():
    data=request.form
    username= request.args.get('username')
    password= request.args.get('password')
    user = create_admin(username=username, password=password)
    if user:
        return jsonify({"message": f"user {username} created"}), 201
    else:
       return jsonify({"message": "User not created"}), 400

    