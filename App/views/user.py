from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt import jwt_required, current_identity
from flask_login import current_user

from App.controllers import (
    create_staff,
    get_user,
    get_all_users,
    get_all_users_json,
    get_users_by_access,
    delete_user,
    get_staff_by_username,
    login_user,
    logout_user,
    create_admin,
    get_admin_by_username
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


@user_views.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.cache_control.private = True
    response.cache_control.public = False
    return response


# Log out route
@user_views.route("/logout")
def logout():
    logout_user()
    flash("Log out successful.")
    return redirect(url_for('index_views.index_page'))


# Log in route
@user_views.route("/staff-login", methods=["POST", "GET"])
def staff_login():
    if request.method == "POST":
        data = request.form
        staff = get_staff_by_username(data["username"])
        if staff and staff.check_password(data["password"]):
            login_user(staff)
            flash(f"Log in successful! Welcome, {current_user.username}!")
            return redirect(url_for('student_views.staff_show_all_students'))
        flash("Incorrect login credentials.")
    return render_template("staff-login.html")


@user_views.route("/admin-login", methods=["POST", "GET"])
def admin_login():
    if request.method == "POST":
        data = request.form
        admin = get_admin_by_username(data["username"])
        if admin and admin.check_password(data["password"]):
            login_user(admin)
            flash(f"Log in successful! Welcome, {current_user.username}!")
            return redirect(url_for('student_views.admin_show_all_students'))
        flash("Incorrect login credentials.")
    return render_template("admin-login.html")


# Sign up route
@user_views.route("/api/users", methods=["POST"])
def signup_action():
    data = request.json
    if get_user_by_username(data["username"]):
        return jsonify({"message": "Username taken."}), 400
    user = create_user(
        username=data["username"], password=data["password"], access=data["access"]
    )
    if user:
        return jsonify({"message": f"user {data['username']} created"}), 201
    return jsonify({"message": "User not created"}), 400


@user_views.route("/staff-signup", methods=["POST", "GET"])
def staff_signup():
    if request.method == "POST":
        data = request.form
        if data["username"] and data["password"]:
            if get_staff_by_username(data["username"]):
                flash("Username taken.")
                return render_template("staff-signup.html")
            user = create_staff(
                username=data["username"], password=data["password"]
            )
            if user:
                login_user(user)
                flash(f"Account created! Welcome, {current_user.username}!")
                return redirect(url_for('student_views.staff_show_all_students'))
        flash("Error: There was a problem creating your account")
    return render_template("staff-signup.html")


@user_views.route("/admin-signup", methods=["POST", "GET"])
def admin_signup():
    if request.method == "POST":
        data = request.form
        if data["username"] and data["password"]:
            if get_admin_by_username(data["username"]):
                flash("Username taken.")
                return render_template("admin-signup.html")
            user = create_admin(
                username=data["username"], password=data["password"]
            )
            if user:
                login_user(user)
                flash(f"Account created! Welcome, {current_user.username}!")
                return redirect(url_for('student_views.admin_show_all_students'))
        flash("Error: There was a problem creating your account")
    return render_template("admin-signup.html")


# Get all users route
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
@user_views.route("/api/users/access/<int:access_level>", methods=["GET"])
@jwt_required()
def get_user_by_access_action(access_level):
    if not current_identity.is_admin():
        return jsonify({"message": "Access denied"}), 403
    users = get_users_by_access(access_level)
    if users:
        return jsonify([user.to_json() for user in users]), 200
    return jsonify({"message": "No users found"}), 404
