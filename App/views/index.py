from flask import Blueprint, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required

index_views = Blueprint("index_views", __name__, template_folder="../templates")


@index_views.route("/", methods=["GET"])
def index_page():
    if not current_user.is_authenticated:
        return render_template("index.html")
    elif current_user.access == "staff":
        return redirect(url_for("student_views.staff_show_all_students"))
    elif current_user.access == "admin":
        return redirect(url_for("student_views.admin_show_all_students"))
    return jsonify({"error": "unauthorized"}), 401
