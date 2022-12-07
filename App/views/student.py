from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for
from flask_jwt import jwt_required, current_identity
from flask_login import current_user, login_required

from App.controllers import (
    create_student,
    get_student,
    get_student_by_school_id,
    get_all_students,
    get_students_by_name,
    get_all_student_reviews,
    get_reviews_by_student,
    update_student,
)


student_views = Blueprint("student_views", __name__, template_folder="../templates")


# Create student given name, programme and faculty for Postman
# Must be an admin to access this route
@student_views.route("/api/add-student", methods=["POST"])
@jwt_required()
def add_student_postman():
    data=request.get_json()
    if data["admin_id"] and data["name"] and data["school_id"] and data["programme"] and data["faculty"]:
        student = create_student(admin_id=data["admin_id"], name=data["name"], school_id=data["school_id"], programme=data["programme"], faculty=data["faculty"])
        if student:
            return student.to_json(), 201
        return jsonify({"error": "student not created"}), 400
    return jsonify({"error": "unauthorized access"}), 401


@student_views.route("/add-student", methods=["POST", "GET"])
@login_required
def add_student():
    if request.method == "POST":
        if current_user.access == "admin":
            data = request.form
            if data["name"] and data["school_id"] and data["programme"] and data["faculty"]:
                student = create_student(
                    admin_id=current_user.id, name=data["name"], school_id=data["school_id"], programme=data["programme"], faculty=data["faculty"]
                    )
                if student:
                    flash("Student successfully added!")
                    return redirect(url_for('student_views.admin_show_all_students'))
            flash("Error: There was a problem adding the student.")
            return render_template("add-student.html")
        flash("You are unauthorized to perform this action.")
        return jsonify({"error": "unauthorized", "access":f"{current_user.access}", "username":f"{current_user.username}"}), 401
    return render_template("add-student.html")


# Updates student given student id, name, programme and faculty

# Updates student given student id, name, programme and faculty for Postman
# Must be an admin to access this route
@student_views.route("/api/students/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student_action_postman(student_id):
    admin= get_admin(current_identity.id)
    if admin:
        data = request.json
        student = update_student(
            student_id,
            name=data["name"],
            school_id=data["school_id"],
            programme=data["programme"],
            faculty=data["faculty"],
        )
        if student:
            return jsonify(student.to_json()), 200
        return jsonify({"error": "student not updated"}), 400
    return jsonify({"error": "unauthorized"}), 401


@student_views.route("/edit-student/<school_id>", methods=["POST", "GET"])
@login_required
def edit_student(school_id):
    student = get_student_by_school_id(school_id)
    if not student:
        return jsonify({"error": "student not found"}), 404
    if request.method == "POST":
        if current_user.access == "admin":
            data = request.form
            if data["name"] and data["programme"] and data["faculty"]:
                updated_student = update_student(
                    admin_id=current_user.id, student_id=student.id, name=data["name"], school_id=school_id, programme=data["programme"], faculty=data["faculty"]
                    )
                if updated_student:
                    flash("Student successfully edited!")
                    return redirect(url_for('student_views.admin_show_all_students'))
            flash("Error: There was a problem editing the student.")
            return render_template("edit-student.html", student=student)
        flash("You are unauthorized to perform this action.")
        return jsonify({"error": "unauthorized", "access":f"{current_user.access}", "username":f"{current_user.username}"}), 401
    return render_template("edit-student.html", student=student)


# Lists all students

# Lists all students for Postman
@student_views.route("/api/students", methods=["GET"])
@jwt_required()
def get_all_students_action_postman():
    students = get_all_students()
    if students:
        return jsonify([student.to_json() for student in students]), 200
    return jsonify({"error": "students not found"}), 404


@student_views.route("/admin-students", methods=["GET"])
@login_required
def admin_show_all_students():
    students = get_all_students()
    return render_template("admin-students.html", students=students)


@student_views.route("/staff-students", methods=["GET"])
@login_required
def staff_show_all_students():
    students = get_all_students()
    return render_template("staff-students.html", students=students)


# Gets a student given student id

# Gets a student given student id for Postman
@student_views.route("/api/students/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student_action_postman(student_id):
    student = get_student(student_id)
    if student:
        return jsonify(student.to_json()), 200
    return jsonify({"error": "student not found"}), 404


# Gets a student given their name for Postman
@student_views.route("/api/students/name/<string:name>", methods=["GET"])
@jwt_required()
def get_student_by_name_action_postman(name):
    students = get_students_by_name(name)
    if students:
        return jsonify([student.to_json() for student in students]), 200
    return jsonify({"error": "student not found"}), 404

# Gets a student given their school_id for Postman
@student_views.route("/api/students/school_id/<string:school_id>", methods=["GET"])
@jwt_required()
def get_student_by_school_id_action_postman(school_id):
    students = get_students_by_school_id(school_id)
    if students:
        return jsonify([student.to_json() for student in students]), 200
    return jsonify({"error": "student not found"}), 404

# Lists all reviews for a given student for Postman
@student_views.route("/api/students/<int:student_id>/reviews", methods=["GET"])
@jwt_required()
def get_all_student_reviews_action_postman(student_id):
    reviews = get_all_student_reviews(student_id)
    if reviews:
       return jsonify([review.to_json() for review in reviews]), 200
    return jsonify({"message": "reviews not found"}), 404


@student_views.route("/staff-students/<school_id>", methods=["GET", "DELETE"])
@login_required
def staff_show_all_reviews_for_student(school_id):
    student = get_student_by_school_id(school_id)
    reviews = get_reviews_by_student(student.id)
    return render_template("staff-student-reviews.html", reviews=reviews, current_user=current_user, student=student)


@student_views.route("/admin-students/<school_id>", methods=["GET", "DELETE"])
@login_required
def admin_show_all_reviews_for_student(school_id):
    student = get_student_by_school_id(school_id)
    reviews = get_reviews_by_student(student.id)
    return render_template("admin-student-reviews.html", reviews=reviews, current_user=current_user, student=student)
    

#Search Students for Postman
@student_views.route("/api/students/search/<string:val>", methods=["GET"])
@jwt_required()
def search_postman():
    students=[]
    student=get_student(val)
    if student:
        students.append(student)
    groupA= get_students_by_name(val)
    for student in groupA:
        students.append(student)
    groupB= get_students_by_school_id(val)
    for student in groupB:
        students.append(student)
    if students:
        return jsonify([student.to_json() for student in students]), 200
    else:
        return jsonify({"message": "students not found"}), 404
