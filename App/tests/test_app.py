import pytest, logging, unittest, os
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import create_db
from App.models import User, Student, Review
from App.controllers.auth import authenticate
from App.controllers.user import (
    create_user,
    get_all_users,
    get_all_users_json,
    get_user,
    get_user_by_username,
    update_user,
    delete_user,
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
    get_review_json,
    get_all_reviews,
    get_all_reviews_json,
    upvote_review,
    downvote_review,
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

    def test_new_admin_user(self):
        user = User("bob", "bobpass", 2)
        assert user.access == 2

    def test_new_normal_user(self):
        user = User("bob", "bobpass", 1)
        assert user.access == 1

    def test_user_is_admin(self):
        user = User("bob", "bobpass", 2)
        assert user.is_admin()

    def test_user_is_not_admin(self):
        user = User("bob", "bobpass", 1)
        assert not user.is_admin()

    # pure function no side effects or integrations called
    def test_to_json(self):
        user = User("bob", "bobpass")
        user_json = user.to_json()
        self.assertDictEqual(user_json, {"access": 1, "id": None, "username": "bob"})

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
        student = Student("bob", "FST", "Computer Science")
        assert (
            student.name == "bob"
            and student.faculty == "FST"
            and student.programme == "Computer Science"
        )

    def test_student_to_json(self):
        student = Student("bob", "FST", "Computer Science")
        student_json = student.to_json()
        self.assertDictEqual(
            student_json,
            {
                "faculty": "FST",
                "id": None,
                "karma": 0,
                "name": "bob",
                "programme": "Computer Science",
            },
        )

    def test_student_karma(self):
        with self.subTest("No reviews"):
            student = Student("bob", "FST", "Computer Science")
            self.assertEqual(student.get_karma(), 0)

        with self.subTest("No reviews"):
            student = Student("bob", "FST", "Computer Science")
            mockReview = Review(1, 1, "good")
            mockReview.vote(1, "up")
            student.reviews.append(mockReview)
            self.assertEqual(student.get_karma(), 1)

        with self.subTest("One negative review"):
            student = Student("bob", "FST", "Computer Science")
            mockReview1 = Review(1, 1, "good")
            mockReview1.vote(1, "down")
            student.reviews.append(mockReview1)
            self.assertEqual(student.get_karma(), -1)


# Unit tests for Review model
class ReviewUnitTests(unittest.TestCase):
    def test_new_review(self):
        review = Review(1, 1, "good")
        assert review.student_id == 1 and review.user_id == 1 and review.text == "good"

    def test_review_to_json(self):
        review = Review(1, 1, "good")
        review_json = review.to_json()
        self.assertDictEqual(
            review_json,
            {
                "id": None,
                "user_id": 1,
                "student_id": 1,
                "text": "good",
                "karma": 0,
                "num_upvotes": 0,
                "num_downvotes": 0,
            },
        )

    def test_review_vote(self):
        with self.subTest("Upvote"):
            review = Review(1, 1, "good")
            review.vote(1, "up")
            self.assertEqual(review.votes["num_upvotes"], 1)

        with self.subTest("Downvote"):
            review = Review(1, 1, "good")
            review.vote(1, "down")
            self.assertEqual(review.votes["num_downvotes"], 1)

    def test_review_get_num_upvotes(self):
        with self.subTest("No votes"):
            review = Review(1, 1, "good")
            self.assertEqual(review.get_num_upvotes(), 0)

        with self.subTest("One upvote"):
            review = Review(1, 1, "good")
            review.vote(1, "up")
            self.assertEqual(review.get_num_upvotes(), 1)

        with self.subTest("One downvote"):
            review = Review(1, 1, "good")
            review.vote(1, "down")
            self.assertEqual(review.get_num_upvotes(), 0)

    def test_review_get_num_downvotes(self):
        with self.subTest("No votes"):
            review = Review(1, 1, "good")
            self.assertEqual(review.get_num_downvotes(), 0)

        with self.subTest("One upvote"):
            review = Review(1, 1, "good")
            review.vote(1, "up")
            self.assertEqual(review.get_num_downvotes(), 0)

        with self.subTest("One downvote"):
            review = Review(1, 1, "good")
            review.vote(1, "down")
            self.assertEqual(review.get_num_downvotes(), 1)

    def test_review_get_karma(self):
        with self.subTest("No votes"):
            review = Review(1, 1, "good")
            self.assertEqual(review.get_karma(), 0)

        with self.subTest("One upvote"):
            review = Review(1, 1, "good")
            review.vote(1, "up")
            self.assertEqual(review.get_karma(), 1)

        with self.subTest("One downvote"):
            review = Review(1, 1, "good")
            review.vote(1, "down")
            self.assertEqual(review.get_karma(), -1)

    def test_review_get_all_votes(self):
        with self.subTest("No votes"):
            review = Review(1, 1, "good")
            self.assertEqual(
                review.get_all_votes(), {"num_upvotes": 0, "num_downvotes": 0}
            )

        with self.subTest("One upvote"):
            review = Review(1, 1, "good")
            review.vote(1, "up")
            self.assertEqual(
                review.get_all_votes(), {1: "up", "num_upvotes": 1, "num_downvotes": 0}
            )

        with self.subTest("One downvote"):
            review = Review(1, 1, "good")
            review.vote(1, "down")
            self.assertEqual(
                review.get_all_votes(),
                {1: "down", "num_upvotes": 0, "num_downvotes": 1},
            )

        with self.subTest("One upvote and one downvote"):
            review = Review(1, 1, "good")
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


# Integration tests for User model
class UsersIntegrationTests(unittest.TestCase):
    def test_authenticate(self):
        user = create_user("bob", "bobpass")
        assert authenticate("bob", "bobpass") is not None

    def test_create_admin(self):
        test_admin = create_user("rick", "rickpass", 2)
        admin = get_user_by_username("rick")
        assert test_admin.username == admin.username and test_admin.is_admin()

    def test_create_user(self):
        test_user = create_user("john", "johnpass", 1)
        user = get_user_by_username("john")
        assert user.username == "john" and not user.is_admin()

    def test_get_user(self):
        test_user = create_user("johnny", "johnpass", 1)
        user = get_user(test_user.id)
        assert test_user.username == user.username

    def test_get_all_users_json(self):
        users = get_all_users()
        users_json = get_all_users_json()
        assert users_json == [user.to_json() for user in users]

    def test_update_user(self):
        user = create_user("danny", "johnpass", 1)
        update_user(user.id, "daniel")
        assert get_user(user.id).username == "daniel"

    def test_delete_user(self):
        user = create_user("bobby", "bobbypass", 1)
        uid = user.id
        delete_user(uid)
        assert get_user(uid) is None


# Integration tests for Student model
class StudentIntegrationTests(unittest.TestCase):
    def test_create_student(self):
        test_student = create_student("bob", "fst", "cs")
        student = get_student(test_student.id)
        assert test_student.name == student.name

    def test_get_students_by_name(self):
        students = get_students_by_name("bob")
        assert students[0].name == "bob"

    def test_get_all_students_json(self):
        students = get_all_students()
        students_json = get_all_students_json()
        assert students_json == [student.to_json() for student in students]

    # tests updating a student's name, programme and/or faculty
    def test_update_student(self):
        with self.subTest("Update name"):
            student = create_student("bob", "fst", "cs")
            update_student(student.id, "bobby")
            assert get_student(student.id).name == "bobby"
        with self.subTest("Update programme"):
            student = create_student("bob", "fst", "cs")
            update_student(student.id, programme="it")
            assert get_student(student.id).programme == "it"
        with self.subTest("Update faculty"):
            student = create_student("bob", "fst", "cs")
            update_student(student.id, faculty="fss")
            assert get_student(student.id).faculty == "fss"
        with self.subTest("Update all"):
            student = create_student("bob", "fst", "cs")
            update_student(student.id, "bobby", "it", "fss")
            assert get_student(student.id).name == "bobby"
            assert get_student(student.id).programme == "it"
            assert get_student(student.id).faculty == "fss"

    def test_delete_student(self):
        student = create_student("bob", "fst", "cs")
        sid = student.id
        delete_student(sid)
        assert get_student(sid) is None


# Integration tests for Review model
class ReviewIntegrationTests(unittest.TestCase):
    def test_create_review(self):
        test_review = create_review(1, 1, "good")
        review = get_review(test_review.id)
        assert test_review.text == review.text

    def test_update_review(self):
        test_review = create_review(1, 1, "good")
        update_review(test_review.id, "bad")
        assert get_review(test_review.id).text == "bad"

    def test_delete_review(self):
        test_review = create_review(1, 1, "good")
        rid = test_review.id
        delete_review(rid)
        assert get_review(rid) is None

    def test_get_review_json(self):
        test_review = create_review(1, 1, "good")
        review_json = get_review_json(test_review.id)
        assert review_json == test_review.to_json()

    def test_get_all_reviews_json(self):
        reviews = get_all_reviews()
        reviews_json = get_all_reviews_json()
        assert reviews_json == [review.to_json() for review in reviews]

    def test_upvote_review(self):
        test_review = create_review(1, 1, "good")
        upvote_review(test_review.id, 1)
        assert get_review(test_review.id).get_num_upvotes() == 1

    def test_downvote_review(self):
        test_review = create_review(1, 1, "good")
        downvote_review(test_review.id, 1)
        assert get_review(test_review.id).get_num_downvotes() == 1
