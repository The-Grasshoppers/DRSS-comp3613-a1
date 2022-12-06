from App.database import db


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id= db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    programme = db.Column(db.String(100), nullable=False)
    reviews = db.relationship(
        "Review", backref="student", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(self,school_id, name, faculty, programme):
        self.school_id= school_id
        self.name=name
        self.faculty = faculty
        self.programme = programme

    def get_karma(self):
        karma = 0
        reviews = self.reviews
        if not reviews:
            return karma

        for review in self.reviews:
            karma += review.get_karma()
        return karma

    def to_json(self):
        return {
            "id": self.id,
            "school_id": self.school_id,
            "name": self.name,
            "faculty": self.faculty,
            "programme": self.programme,
            "karma": self.get_karma(),
        }
