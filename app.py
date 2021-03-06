import os

from flask import Flask, render_template, request, flash, redirect, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
# from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc
from werkzeug.exceptions import Unauthorized
from flask_cors import CORS

from forms import UserAddForm, LoginForm, MessageForm, UserEditForm, CSRFForm
from models import db, connect_db, User, Message, Like

database_url = os.environ.get('DATABASE_URL', 'postgresql:///warbler')
# fix incorrect database URIs currently returned by Heroku's pg setup
database_url = database_url.replace('postgres://', 'postgresql://')

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
cors = CORS(app)


# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
# app.config['SQLALCHEMY_DATABASE_URI'] = (
    # os.environ.get('DATABASE_URL', 'postgresql:///warbler'))
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None
    
@app.before_request
def add_csrf_form_to_g():
    """add a wtform to g to protect csrf attack"""

    g.csrf_form = CSRFForm()
    print(g.csrf_form.hidden_tag())


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    # breakpoint()

    form = UserAddForm()
    
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except exc.IntegrityError:
            db.session.rollback()
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)


        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout', methods=["POST"])
def logout():
    """Handle logout of user."""
    
    user= User.query.get_or_404(session[CURR_USER_KEY])
    
    flash(f"{user.username} has logged out")
    
    do_logout()
    
    return redirect("/login")



##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    
    user = User.query.get_or_404(user_id)
    
    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.csrf_form.validate_on_submit():

        followed_user = User.query.get_or_404(follow_id)
        g.user.following.append(followed_user)
        db.session.commit()

    else:
        raise Unauthorized()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.csrf_form.validate_on_submit():

        followed_user = User.query.get(follow_id)
        g.user.following.remove(followed_user)
        db.session.commit()

    else:
        raise Unauthorized()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    form = UserEditForm(obj=g.user)

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if form.validate_on_submit():

        username = form.username.data                   
        email = form.email.data
        image_url = form.image_url.data or User.image_url.default.arg
        header_image_url = form.header_image_url.data or User.header_image_url.default.arg
        bio = form.bio.data
        password = form.password.data

        if User.authenticate(g.user.username, password):
            
            g.user.username = username
            g.user.email = email
            g.user.image_url = image_url
            g.user.header_image_url = header_image_url
            g.user.bio = bio

            db.session.commit()

        else:

            flash("Password does not match")
            return redirect("/")


        return redirect(f"/users/{g.user.id}")

    return render_template('users/edit.html', form=form)
    

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
        
    if g.csrf_form.validate_on_submit():

        if g.user.id == user_id:

            do_logout()

        for message in g.user.messages:
            db.session.delete(message)
        
        db.session.delete(g.user)
        db.session.commit()
        
        return redirect("/signup")

    else:
        raise Unauthorized()
    

@app.route('/users/<int:user_id>/likes')
def liked_messages(user_id):
    """Display all messages that are liked by current user"""

    user = User.query.get_or_404(user_id)

    return render_template('users/likes.html', user=user)



##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>')
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    
    return render_template('messages/show.html',
        msg=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    
    if g.csrf_form.validate_on_submit():

        if g.user.id == msg.user.id:    
            db.session.delete(msg)
            db.session.commit()

        return redirect(f"/users/{g.user.id}")

    else:
        raise Unauthorized()




@app.route('/messages/<int:message_id>/like', methods=["POST"])
def message_like_or_unlike(message_id):
    """Like/Unlike a message"""

    message = Message.query.get_or_404(message_id)

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    else:
        user_id = g.user.id

    if g.csrf_form.validate_on_submit():
        if message.is_liked_by(g.user):
            like = Like.query.get_or_404((user_id, message_id))
            db.session.delete(like)
        else:
            liked_msg = Like(user_id=user_id, message_id=message_id)
            db.session.add(liked_msg)

        db.session.commit()

    else:
        raise Unauthorized()

    # return redirect(f'/messages/{message_id}')
    # breakpoint()
    message = message.serialize()
    
    return jsonify(message)
    


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        following_ids = [followee.id for followee in g.user.following]
        following_ids.append(g.user.id)
        messages = (Message
                    .query
                    .filter(Message.user_id.in_(following_ids))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', 
        messages=messages)

    else:
        return render_template('home-anon.html')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', e=e), 404


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response
