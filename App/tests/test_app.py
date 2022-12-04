import pytest, logging, unittest, os
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import create_db
from App.models import User, Student, Review, Admin, Staff
from App.controllers.auth import authenticate
from App.controllers.user import (
    create_user,
    create_admin,
    create_staff,
    get_admin_by_username,
    get_staff_by_username,
    get_all_users,
    get_all_admins,
    get_all_admins_json,
    get_all_staff_json,
    get_user,
    get_admin,
    get_staff,
    get_user_by_username,
    update_user,
    update_admin,
    update_staff,
    delete_user,
    delete_admin,
    delete_staff
)
from App.controllers.student import (
    create_student,
    get_students_by_name,
    get_student,
    get_all_students,
    get_all_students_json,
    update_student,
    delete_student,
)

from App.controllers.review import (
    create_review,
    update_review,
    delete_review,
    get_review,
    get_review_votes,
    get_review_json,
    get_all_reviews,
    get_all_reviews_json,
    vote_on_review
    # upvote_review,
    # downvote_review,
)

from wsgi import app


LOGGER = logging.getLogger(__name__)

"""
   Unit Tests
"""

# Unit tests for User model
class UserUnitTests(unittest.TestCase):
    def test_new_user(self):
        user = User("bob", "bobpass")
        assert user.username == "bob"

    def test_new_admin(self):
        admin = Admin("bob", "bobpass")
        assert admin.username == "bob"
        assert admin.access == "admin"

    def test_new_staff(self):
        staff = Staff("bob", "bobpass")
        assert staff.username == "bob"
        assert staff.access == "staff"

    def test_admin_to_json(self):
        admin = Admin("bob", "bobpass")
        admin_json = admin.to_json()
        self.assertDictEqual(admin_json, {"id": None, "username": "bob", "access": "admin"})

    def test_staff_to_json(self):
        staff = Staff("bob", "bobpass")
        staff_json = staff.to_json()
        self.assertDictEqual(staff_json, {"id": None, "username": "bob", "access": "staff"})

    def test_hashed_password(self):
        password = "mypass"
        hashed = generate_password_hash(password, method="sha256")
        user = User("bob", password)
        assert user.password != password

    def test_check_password(self):
        password = "mypass"
        user = User("bob", password)
        assert user.check_password(password)


# Unit tests for Student model
class StudentUnitTests(unittest.TestCase):
    def test_new_student(self):
        student = Student(1, "bob", "FST", "Computer Science")
        assert (
            student.name == "bob"
            and student.faculty == "FST"
            and student.programme == "Computer Science"
            and student.school_id == 1
        )

    def test_student_to_json(self):
        student = Student(1, "bob", "FST", "Computer Science")
        student_json = student.to_json()
        self.assertDictEqual(
            student_json,
            {
                "id": None,
                "school_id": 1,
                "name": "bob",
                "faculty": "FST",
                "programme": "Computer Science",
                "karma": 0,
            },
        )


    #karma score needs to be checked
    #karma is returning 5 
    def test_student_karma(self):
        with self.subTest("No reviews"):
            student = Student(1, "bob", "FST", "Computer Science")
            self.assertEqual(student.get_karma(), 0)

        with self.subTest("One positive review"):
            student = Student(1, "bob", "FST", "Computer Science")
            mockReview = Review(1, 1, "good", 5)
            vote_on_review(1, 1, "upvote")
            student.reviews.append(mockReview)
            self.assertEqual(student.get_karma(), 6)

        with self.subTest("One negative review"):
            student = Student(1, "bob", "FST", "Computer Science")
            mockReview1 = Review(1, 1, "good", 5)
            vote_on_review(1, 1, "downvote")
            student.reviews.append(mockReview1)
            self.assertEqual(student.get_karma(), 4)


