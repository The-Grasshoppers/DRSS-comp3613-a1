from App.database import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    text = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    votes = db.relationship(
        "Vote", backref="review", lazy=True, cascade="all, delete-orphan"
    )
    
    def __init__(self, staff_id, student_id, text, rating):
        self.staff_id = staff_id
        self.student_id = student_id
        self.text = text
        self.rating= rating
"""
    def vote(self, user_id, vote):
        self.votes.update({staff_id: vote})
        self.votes.update(
            {"num_upvotes": len([vote for vote in self.votes.values() if vote == "up"])}
        )
        self.votes.update(
            {
                "num_downvotes": len(
                    [vote for vote in self.votes.values() if vote == "down"]
                )
            }
        )

    def get_num_upvotes(self):
        return self.votes["num_upvotes"]

    def get_num_downvotes(self):
        return self.votes["num_downvotes"]

    def get_karma(self):
        return self.get_num_upvotes() - self.get_num_downvotes()

    def get_all_votes(self):
        return self.votes
"""

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "student_id": self.student_id,
            "text": self.text,
            "rating": self.rating,
            "karma": self.get_karma(),
            "num_upvotes": self.get_num_upvotes(),
            "num_downvotes": self.get_num_downvotes(),
        }
