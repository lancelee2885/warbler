"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from datetime import time
import os
from unittest import TestCase

from models import db, User, Message, Follows, Like
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
    """Test models for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u = User(
            id = 1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            id = 2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([u, u2])
        db.session.commit()

        m_u1 = Message(
            text = "TestMessage1",
            user_id = u.id
        ) 

        m_u2 = Message(
            text = "TestMessage1",
            user_id = u2.id
        )

        db.session.add_all([m_u1, m_u2])
        db.session.commit()

        self.u = u
        self.u2 = u2
        self.m_u1 = m_u1
        self.m_u2 = m_u2
        

    def tearDown(self):
        db.session.rollback()


    def test_message_model(self):
        """Test basic message model
        Add second message to user 1 and 
        test that the message was created
        """

        m = Message(
            text = "TestMessage1",
            user_id = self.u.id
        ) 

        db.session.add(m)
        db.session.commit()

        self.assertEqual(m.text, "TestMessage1")
        self.assertEqual(m.user_id, self.u.id)
        self.assertEqual(len(self.u.messages), 2)

    def test_like_message(self):
        """Test if like association works"""

        like = Like(
            user_id = self.u.id,
            message_id = self.m_u2.id
            )
        #user.likes.append(self.m_u2)

        db.session.add(like)
        db.session.commit()
        message_ids = [message.id for message in self.u.likes]
        self.assertIn(like.message_id ,message_ids)
        #can just test length of likes since setup always has 0 likes

    def test_is_liked_by_method(self):
        """make sure that the method 'is_liked_by()' returns a correct bool"""
        breakpoint()
        like = Like(
            user_id = self.u2.id,
            message_id = self.m_u1.id
            )

        db.session.add(like)
        db.session.commit()

        self.assertTrue(self.m_u1.is_liked_by(self.u2))
        self.assertFalse(self.m_u1.is_liked_by(self.u))
