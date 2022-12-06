import pytest, logging, unittest, os
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import create_db
from App.models import User, Student, Review, Admin, Staff
from App.models.vote import Value
from App.controllers.auth import authenticate
from App.controllers.user import (
    create_admin,
    create_staff,
    get_admin_by_username,
    get_staff_by_username,
    get_all_users,
    get_all_admins,
    get_all_staff,
    get_all_admins_json,
    get_all_staff_json,
    get_admin,
    get_staff,
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
    get_student_by_school_id,
    get_all_students,
    get_all_students_json,
    update_student,
    delete_student,
)

from App.controllers.review import (
    create_review_by_student_id,
    update_review,
    delete_review,
    get_review,
    get_review_votes,
    get_review_json,
    get_all_reviews,
    get_all_reviews_json,
    get_reviews_by_student,
    vote_on_review
)

from App.controllers.vote import (
    get_staff_votes
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


    def test_student_karma(self):
        student = Student(1, "bob", "FST", "Computer Science")
        self.assertEqual(student.get_karma(), 0)


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

    def test_review_get_karma(self):
        review = Review(1, 1, "good", 5)
        self.assertEqual(review.get_karma(), 5)
    
    def test_review_upvotes(self):
        review = Review(1, 1, "good", 5)
        self.assertEqual(review.get_num_upvotes(), 0)

    def test_review_downvotes(self):
        review = Review(1, 1, "good", 5)
        self.assertEqual(review.get_num_downvotes(), 0)




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



#Delete the test db before running each time
#Integration tests for User model
class UsersIntegrationTests(unittest.TestCase):
    

    def test_create_admin(self):
        test_admin = create_admin("rick", "rickpass")
        admin = get_admin_by_username("rick")
        assert test_admin.username == admin.username and admin.access == "admin"

    def test_create_staff(self):
        test_staff = create_staff("rick", "rickpass")
        staff = get_staff_by_username("rick")
        assert staff.username == "rick" and staff.access =="staff"

    def test_get_admin(self):
        admin = get_admin(1)
        assert "rick" == admin.username

    def test_get_staff(self):
        staff = get_staff(1)
        assert "rick" == staff.username

    def test_get_all_admins_json(self):
        admins = get_all_admins()
        admins_json = get_all_admins_json()
        assert admins_json == [admin.to_json() for admin in admins]

    def test_get_all_staff_json(self):
        staffs = get_all_staff()
        staffs_json = get_all_staff_json()
        assert staffs_json == [staff.to_json() for staff in staffs]

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

    def test_staff_get_votes(self):
        test_admin = create_admin("brock", "pass")
        test_staff = create_staff("brock", "pass")
        test_student1 = create_student(test_admin.id, "billy", 998,"CS","FST")
        test_student2 = create_student(test_admin.id, "billy", 997,"CS","FST")
        test_review1 = create_review_by_student_id(test_student1.id, test_staff.id, "good", 5)
        test_review2 = create_review_by_student_id(test_student2.id, test_staff.id, "good", 5)
        vote_command1 = vote_on_review(test_review1.id, test_staff.id, "upvote")
        vote_command2 = vote_on_review(test_review2.id, test_staff.id, "upvote")
        votes = get_staff_votes(test_staff.id)
        for vote in votes:
            self.assertEqual(vote.staff_id, test_staff.id)




# # Integration tests for Student model
class StudentIntegrationTests(unittest.TestCase):
    
    def test_create_student(self):
        test_student = create_student(1, "billy", 1,"CS","FST")
        student = get_student_by_school_id(1)
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
    
    def test_get_student_by_school_id(self):
        test_student = create_student(1, "billy", 1,"CS","FST")
        student = get_student_by_school_id(1)
        assert student.school_id == test_student.school_id

    def test_student_karma(self):
        with self.subTest("No Review"):
            test_student = create_student(1, "billy", 10 ,"CS","FST")
            assert test_student.get_karma() == 0

        with self.subTest("One review == 5"):
            test_staff = create_staff("reiner", "pass")
            test_student = create_student(1, "billy", 20 ,"CS","FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)
            assert test_student.get_karma() == 5

        with self.subTest("One review > 5"):
            test_staff = create_staff("tommy", "pass")
            test_student = create_student(1, "billy", 30 ,"CS","FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 6)
            assert test_student.get_karma() == 6

        with self.subTest("One review < 5"):
            test_staff = create_staff("arthur", "pass")
            test_student = create_student(1, "billy", 40 ,"CS","FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 4)
            assert test_student.get_karma() == -6

        with self.subTest("One review == 5, one upvote"):
            test_staff = create_staff("armin", "pass")
            test_student = create_student(1, "billy",50 ,"CS","FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)
            vote_command = vote_on_review(test_review.id, test_staff.id, "upvote")
            assert test_review.get_num_upvotes() == 1
            assert test_student.get_karma() == 6
        
        with self.subTest("One review == 5, one downvote"):
            test_staff = create_staff("annie", "pass")
            test_student = create_student(1, "billy",60 ,"CS","FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)
            vote_command = vote_on_review(test_review.id, test_staff.id, "downvote")
            assert test_review.get_num_downvotes() == 1
            assert test_student.get_karma() == 4
        
        with self.subTest("One review > 5, one upvote"):
            test_staff = create_staff("connie", "pass")
            test_student = create_student(1, "billy",70 ,"CS","FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 6)
            vote_command = vote_on_review(test_review.id, test_staff.id, "upvote")
            assert test_review.get_num_upvotes() == 1
            assert test_student.get_karma() == 7

        with self.subTest("One review > 5, one downvote"):
            test_staff = create_staff("hanji", "pass")
            test_student = create_student(1, "billy",80 ,"CS","FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 6)
            vote_command = vote_on_review(test_review.id, test_staff.id, "downvote")
            assert test_review.get_num_downvotes() == 1
            assert test_student.get_karma() == 5

        with self.subTest("One review < 5, one upvote"):
            test_staff = create_staff("mikasa", "pass")
            test_student = create_student(1, "billy", 90 ,"CS","FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 4)
            vote_command = vote_on_review(test_review.id, test_staff.id, "upvote")
            assert test_review.get_num_upvotes() == 1
            assert test_student.get_karma() == -7
        
        with self.subTest("One review < 5, one downvote"):
            test_staff = create_staff("erwin", "pass")
            test_student = create_student(1, "billy", 11 ,"CS","FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 1)
            vote_command = vote_on_review(test_review.id, test_staff.id, "downvote")
            assert test_review.get_num_downvotes() == 1
            assert test_student.get_karma() == -5




# # Integration tests for Review model
class ReviewIntegrationTests(unittest.TestCase):
    
    def test_create_review_by_student_id(self):
        test_review = create_review_by_student_id(1, 1, "good", 5)
        review = get_review(test_review.id)
        assert test_review.text == review.text
    
    def test_get_review(self):
        test_staff = create_staff("ash", "pass")
        review = create_review_by_student_id(1, test_staff.id, "good", 5)
        test_review = get_review(review.id)
        assert (
            review.id == test_review.id
            and review.student_id == test_review.student_id
            and review.staff_id == test_review.staff_id
            and review.text == test_review.text
         )
    
    def test_update_review(self):
        test_staff = create_staff("bruce", "pass")
        test_review = create_review_by_student_id(1, test_staff.id, "good", 5)
        assert test_review.text == "good"
        update_review(test_review.id, "bad")
        assert get_review(test_review.id).text == "bad"

    def test_delete_review(self):
        test_review = create_review_by_student_id(1, 4, "good", 5)
        assert test_review.text == "good"
        delete_review(test_review.id)
        assert get_review(test_review.id) == None

    def test_get_review_json(self):
        test_staff = create_staff("kimber", "pass")
        test_review = create_review_by_student_id(1, test_staff.id, "good", 5)
        review_json = get_review_json(test_review.id)
        assert review_json == test_review.to_json()

    def test_get_all_reviews_json(self):
        reviews = get_all_reviews()
        reviews_json = get_all_reviews_json()
        assert reviews_json == [review.to_json() for review in reviews]

    def test_upvote_review(self):
        test_staff = create_staff("jimmy", "pass")
        test_review = create_review_by_student_id(1, test_staff.id, "good", 5)
        i = test_review.get_num_upvotes()
        vote_command = vote_on_review(test_review.id, 1, "upvote")
        assert i == 0
        assert test_review.get_num_upvotes() == 1

    def test_downvote_review(self):
        test_staff = create_staff("johnathon", "pass")
        test_review = create_review_by_student_id(1, test_staff.id, "good", 5)
        i = test_review.get_num_downvotes()
        vote_command = vote_on_review(test_review.id, 1, "downvote")
        assert i == 0
        assert test_review.get_num_downvotes() == 1

    def test_review_get_karma(self):
        with self.subTest("No votes"):
            test_admin = create_admin("winston", "pass")
            test_staff = create_staff("winston", "pass")
            test_student = create_student(test_admin.id,"larry",100, "CS", "FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)
            self.assertEqual(test_review.get_karma(), 5)
        
        with self.subTest("One upvote"):
            test_admin = create_admin("vinny", "pass")
            test_staff = create_staff("vinny", "pass")
            test_student = create_student(test_admin.id,"larry",200, "CS", "FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)
            vote_command = vote_on_review(test_review.id, test_staff.id, "upvote")
            self.assertEqual(test_review.get_num_upvotes(), 1)
            self.assertEqual(test_review.get_karma(), 6)

        with self.subTest("Upvote twice by same staff"):
            test_admin = create_admin("jean", "pass")
            test_staff = create_staff("jean", "pass")
            test_student = create_student(test_admin.id,"larry",300, "CS", "FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)
            vote_command = vote_on_review(test_review.id, test_staff.id, "upvote")
            self.assertEqual(test_review.get_num_upvotes(), 1)
            self.assertEqual(test_review.get_karma(), 6)
            vote_command = vote_on_review(test_review.id, test_staff.id, "upvote")
            self.assertEqual(test_review.get_num_upvotes(), 0)
            self.assertEqual(test_review.get_karma(), 5)
        
        with self.subTest("One Downvote"):
            test_admin = create_admin("gerald", "pass")
            test_staff = create_staff("gerald", "pass")
            test_student = create_student(test_admin.id,"larry",400, "CS", "FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)
            vote_command = vote_on_review(test_review.id, test_staff.id, "downvote")
            self.assertEqual(test_review.get_num_downvotes(), 1)
            self.assertEqual(test_review.get_karma(), 4)

        with self.subTest("Downvote twice by same staff"):
            test_admin = create_admin("eren", "pass")
            test_staff = create_staff("eren", "pass")
            test_student = create_student(test_admin.id,"larry",500, "CS", "FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)
            vote_command = vote_on_review(test_review.id, test_staff.id, "downvote")
            self.assertEqual(test_review.get_num_downvotes(), 1)
            self.assertEqual(test_review.get_karma(), 4)
            vote_command = vote_on_review(test_review.id, test_staff.id, "downvote")
            self.assertEqual(test_review.get_num_downvotes(), 0)
            self.assertEqual(test_review.get_karma(), 5)

        with self.subTest("Upvote then downvote by same staff"):
            test_admin = create_admin("levi", "pass")
            test_staff = create_staff("levi", "pass")
            test_student = create_student(test_admin.id,"larry",600, "CS", "FST")
            test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)
            vote_command = vote_on_review(test_review.id, test_staff.id, "upvote")
            self.assertEqual(test_review.get_num_upvotes(), 1)
            self.assertEqual(test_review.get_karma(), 6)
            vote_command = vote_on_review(test_review.id, test_staff.id, "downvote")
            self.assertEqual(test_review.get_num_upvotes(), 0)
            self.assertEqual(test_review.get_num_downvotes(), 1)
            self.assertEqual(test_review.get_karma(), 4)

    def test_review_get_all_votes(self):
        test_admin = create_admin("finn", "pass")
        test_staff = create_staff("finn", "pass")
        test_staff2 = create_staff("polly", "pass")
        test_student = create_student(test_admin.id,"larry",700, "CS", "FST")
        test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5) 
        vote_command = vote_on_review(test_review.id, test_staff.id, "upvote")
        vote_command2 = vote_on_review(test_review.id, test_staff2.id, "upvote")
        votes = get_review_votes(test_review.id)
        for vote in votes:
            self.assertEqual(vote.value, Value.UPVOTE)
    
    def test_get_review_by_student(self):
        test_admin = create_admin("misty", "pass")
        test_staff = create_staff("misty", "pass")
        test_student = create_student(test_admin.id,"larry",800, "CS", "FST")
        test_review = create_review_by_student_id(test_student.id, test_staff.id, "good", 5)       
        reviews = get_reviews_by_student(test_student.id)
        for review in reviews:
            self.assertEqual(test_review.id, review.id)

        
