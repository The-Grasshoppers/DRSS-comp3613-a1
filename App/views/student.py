from flask import Blueprint, jsonify, request
from flask_jwt import jwt_required, current_identity

from App.controllers import (
    create_student,
    get_student,
    get_all_students,
    get_students_by_name,
    get_all_student_reviews,
    update_student,
    delete_student,
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


# Lists all students for Postman
@student_views.route("/api/students", methods=["GET"])
@jwt_required()
def get_all_students_action_postman():
    students = get_all_students()
    if students:
        return jsonify([student.to_json() for student in students]), 200
    return jsonify({"error": "students not found"}), 404


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
        