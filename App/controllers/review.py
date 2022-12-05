from App.models import Review, Student, User, Staff
from App.database import db


# Creates a review given a student id, user id and review text
# Returns the review object if successful, None otherwise
def create_review(student_id, staff_id, text, rating):
    staff = Staff.query.get(staff_id)
    student = Student.query.get(student_id)
    review=Review.query.filter_by(staff_id=staff_id, student_id=student_id)
    if review:
        return None
    else:
        if staff and student:
            try:
                review = Review(staff_id, student_id, text, rating)
                db.session.add(review)
                db.session.commit()
                #staff.reviews.append(review)
                # student.reviews.append(review)
                # db.session.add(staff)
                #db.session.add(student)
                #db.session.commit()
                return review
            except:
                return None



# Updates a review given a review id and updated review text
# Returns the review object as a json if successful, None otherwise
def update_review(id, text):
    review = Review.query.get(id)
    if review:
        review.text = text
        db.session.add(review)
        db.session.commit()
        return review
    return None


# Deletes a review given a review id
# Returns True if successful, False otherwise
def delete_review(id):
    review = Review.query.get(id)
    if review:
        db.session.delete(review)
        db.session.commit()
        return True
    return False


# Returns a review given the review id
def get_review(id):
    return Review.query.get(id)


# Returns a review as a json given the review id
def get_review_json(id):
    review = Review.query.get(id)
    if review:
        return review.to_json()
    return None


# Returns all reviews in the database
def get_all_reviews():
    return Review.query.all()


# Returns all reviews as a json object
# Returns None if no reviews exist
def get_all_reviews_json():
    reviews = Review.query.all()
    if reviews:
        return [review.to_json() for review in reviews]
    return None


# Gets the reviews for a student given the student id
def get_reviews_by_student(student_id):
    reviews = Review.query.filter_by(student_id=student_id).all()
    return reviews


# Returns the reviews posted by a user given the user id
def get_reviews_by_user(user_id):
    reviews = Review.query.filter_by(user_id=user_id).all()
    return reviews


# Upvotes a post given a review id and user id
# Returns the review object if successful, None otherwise
def upvote_review(review_id, user_id):
    review = Review.query.get(review_id)
    user = User.query.get(user_id)
    if review and user:
        review.vote(user_id, "up")
        db.session.add(review)
        db.session.commit()
        return review
    return None


# Downvotes a post given a review id and user id
# Returns the review object if successful, None otherwise
def downvote_review(review_id, user_id):
    review = Review.query.get(review_id)
    user = User.query.get(user_id)
    if review and user:
        review.vote(user_id, "down")
        db.session.add(review)
        db.session.commit()
        return review
    return None


# Gets all votes for a review given the review id
def get_review_votes(id):
    review = Review.query.get(id)
    if review:
        return review.get_votes()
    return None


# Gets a review's karma given the review id
def get_review_karma(id):
    review = Review.query.get(id)
    if review:
        return review.get_karma()
    return None
