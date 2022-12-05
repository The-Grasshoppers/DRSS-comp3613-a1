#Invoker
from App.database import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableDict
from .vote import Vote, Value
from .command import Command


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

    def get_num_upvotes(self):
        if not self.votes:
            return 0
        num_upvotes=0
        for vote in self.votes:
            if (vote.value==Value.UPVOTE):
                num_upvotes= num_upvotes+1
        return num_upvotes
    
    def get_num_downvotes (self):
        if not self.votes:
            return 0
        num_downvotes=0
        for vote in self.votes:
            if (vote.value==Value.DOWNVOTE):
                num_downvotes=num_downvotes+1
        return num_downvotes

    #for a positive or negative review: increases the weight of an upvote or downvote by 1 for each rating above 5 
    #e.g  rating 6/4= +/- 1, rating 7/3= +/- 2, rating 8/2= +/- 3, rating 9/1= +/- 4, rating 10= +/- 5
    #for positive reviews: karma= upvotes-downvotes + rating
    #for negative reviews: karma= downvotes-upvotes + (rating-10) since the rating from a negative review should not increase karma
    # if a review has no votes, it will still have karma from its rating     
    def get_karma (self):
        if (self.rating>5): #positive review
            return (self.rating + (self.rating-5)*self.get_num_upvotes() - (self.rating-5)*self.get_num_downvotes() )
        elif (self.rating<5):   #negative review
            return ((self.rating-10) - (5-self.rating)*self.get_num_upvotes() + (5-self.rating)*self.get_num_downvotes() )
        elif (self.rating==5):  #neutral review
            return (self.rating + self.get_num_upvotes() - self.get_num_downvotes())
        
    """ #simpler way of getting karma score
            if not self.votes:  # if there are no votes the karma score for this review is 0
                return 0    
            if (self.rating>=5):    # positive review
                return (self.get_num_upvotes - self.get_num_downvotes)  
            else:   # negative review 
                return (self.get_num_downvotes- self.get_num_upvotes)
    """

    def to_json(self):
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "student_id": self.student_id,
            "text": self.text,
            "rating": self.rating,
            "karma": self.get_karma(),
            "num_upvotes": self.get_num_upvotes(),
            "num_downvotes": self.get_num_downvotes(),
        }
