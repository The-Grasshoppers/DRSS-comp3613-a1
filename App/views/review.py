from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for
from flask_jwt import jwt_required, current_identity
from flask_login import current_user, login_required

from App.controllers import (
    create_review,
    get_review,
    get_all_reviews,
    update_review,
    delete_review,
)

review_views = Blueprint("review_views", __name__, template_folder="../templates")


# Create review given user id, student id and text
@review_views.route("/api/reviews", methods=["POST"])
@jwt_required()
def create_review_action():
    data = request.json
    review = create_review(
        user_id=data["user_id"], student_id=data["student_id"], text=data["text"]
    )
    if review:
        return jsonify(review.to_json()), 201
    return jsonify({"error": "review not created"}), 400


# List all reviews
@review_views.route("/api/reviews", methods=["GET"])
@jwt_required()
def get_all_reviews_action():
    reviews = get_all_reviews()
    return jsonify([review.to_json() for review in reviews]), 200


@review_views.route("/admin-reviews", methods=["GET"])
@login_required
def show_all_reviews():
    reviews = get_all_reviews()
    return render_template("admin-reviews.html", reviews=reviews)


# Gets review given review id
@review_views.route("/api/reviews/<int:review_id>", methods=["GET"])
@jwt_required()
def get_review_action(review_id):
    review = get_review(review_id)
    if review:
        return jsonify(review.to_json()), 200
    return jsonify({"error": "review not found"}), 404


# Upvotes post given post id and user id
@review_views.route("/api/reviews/<int:review_id>/upvote", methods=["PUT"])
@jwt_required()
def upvote_review_action(review_id):
    review = get_review(review_id)
    if review:
        review.vote(current_identity.id, "up")
        return jsonify(review.to_json()), 200
    return jsonify({"error": "review not found"}), 404


# Downvotes post given post id and user id
@review_views.route("/api/reviews/<int:review_id>/downvote", methods=["PUT"])
@jwt_required()
def downvote_review_action(review_id):
    review = get_review(review_id)
    if review:
        review.vote(current_identity.id, "down")
        return jsonify(review.to_json()), 200
    return jsonify({"error": "review not found"}), 404


# Updates post given post id and new text
# Only admins or the original reviewer can edit a review
@review_views.route("/api/reviews/<int:review_id>", methods=["PUT"])
@jwt_required()
def update_review_action(review_id):
    data = request.json
    review = get_review(review_id)
    if review:
        if current_identity.id == review.user_id or current_identity.is_admin():
            update_review(review_id, text=data["text"])
            return jsonify({"message": "post updated successfully"}), 200
        else:
            return jsonify({"error": "Access denied"}), 403
    return jsonify({"error": "review not found"}), 404


# Deletes post given post id
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
