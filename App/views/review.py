from flask import Blueprint, jsonify, request
from flask_jwt import jwt_required, current_identity

from App.controllers import (
    create_review,
    get_review,
    get_all_reviews,
    update_review,
    delete_review,
)

review_views = Blueprint("review_views", __name__, template_folder="../templates")


# Create review given user id, student id and text for Postman
@review_views.route("/api/reviews", methods=["POST"])
@jwt_required()
def create_review_action():
    data = request.json
    review = create_review(
        student_id=data["student_id"],staff_id=data["staff_id"],  text=data["text"], rating=data["rating"]
    )
    if review:
        return jsonify(review.to_json()), 201
    return jsonify({"error": "review not created"}), 400

#Add reviews by student for Postman testing
@review_views.route("/api/add-review/<student_id>", methods=["POST", "GET"])
@jwt_required
def add_review_by_student(student_id):
    if request.method == "POST":
        if current_user.access == "staff":
            data = request.json
            if data["student_id"] and data["text"] and data["rating"]:
                review = create_review(
                    student_id=data["student_id"],
                    staff_id=current_user.id, text=data["text"], rating=data["rating"]
                    )
                if review:
                    return jsonify(review.to_json()), 201
            return jsonify({"error": "review not created"}), 400
        return jsonify({"error": "Access denied"}), 403

# List all reviews for Postman
@review_views.route("/api/reviews", methods=["GET"])
@jwt_required()
def get_all_reviews_action():
    reviews = get_all_reviews()
    return jsonify([review.to_json() for review in reviews]), 200


# Gets review given review id for Postman
@review_views.route("/api/reviews/<int:review_id>", methods=["GET"])
@jwt_required()
def get_review_action(review_id):
    review = get_review(review_id)
    if review:
        return jsonify(review.to_json()), 200
    return jsonify({"error": "review not found"}), 404

#Upvote, downvote or remove vote given review_id, current identity and action for Postman
#If the action is upvote and the review is already upvoted the action changes to remove vote, same for downvote
#Only the staff can vote
@review_views.route("/api/reviews/<int:review_id>/<string: action>", methods=["PUT"])
@jwt_required
def vote_action(review_id, action):
    data= request.json()
    message= vote_on_review(review_id, current_identity.id, action)
    if (message=="Must have a Staff account to vote")
        return jsonify({"message": f"{message}"}), 400
    else:   
        return jsonify(message), 200


# Updates post given post id and new text for Postman
# Only the original reviewer can edit a review
@review_views.route("/api/reviews/<int:review_id>", methods=["PUT"])
@jwt_required()
def update_review_action(review_id):
    data = request.json
    review = get_review(review_id)
    if review:
        if (current_identity.id == review.user_id):
            update_review(review_id, text=data["text"], rating=data["rating"])
            return jsonify({"message": "post updated successfully"}), 200
        else:
            return jsonify({"error": "Access denied"}), 403
    return jsonify({"error": "review not found"}), 404


# Deletes post given post id for Postman
# Only admins or the original reviewer can delete a review
@review_views.route("/api/reviews/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review_action(review_id):
    review = get_review(review_id)
    if review:
        if current_identity.id == review.user_id or current_identity.is_admin():
            delete_review(review_id)
            return jsonify({"message": "post deleted successfully"}), 200
        else:
            return jsonify({"error": "Access denied"}), 403
    return jsonify({"error": "review not found"}), 404


# Gets all votes for a given review
@review_views.route("/api/reviews/<int:review_id>/votes", methods=["GET"])
@jwt_required()
def get_review_votes_action(review_id):
    review = get_review(review_id)
    if review:
        return jsonify(review.get_all_votes()), 200
    return jsonify({"error": "review not found"}), 404
