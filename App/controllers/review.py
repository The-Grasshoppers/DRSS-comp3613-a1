from App.models import Review, Student, User, Staff, VoteCommand, Vote
from App.database import db
from App.models.vote import Value
from App.models.voteCommand import Action
from App.controllers.vote import get_votes

# Creates a review given a student's school id, user id, review text, and rating
# Returns the review object if successful, None otherwise

def create_review_by_student_id(student_id, staff_id, text, rating):
    staff = Staff.query.get(staff_id)
    student = Student.query.get(student_id)
    if staff and student:
        review = Review.query.filter_by(staff_id=staff_id, student_id=student_id).first()
        if review:
            return "Review exists"
        try:
            review = Review(staff_id, student_id, text, rating)
            db.session.add(review)
            db.session.commit()
            return review
        except:
            return None



def create_review(school_id, staff_id, text, rating):
    staff = Staff.query.get(staff_id)
    student = Student.query.filter_by(school_id=school_id).first()
    if staff and student:
        review = Review.query.filter_by(staff_id=staff_id, student_id=student.id).first()
        if review:
            return None
        try:
            review = Review(staff_id=staff_id, student_id=student.id, text=text, rating=rating)
            db.session.add(review)
            db.session.commit()
            return review
        except:
            return None

# Creates a review given a student id, user id and review text
# Returns the review object if successful, None otherwise
def create_review_postman(student_id, staff_id, text, rating):
    staff = Staff.query.get(staff_id)
    student = Student.query.get(student_id)
    try:
        review = Review(staff_id, student_id, text, rating)
        db.session.add(review)
        db.session.commit()
        return review
    except:
        return ("Review not created")



# Updates a review given a review id and updated review text
# Returns the review object as a json if successful, None otherwise
def update_review(id, text, rating):
    review = Review.query.get(id)
    if review:
        review.text = text
        review.rating= rating
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
    review = Review.query.get(id)
    if not review:
        return None
    return review


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

# Returns the reviews posted by a staff given the staff id
def get_reviews_by_staff(staff_id):
    reviews = Review.query.filter_by(staff_id=staff_id).all()
    return reviews

#Handles voting on a review, updating a vote and removing a vote
def vote_on_review(review_id, staff_id, action):
    review = Review.query.get(review_id)
    staff= Staff.query.get(staff_id)

    if staff and review:

        #converting string action to enum
        if (action=="upvote"):
            actionEnum=Action.UPVOTE    
        elif (action=="downvote"):
            actionEnum=Action.DOWNVOTE
        else:
            return("Invalid action")
    #if ((action!="upvote")and(action!="downvote")):
    #    return ('invalid action')
    
    #actionEnum= Action[action]
    
        #checking for removing a vote. Will remove if an upvote is upvoted or a downvote is downvoted again
        vote= Vote.query.filter_by(staff_id=staff_id, review_id=review_id).first()
        if vote: 
            print("vote found")
            if (((vote.value==Value.UPVOTE) and (actionEnum==Action.UPVOTE)) or ((vote.value==Value.DOWNVOTE) and (actionEnum==Action.DOWNVOTE))):
                actionEnum=Action.REMOVE
                print("Action changed to remove")

        new_voteCommand= VoteCommand(staff_id, review_id,actionEnum)

        db.session.add(new_voteCommand)
        db.session.commit()
        new_voteCommand.execute()
        return new_voteCommand.to_json()
    else:
        return ('Must have a Staff account to vote')


# Gets all votes for a review given the review id
def get_review_votes(id):
    review = Review.query.get(id)
    if review:
        votes = get_votes(id)
        if votes:
            return votes
    return None 


# Gets a review's karma given the review id
def get_review_karma(id):
    review = Review.query.get(id)
    if review:
        return review.get_karma()
    return None
        



