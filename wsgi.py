import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from App.models.vote import Value
from App.database import create_db, get_migrate
from App.main import create_app
from App.controllers import (
    create_staff,
    create_admin, 
    create_student,
    create_review_by_student_id,
    get_review,
    get_all_users_json, 
    get_all_users,  
    get_all_admins,
    get_all_staff,
    get_all_reviews,
    get_all_students,
    get_review_votes,
    get_staff,
    get_review,
    delete_review,
    vote_on_review,
)

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)


# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    create_db(app)
    print("database intialized")


"""
User Commands
"""

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup("user", help="User object commands")


# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f"{username} created!")


# this command will be : flask user create bob bobpass


@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == "string":
        print(get_all_users())
    else:
        print(get_all_users_json())


app.cli.add_command(user_cli)  # add the group to the cli


"""
Generic Commands
"""


@app.cli.command("init")
def initialize():
    create_db(app)
    print("database intialized")


"""
Test Commands
"""




admin = AppGroup("admin", help="Testing admin")

@admin.command("create", help="Creates an admin")
@click.argument("username", default="bob")
@click.argument("password", default="bobpass")
def create_admin_command(username, password):
    create_admin(username, password)
    print(f"{username} created!")


@admin.command("list", help="Lists admins in the database")
def list_admin_command():
    admins = get_all_admins()
    for admin in admins:
        print(admin.username)
        print (admin.id)

app.cli.add_command(admin)



staff = AppGroup("staff", help="Testing staff")

@staff.command("create", help="Creates a staff")
@click.argument("username", default="Sue")
@click.argument("password", default="suepass")
def create_staff_command(username, password):
    create_staff(username, password)
    print(f"{username} created!")


@staff.command("list", help="Lists staff in the database")
def list_staff_command():
    staffs = get_all_staff()
    for staff in staffs:
        print(staff.username)
        print(staff.id)

@staff.command("get", help="Get a staff member by their id")
def get_staff_by_id_command():
    id=1
    staff=get_staff(1)
    if staff:
        print(staff.id)
        print(staff.username)
        print(staff.access)
    else:
        print("Staff not found")

app.cli.add_command(staff)



review_cli = AppGroup('review', help="Review object commands")
@review_cli.command("create", help="Create a review")
@click.argument("student_id", default="1")
@click.argument("staff_id", default="1")
@click.argument("text", default="good")
@click.argument("rating", default="6")
def create_review_command(student_id, staff_id, text, rating):
    message = create_review(student_id, staff_id, text, rating)
    print(message)


@review_cli.command("list", help="Lists reviews in the database")
def list_review_command():
    reviews = get_all_reviews()
    if reviews:
        for review in reviews:
            print("Here's a review")
            print(review.staff_id)
            print(review.student_id)
            print(review.text)
            print(get_review_votes(review.id))
    else:
        print("No reviews")

@review_cli.command("get", help="Get a review by its id")
def get_review_by_id_command():
    id=1
    review= get_review(id)
    if review:
        print(review.text)
        print(review.rating)
    else:
        print("Review not found")

@review_cli.command("upvotes", help="Lists staff in the database")
@click.argument("review_id", default="1")
def review_upvotes_command(review_id):
    review = get_review(review_id)
    if not review:
        print("No review found")
    num_upvotes = review.get_num_upvotes()
    print(num_upvotes)

@review_cli.command("delete", help="Delete a review")
def delete_review_by_id_command():
    id=1
    deleted=delete_review(1)
    if (deleted==True):
        print("Review deleted")
    else:
        print("Not deleted")

app.cli.add_command(review_cli)


student_cli = AppGroup('student', help="Student object commands")
@student_cli.command("create", help="Create a student")
@click.argument("admin_id", default="1")
@click.argument("name", default="Joe")
@click.argument("school_id", default="1")
@click.argument("programme", default="CS")
@click.argument("faculty", default="FST")
def create_review_command(admin_id, name, school_id, programme, faculty):
    create_student(admin_id, name, school_id, programme, faculty)
    print(f'Student created!')


@student_cli.command("list", help="Lists students in the database")
def list_students_command():
    students = get_all_students()
    for student in students:
        print(student.name)
        #print(student.get_karma)
    

app.cli.add_command(student_cli)



vote_cli = AppGroup('vote', help="Vote object commands")
@vote_cli.command("upvote", help="Create a vote")
@click.argument("review_id", default="1")
@click.argument("staff_id", default="1")
def create_vote_command(review_id, staff_id):
    action = "upvote"
    voteCommand = vote_on_review(review_id,staff_id,action)
    print(voteCommand)

@vote_cli.command("downvote", help="Create a vote")
@click.argument("review_id", default="1")
@click.argument("staff_id", default="2")
def create_vote_command(review_id, staff_id):
    action = "downvote"
    voteCommand = vote_on_review(review_id,staff_id,action)
    print(voteCommand)

    

app.cli.add_command(vote_cli)


test = AppGroup("test", help="Testing commands")


@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


@test.command("student", help="Run Student tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "StudentUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "StudentIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


@test.command("review", help="Run Student tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "ReviewUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "ReviewIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


app.cli.add_command(test)
