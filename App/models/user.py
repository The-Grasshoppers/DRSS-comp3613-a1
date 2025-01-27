from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    access = db.Column(db.String(20), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)     
    
    def to_json(self):
        return {"id": self.id, "username": self.username}

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
