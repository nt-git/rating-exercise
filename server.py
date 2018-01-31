"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()

    return render_template("user_list.html", users=users)


@app.route("/users/<id>")
def user_profile(id):
    """Shows details about a specific user."""

    user = User.query.filter_by(user_id=id).one()

    return render_template("user_detail.html", user=user)


@app.route("/sign-up")
def user_sign_up_form():
    """ Display sign up form """

    return render_template("registration_form.html")


@app.route("/register", methods=["POST"])
def user_registration():
    """ Get User's email and password and adds user to the DB"""

    email = request.form.get("email")
    password = request.form.get("password")
    zipcode = request.form.get("zip")
    age = request.form.get("age")

    query = db.session.query('User')
    users_emails = query.filter(User.email == email).all()
    print users_emails
    if users_emails:
        flash("User already exists!")
        return redirect('/sign-up')
    else:
        new_user = User(email=email, password=password, zipcode=zipcode, age=age)
        db.session.add(new_user)
        db.session.commit()

        flash("Registered successfully!")
        return redirect('/')


@app.route("/login-form")
def user_login_form():
    """ Display Login form """

    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def user_login():
    """ Validate User Login """

    email = request.form.get("email")
    password = request.form.get("password")

    #query = db.session.query('User')
    query_user = User.query.filter_by(email=email).first()
    print query_user

    if query_user is None:
        flash("That email isn't in our system.  It looks like you need to sign up!")
        return redirect("/sign-up")

    if query_user.password != password:
        flash("Incorrect password, please try signing in again")
        return redirect("/login-form")
    else:
        session['id'] = query_user.user_id
        flash("Login successful!")
        print session["id"]
        return redirect("/")


@app.route("/logout")
def user_logout():
    """ Logout User and Redirect to Homepage """

    if session:
        session.clear()

    return redirect('/')




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