# Unit tests for Review model
class ReviewUnitTests(unittest.TestCase):
    def test_new_review(self):
        review = Review(1, 1, "good", 1)
        assert (
            review.student_id == 1
            and review.staff_id == 1 
            and review.text == "good"
         )


    def test_review_to_json(self):
        review = Review(1, 1, "good", 5)
        review_json = review.to_json()
        self.assertDictEqual(
            review_json,
            {
                "id": None,
                "staff_id": 1,
                "student_id": 1,
                "text": "good",
                "rating": 5,
                "karma": 5,
                "num_upvotes": 0,
                "num_downvotes": 0,
            },
        )

    #not working
    def test_review_vote(self):
        with self.subTest("Upvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            vote_on_review(1,1,"upvote")
            self.assertEqual(review.get_num_upvotes(), 1)

        with self.subTest("Downvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            vote_on_review(1, 1, "downvote")
            self.assertEqual(review.get_num_downvotes(), 1)

    def test_review_get_num_upvotes(self):
        with self.subTest("No votes"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            self.assertEqual(review.get_num_upvotes(), 0)
            self.assertEqual(review.get_num_downvotes(), 0)           

        with self.subTest("One upvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            vote_on_review(1,1,"upvote")
            self.assertEqual(review.get_num_upvotes(), 1)
            self.assertEqual(review.get_num_downvotes(), 0)           

        with self.subTest("One downvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            vote_on_review(1,1,"downvote")
            self.assertEqual(review.get_num_downvotes(), 1)
            self.assertEqual(review.get_num_upvotes(), 0)           

    def test_review_get_num_downvotes(self):
        with self.subTest("No votes"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            self.assertEqual(review.get_num_downvotes(), 0)

        with self.subTest("One upvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            vote_on_review(1,1,"upvote")
            self.assertEqual(review.get_num_downvotes(), 0)

        with self.subTest("One downvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            vote_on_review(1,1,"downvote")
            self.assertEqual(review.get_num_downvotes(), 1)

    def test_review_get_karma(self):
        with self.subTest("No votes"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            self.assertEqual(review.get_karma(), 0)

        with self.subTest("One upvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            vote_on_review(1,1,"upvote")
            self.assertEqual(review.get_karma(), 1)

        with self.subTest("One downvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 5)
            vote_on_review(1,1,"downvote")
            self.assertEqual(review.get_karma(), -1)

    def test_review_get_all_votes(self):
        with self.subTest("No votes"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 1)
            votes = get_review_votes(review.id)
            self.assertEqual(
                None, votes
            )

        with self.subTest("One upvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 1)
            vote_on_review(1,1,"upvote")
            self.assertEqual(
                review.get_all_votes(), {1: "up", "num_upvotes": 1, "num_downvotes": 0}
            )

        with self.subTest("One downvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 1)
            vote_on_review(1,1,"downvote")
            self.assertEqual(
                review.get_all_votes(),
                {1: "down", "num_upvotes": 0, "num_downvotes": 1},
            )

        with self.subTest("One upvote and one downvote"):
            staff = Staff("Jill","jillpass")
            review = Review(1, 1, "good", 1)
            review.vote(1, "up")
            review.vote(2, "down")
            self.assertEqual(
                review.get_all_votes(),
                {1: "up", 2: "down", "num_upvotes": 1, "num_downvotes": 1},
            )


"""
    Integration Tests
"""

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app.config.update({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db"})
    create_db(app)
    yield app.test_client()
    # os.unlink(os.getcwd() + "/App/test.db")




#Integration tests for User model
class UsersIntegrationTests(unittest.TestCase):
    #delete the temp and test db before running each time

    def test_create_admin(self):
        test_admin = create_admin("rick", "rickpass")
        admin = get_admin_by_username("rick")
        assert test_admin.username == admin.username and admin.access == "admin"

    def test_create_staff(self):
        test_staff = create_staff("rick", "rickpass")
        staff = get_staff_by_username("rick")
        assert staff.username == "rick" and staff.access =="staff"

    def test_get_admin(self):
        test_admin = create_admin("joe","joepass")
        admin = get_admin_by_username("joe")
        assert test_admin.username == admin.username

    def test_get_staff(self):
        test_staff = create_staff("joe", "joepass")
        user = get_staff_by_username("joe")
        assert test_staff.username == user.username

    def test_get_all_admins_json(self):
        admins = get_all_admins()
        admins_json = get_all_admins_json()
        assert admins_json == [admin.to_json() for admin in admins]

    def test_update_admin(self):
        admin = create_admin("kyle","pass")
        update_admin(admin.id, "Daniel")
        assert get_admin(admin.id).username == "Daniel"

    def test_update_staff(self):
        staff = create_staff("kyle","pass")
        update_staff(staff.id, "Daniel")
        assert get_staff(staff.id).username == "Daniel"

    def test_delete_admin(self):
        admin = create_admin("rob", "robpass")
        aid = admin.id
        delete_admin(aid)
        assert get_admin(aid) is None
    
    def test_delete_staff(self):
        staff = create_staff("rob", "robpass")
        sid = staff.id
        delete_staff(sid)
        assert get_staff(sid) is None





# Integration tests for Student model
class StudentIntegrationTests(unittest.TestCase):
    
    def test_create_student(self):
        test_student = create_student(1, "billy", 1,"CS","FST")
        student = get_student(1)
        assert "billy" == student.name

    def test_get_students_by_name(self):
        students = get_students_by_name("billy")
        assert students[0].name == "billy"

    def test_get_all_students_json(self):
        students = get_all_students()
        students_json = get_all_students_json()
        assert students_json == [student.to_json() for student in students]

    # # tests updating a student's name, programme and/or faculty
    def test_update_student(self):
        with self.subTest("Update name"):
            test_student = create_student(1, "billy", 1,"CS","FST")
            update_student(1, test_student.id, "bobby", 1, "CS", "FST")
            assert get_student(test_student.id).name == "bobby"
        with self.subTest("Update programme"):
            test_student = create_student(1, "billy", 1,"CS","FST")
            update_student(1, test_student.id, test_student.name, 1, "IT", "FST")
            assert get_student(test_student.id).programme == "IT"
        with self.subTest("Update faculty"):
            test_student = create_student(1, "billy", 1,"CS","FST")
            update_student(1, test_student.id, test_student.name, 1, "CS", "FSS")
            assert get_student(test_student.id).faculty == "FSS"
        with self.subTest("Update all"):
            test_student = create_student(1, "billy", 1,"CS","FST")
            update_student(1, test_student.id, "bobby", 1, "IT", "FSS")
            assert get_student(test_student.id).name == "bobby"
            assert get_student(test_student.id).programme == "IT"
            assert get_student(test_student.id).faculty == "FSS"

    def test_delete_student(self):
        test_student = create_student(1, "billy", 1,"CS","FST")
        sid = test_student.id
        delete_student(sid,1)
        assert get_student(sid) is None



# Integration tests for Review model
 #class ReviewIntegrationTests(unittest.TestCase):
    
    # def test_create_review(self):
    #     test_review = create_review(1, 1, "good")
    #     review = get_review(test_review.id)
    #     assert test_review.text == review.text

    # def test_update_review(self):
    #     test_review = create_review(1, 1, "good")
    #     update_review(test_review.id, "bad")
    #     assert get_review(test_review.id).text == "bad"

    # def test_delete_review(self):
    #     test_review = create_review(1, 1, "good")
    #     rid = test_review.id
    #     delete_review(rid)
    #     assert get_review(rid) is None

    # def test_get_review_json(self):
    #     test_review = create_review(1, 1, "good")
    #     review_json = get_review_json(test_review.id)
    #     assert review_json == test_review.to_json()

    # def test_get_all_reviews_json(self):
    #     reviews = get_all_reviews()
    #     reviews_json = get_all_reviews_json()
    #     assert reviews_json == [review.to_json() for review in reviews]

    # def test_upvote_review(self):
    #     test_review = create_review(1, 1, "good")
    #     upvote_review(test_review.id, 1)
    #     assert get_review(test_review.id).get_num_upvotes() == 1

    # def test_downvote_review(self):
    #     test_review = create_review(1, 1, "good")
    #     downvote_review(test_review.id, 1)
    #     assert get_review(test_review.id).get_num_downvotes() == 1
