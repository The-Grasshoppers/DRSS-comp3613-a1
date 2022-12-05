from App.database import db
from App.models import Vote
from App.models.vote import Value

# Get all votes for a review, given the review id
def get_votes(review_id):
    votes = Vote.query.filter_by(review_id=review_id)
    if not votes:
        return None
    return votes

# Get all votes of a staff member
def get_staff_votes(staff_id):
    votes = Vote.query.filter_by(staff_id=staff_id)
    if not votes:
        return None
    return votes

# Get staff member's vote from a review
def get_vote_by_staff(review_id, staff_id):
    votes = Vote.query.filter_by(review_id=review_id)
    if not votes:
        return None

    for vote in votes:
        if vote.staff_id == staff_id:
            return vote
    return None