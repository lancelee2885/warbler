"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from flask_bcrypt import Bcrypt
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()
bcrypt = Bcrypt()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        self.u = u
        self.u2 = u2

        db.session.add_all([u, u2])
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u.messages), 0)
        self.assertEqual(len(self.u.followers), 0)

    def test_user_following(self):
        """Tests if the following association between users works"""

        follow = Follows(
            user_being_followed_id=self.u2.id,
            user_following_id=self.u.id)
        # breakpoint()
        # self.u2.following.append(self.u)

        db.session.add(follow)
        db.session.commit()

        #User 1 should be following user 2
        self.assertTrue(self.u.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u))
    
    def test_user_is_followed_by(self):
        """Test if is_followed_by function works"""

        follow = Follows(
            user_being_followed_id=self.u2.id,
            user_following_id=self.u.id)

        db.session.add(follow)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u))
        self.assertFalse(self.u.is_followed_by(self.u2))


    def test_repr_(self):
        """Test if __repr__ method works"""

        self.assertEqual(str(self.u), 
            f"<User #{self.u.id}: {self.u.username}, {self.u.email}>")

    
    def test_valid_signup(self):
        """Test if User.signup successfully create a new user given valid credentials"""

        username = "testuser3"
        email = "testuser3@email.com"
        password = "HASHED_PASSWORD"
        image_url = "http://test.jpeg"
        id = 100000000

        user = User.signup(username, email, password, image_url)
        user.id = id
        db.session.commit()

        user = User.query.get(id)

        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertTrue(bcrypt.check_password_hash(user.password, password))
        self.assertEqual(user.image_url, image_url)


    def test_invalid_signup(self):
        """Test if signing up with an invalid email throws an integrity error"""
        username = "testuser3"
        email = None
        password = "HASHED_PASSWORD"
        image_url = "http://test.jpeg"

        with self.assertRaises(exc.IntegrityError):
            user = User.signup(username, email, password, image_url)
            db.session.commit()

    def test_user_authentication(self):
        """Tests if the user authentication class method correctly works"""
        self.u.password = bcrypt.generate_password_hash(self.u.password).decode('UTF-8')
        db.session.commit()
        user = User.authenticate(self.u.username, "HASHED_PASSWORD")

        self.assertEqual(user, self.u)

    def test_ivalid_user_authentication(self):
        """tests invalid username and password on authenticate method"""

        self.u2.password = bcrypt.generate_password_hash(self.u2.password).decode('UTF-8')
        db.session.commit()

        user = User.authenticate("bazinga", "HASHED_PASSWORD")
        self.assertFalse(user)

        user = User.authenticate(self.u2.username, "bazinga")
        self.assertFalse(user)