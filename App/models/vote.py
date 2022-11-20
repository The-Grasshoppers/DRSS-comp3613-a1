from App.database import db
from datetime import datetime

class Vote (db.Model):
    id= db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=False)
    time= db.Column(db.DateTime, default=datetime.utcnow)