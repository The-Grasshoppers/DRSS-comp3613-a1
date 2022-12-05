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


# Create student given name, programme and faculty
# Must be an admin to access this route
@student_views.route("/api/students", methods=["POST"])
@jwt_required()
def create_student_action():
    if current_identity.is_admin():
        data = request.json
        # student = create_student(
        #     name=data["name"], programme=data["programme"], faculty=data["faculty"]
        # )
        if student:
            return jsonify(student.to_json()), 201
        return jsonify({"error": "student not created"}), 400
    return jsonify({"error": "unauthorized"}), 401


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
# Must be an admin to access this route
@student_views.route("/api/students/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student_action(student_id):
    if current_identity.is_admin():
        data = request.json
        student = update_student(
            student_id,
            name=data["name"],
            programme=data["programme"],
            faculty=data["faculty"],
        )
        if student:
            return jsonify(student.to_json()), 200
        return jsonify({"error": "student not updated"}), 400
    return jsonify({"error": "unauthorized"}), 401


# Lists all students
@student_views.route("/api/students", methods=["GET"])
@jwt_required()
def get_all_students_action():
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
@student_views.route("/api/students/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student_action(student_id):
    student = get_student(student_id)
    if student:
        return jsonify(student.to_json()), 200
    return jsonify({"error": "student not found"}), 404


# Gets a student given their name
@student_views.route("/api/students/name/<string:name>", methods=["GET"])
@jwt_required()
def get_student_by_name_action(name):
    students = get_students_by_name(name)
    if students:
        return jsonify([student.to_json() for student in students]), 200
    return jsonify({"error": "student not found"}), 404


# Deletes a student given student id
# Must be an admin to access this route
@student_views.route("/api/students/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student_action(student_id):
    if current_identity.is_admin():
        outcome = delete_student(student_id)
        if outcome:
            return jsonify({"message": "student deleted"}), 200
        return jsonify({"error": "student not deleted"}), 400
    return jsonify({"error": "unauthorized"}), 401


# Lists all reviews for a given student.
@student_views.route("/api/students/<int:student_id>/reviews", methods=["GET"])
@jwt_required()
def get_all_student_reviews_action(student_id):
    reviews = get_all_student_reviews(student_id)
    return jsonify(reviews), 200


@student_views.route("/staff-students/<student_id>", methods=["GET", "DELETE"])
@login_required
def staff_show_all_reviews_for_student(student_id):
    student = get_student_by_school_id(student_id)
    reviews = get_reviews_by_student(student_id)
    return render_template("staff-student-reviews.html", reviews=reviews, current_user=current_user, student=student)


@student_views.route("/admin-students/<student_id>", methods=["GET", "DELETE"])
@login_required
def admin_show_all_reviews_for_student(student_id):
    student = get_student_by_school_id(student_id)
    reviews = get_reviews_by_student(student_id)
    return render_template("admin-student-reviews.html", reviews=reviews, current_user=current_user, student=student)