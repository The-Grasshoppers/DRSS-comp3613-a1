from .user import User
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
        