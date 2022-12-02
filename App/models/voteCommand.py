from App.database import db
from .vote import Vote, Value
from .command import Command
import enum

class Action (enum.Enum):
    UPVOTE= "upvote"
    DOWNVOTE= "downvote"

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
                print('Succesful vote')
                return None
            else:   #if changing a vote
                if ((self.action==Action.UPVOTE) and (vote.value==Value.DOWNVOTE)):
                    vote.value= Value.UPVOTE
                    db.session.add(vote)
                    db.session.commit()
                    return vote
                elif ((self.action==Action.DOWNVOTE) and (vote.value==Value.UPVOTE)):
                    vote.value= Value.DOWNVOTE
                    db.session.add(vote)
                    db.session.commit()
                    return vote
                elif (((self.action==Action.UPVOTE) and (vote.value==Value.UPVOTE)) or ((self.action==Action.DOWNVOTE) and (vote.value==Value.DOWNVOTE))):
                    db.session.delete(vote)
                    db.session.commit()
                    print ('Vote removed')
                    return None
        except Exception as e:
            print('Error handling this vote', e)
            db.session.rollback()
            return None
        
    