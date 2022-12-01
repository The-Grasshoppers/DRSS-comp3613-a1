from App.models import Vote, VoteCommand
from App.database import db



def create_vote(staff_id, review_id, action):
    new_vote = VoteCommand(staff_id=staff_id, review=review_id, action=action)
    new_vote.execute()