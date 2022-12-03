from App.database import db
from App.models import voteCommand
from App.models.voteCommand import Action

def create_voteCommand(staff_id, review_id, action):
    vc = voteCommmand(staff_id=staff_id, review_id=review_id, action=action)
    vc.execute()
    return vc.to_json()