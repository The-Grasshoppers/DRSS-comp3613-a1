from .user import User
from .voteCommand import VoteCommand
from App.database import db

class Staff (User):

    __tablename__ = 'staff'
    reviews= db.relationship('Review', backref=db.backref('staff', lazy='joined'))

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)
        self.access = "staff"

    def toJSON(self):
        return{
            'id': self.id,
            'username': self.username,
            'access': 'staff'
        }
    
    #create command
    def create_command(self, review_id, action):
        try:
            command= VoteCommand (staff_id=self.id, review_id= review_id, action=action)
            db.session.add(command)
            db.session.commit()
            return command
        except Exception as e:
            print('Error creating command', e)
            db.session.rollback()
            return None
            

        