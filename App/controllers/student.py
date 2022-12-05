from flask import jsonify
from App.database import db
from App.models import Student, Admin

# Creates a new student given their name, programme and faculty
# Commits the student to the database and returns the student
def create_student(admin_id, name,school_id, programme, faculty):
    admin= Admin.query.get(admin_id)
    if admin:
        return admin.create_student(name,school_id,programme,faculty)
    return False


# Gets a student by their name
def get_students_by_name(name):
    return Student.query.filter_by(name=name).all()


# Gets a student by their id
def get_student(id):
    return Student.query.get(id)


# Gets all students in the database
def get_all_students():
    return Student.query.all()


# Gets all students in the database and returns them as a JSON object
def get_all_students_json():
    students = Student.query.all()
    if not students:
        return []
    return [student.to_json() for student in students]


# Gets all reviews for a student given their id.
# Returns the reviews as a JSON object
def get_all_student_reviews(id):
    student = Student.query.get(id)
    if not student:
        return {"error": "student not found"}, 404
    return [review.to_json() for review in student.reviews], 200


# Updates a student given their id, name, programme and faculty
def update_student(admin_id, student_id, name,school_id, programme, faculty):
    student = Student.query.get(student_id)
    admin= Admin.query.get(admin_id)
    if student and admin:
        return admin.update_student(student, name, school_id, programme, faculty)
    return False

# Deletes a student given their id
def delete_student(student_id, admin_id):
    student = get_student(student_id)
    admin= Admin.query.get(admin_id)
    if student and admin:
        db.session.delete(student)
        db.session.commit()
        return None
    return None

def get_student_by_school_id(school_id):
    return Student.query.filter_by(school_id=school_id).first()
    
