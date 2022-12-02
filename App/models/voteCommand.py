#Concrete Command
from App.database import db
from .vote import Vote, Value
from .command import Command
import enum

class Action (enum.Enum):
    UPVOTE= "upvote"
    DOWNVOTE= "downvote"
    REMOVE= "remove"

class VoteCommand (Command):
    __tablename__ = 'voteCommand'
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("review.id"), nullable=False)
    action= db.Column(db.Enum(Action), nullable=False)

    def __init__(self, staff_id, review_id, action):
        self.staff_id= staff_id
        self.review_id=review_id
        self.action=action

    def execute(self)  -> None:
        if (self.action==Action.UPVOTE or self.action==Action.DOWNVOTE):
            self.vote()
        elif (self.action==Action.REMOVE):
            self.remove_vote()
     

    def to_json(self):
        return{
            "id" : self.id,
            "staff_id":self.staff_id,
            "review_id":self.review_id,
            "action":self.action
        }

    #handles creating and updating a vote
    def vote(self):
        try:
            vote= Vote.query.filter(staff_id=self.staff_id, review_id=self.review_id).first()
            if not vote:    #if voting on a review for the first time
                if (self.action==Action.UPVOTE):
                    vote= Vote(staff_id=self.staff_id, review_id= self.review_id, vote_command_id=self.id, value=Value.UPVOTE)
                elif (self.action==Action.DOWNVOTE):
                    vote= Vote(staff_id= self.staff_id, review_id= self.review_id, vote_command_id=self.id, value=Value.DOWNVOTE)
                db.session.add(vote)
                db.session.commit()
                print('Vote created')
                return None
            else:   #if changing a vote
                if (self.action==Action.UPVOTE):
                    vote.value= Value.UPVOTE
                elif (self.action==Action.DOWNVOTE):
                    vote.value= Value.DOWNVOTE
                db.session.add(vote)
                db.session.commit()
                print ('Vote updated')
                return vote
        except Exception as e:
            print('Error creating vote', e)
            db.session.rollback()
            return None
        
    #removes a vote if it is already and upvote and the user upvotes again or it is already a downvote and the user downvotes again
    def remove_vote(self):
        try:
            vote= Vote.query.filter(staff_id=self.staff_id, review_id=self.review_id).first()
            if vote:
                db.session.delete(vote)
                db.session.commit()
                print ('Vote removed')
                return None
            else:
                print('Error removing vote')
                return False 
        except Exception as e:
            print('Error removing vote', e)
            db.session.rollback()
            return None    

        
    