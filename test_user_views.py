"""User view tests."""

import os

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from unittest import TestCase
from flask.helpers import get_flashed_messages
from app import app, do_login
from flask import flash
from flask_bcrypt import Bcrypt
from models import db, User, Message, Follows, Like
from sqlalchemy import exc

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler-test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

db.create_all()
bcrypt = Bcrypt()

class UserViewTestCase(TestCase):
    """Test view functions and routes for the app"""

    def setUp(self):
        """Run this function before each test to set up database"""
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

    def test_sign_up(self):
        """Test if a user can sign up"""

        with self.client as client:
            
            # testing a valid signup
            response = client.post(
                '/signup',
                data = {
                    "username" : "testuser3",
                    "password" : "password",
                    "email" : "testuser3@email.com",
                    "image_url" : "http://test.jpeg"
                    },
                follow_redirects=False)
            
            self.assertEqual(response.status_code, 302)
        
            #separate this as different test
            client.post(
                '/signup',
                data = {
                    "username" : "testuser3",
                    "password" : "password",
                    "email" : "testuser34123@email.com",
                    "image_url" : "http://test.jpeg"
                    },
                follow_redirects=False)

            self.assertIn("Username already taken", get_flashed_messages())

        

    def test_logging_in(self):
        """Make sure that a user with correct username/pass can log in"""
        with self.client as client:
            
            response = client.post(
                '/login',
                data = {
                    "username" : self.u.username,
                    "password" : "password"
                    },
                follow_redirects=False)

            self.assertEqual(response.status_code,302)
            self.assertIn(f"Hello, {self.u.username}!", get_flashed_messages())

    def test_followers_following_list_authorized(self):
        """Test if a logged in user can see the follower / following pages"""

        # user2 following user1
        # follow = Follows(user_being_followed_id=1, user_following_id=2)

        self.u2.following.append(self.u)
        db.session.commit()

        with self.client as client:

            client.post(
                '/login',
                data = {
                    "username" : self.u.username,
                    "password" : "password"
                    },
                )

            response = client.get("/users/2/following")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('"/users/1"' ,html)
            
            response = client.get("/users/1/followers")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('"/users/2"' ,html)
    
    def test_followers_following_list_unauthorized(self):
        """Make sure an anon user cannot see the follower / following pages of any users"""

        self.u2.following.append(self.u)
        db.session.commit()

        with self.client as client:
            response = client.get("/users/2/following")

            self.assertEqual(response.location, "http://localhost/")
            self.assertIn('Access unauthorized.', get_flashed_messages())

            response2 = client.get("/users/2/followers")

            self.assertEqual(response2.location, "http://localhost/")
            self.assertIn('Access unauthorized.', get_flashed_messages())


