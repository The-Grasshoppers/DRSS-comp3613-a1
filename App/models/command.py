from App.database import db

class Command (db.Model):
    __abstract__ = True
    id= db.Column(db.Integer, primary_key=True)

    def execute(self) -> None:
        pass
