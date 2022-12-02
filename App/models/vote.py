#Receiver
from App.database import db
from datetime import datetime
import enum

class Value (enum.Enum):
    UPVOTE= 1
    DOWNVOTE= -1

class Vote (db.Model):
    id= db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("review.id"), nullable=False)
    vote_command_id= db.Column(db.Integer, db.ForeignKey("voteCommand.id"), nullable=False)
    time= db.Column(db.DateTime, default=datetime.utcnow)
    value= db.Column(db.Enum(Value), nullable=False)

    def __init__(self,id, staff_id, review_id, vote_command_id,time, value):
        self.id= id
        self.staff_id= staff_id
        self.review_id=review_id
        self.vote_command_id= vote_command_id
        self.time= time
        self.value= value
    
    def to_json(self):
        return{
            "id": self.id,
            "staff_id":self.staff_id,
            "review_id": self.review_id,
            "vote_command_id":self.vote_command_id,
            "time":self.time,
            "value":self.value
        }
       
