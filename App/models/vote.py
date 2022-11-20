from App.database import db
from datetime import datetime
from enum import Enum

class Value (Enum):
    UPVOTE= 1
    DOWNVOTE= -1

class Vote (db.Model):
    id= db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    time= db.Column(db.DateTime, default=datetime.utcnow)
    value= db.Column(Enum(Value), nullable=False)

    
