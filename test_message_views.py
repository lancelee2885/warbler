"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from flask.helpers import get_flashed_messages
from models import db, User, Message, Follows, Like
from flask_bcrypt import Bcrypt

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()
bcrypt = Bcrypt()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Like.query.delete()

        self.client = app.test_client()

        u = User(
            id = 1,
            email="test@test.com",
            username="testuser",
            password=bcrypt.generate_password_hash("password").decode('UTF-8')
        )

        u2 = User(
            id = 2,
            email="test2@test.com",
            username="testuser2",
            password=bcrypt.generate_password_hash("password").decode('UTF-8')
        )

        db.session.add_all([u, u2])
        db.session.commit()

        m_u1 = Message(
            text = "TestMessage1",
            user_id = u.id
        ) 

        m_u2 = Message(
            text = "TestMessage2",
            user_id = u2.id
        )

        db.session.add_all([m_u1, m_u2])
        db.session.commit()

        self.u = u
        self.u2 = u2
        self.m_u1 = m_u1
        self.m_u2 = m_u2
        
    def tearDown(self):
        """Clean up the database after every test"""
        db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter_by(text="Hello").one()
            self.assertEqual(msg.text, "Hello")

    def test_create_other_user_message(self):
        """make sure creating a message for other user doesn't work"""

        with self.client as client:

            client.post(
                '/login',
                data = {
                    "username" : self.u.username,
                    "password" : "password"
                    }
                )

        set_of_warbles_of_user2 = {message.text for message in Message.query.filter_by(user_id=2)}

        response = client.post(
                '/messages/new',
                data = { "text" : "test1234jdfhjkqhfjkew", "user_id" : "2"})

        self.assertEqual(response.status_code, 302)
        #Check self.u2.messages instead
        self.assertNotIn("test1234jdfhjkqhfjkew", set_of_warbles_of_user2)
        
    def test_create_own_message(self):
        """as a user, test create a message for themself"""
        with self.client as client:

            client.post(
                '/login',
                data = {
                    "username" : self.u.username,
                    "password" : "password"
                    }
                )

            response = client.post(
                '/messages/new',
                data = { "text" : "test1234jdfhjkqhfjkew" },
                follow_redirects=True)

            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("test1234jdfhjkqhfjkew", html)

    def test_delete_own_message(self):
        """as a user, test delete a message for themself"""

        with self.client as client:

            client.post(
                '/login',
                data = {
                    "username" : self.u.username,
                    "password" : "password"
                    }
                )

            response = client.post(f'/messages/{self.m_u1.id}/delete')

            list_of_warbles = {message.text for message in Message.query.all()}

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, f"http://localhost/users/{self.u.id}")
            #use self.u.messages instead of the set
            self.assertNotIn("TestMessage1", list_of_warbles)

    def test_delete_message_not_logged_in(self):
        """as an anonymous user, test deleting a message"""

        with self.client as client:
        
            response = client.post(f'/messages/{self.m_u1.id}/delete')
            
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, "http://localhost/")
            self.assertIn("Access unauthorized.", get_flashed_messages())
            
    def test_create_message_not_logged_in(self):
        """as an anonymous user, test creating a message"""

        with self.client as client:
        
            response = client.post(f'/messages/new')
            
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, "http://localhost/")
            self.assertIn("Access unauthorized.", get_flashed_messages())