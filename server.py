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


@app.route("/movies")
def movie_list():
    """ Show list of Movies"""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<m_id>", methods=["GET"])
def movie_detail(m_id):
    """Show details about a specific movie."""

    movie = Movie.query.filter_by(movie_id=m_id).one()

    return render_template("movie_detail.html", movie=movie)


@app.route("/movies/<m_id>", methods=["POST"])
def submit_movie_rating(m_id):
    """Handles user rating for a specific movie."""

    score = request.form.get("rating")
    user = User.query.filter_by(user_id=session["id"]).one()
    user_id = user.user_id
    movie = Movie.query.filter_by(movie_id=m_id).one()
    old_rating = db.session.query(Rating).filter(Rating.movie_id == m_id, Rating.user_id == user_id).first()

    if old_rating:
        old_rating.score = score
        db.session.commit()
        return redirect("/movies/" + str(m_id))

    new_rating = Rating(movie_id=m_id, user_id=user_id, score=score)

    db.session.add(new_rating)
    db.session.commit()

    return redirect("/movies/" + str(m_id))


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()

    return render_template("user_list.html", users=users)


@app.route("/users/<u_id>")
def user_profile(u_id):
    """Shows details about a specific user."""

    user = User.query.filter_by(user_id=u_id).one()

    return render_template("user_detail.html", user=user)


@app.route("/register", methods=["GET"])
def user_sign_up_form():
    """ Display sign up form """

    return render_template("registration_form.html")


@app.route("/register", methods=["POST"])
def user_registration():
    """ Get User's email and password and adds user to the DB"""

    email = request.form.get("email")
    password = request.form.get("password")
    zipcode = request.form.get("zip")  
    query = db.session.query('User')
    users_emails = query.filter(User.email == email).all()

    if users_emails:
        flash("User already exists!")
        return redirect('/sign-up')
    else:
        new_user = User(email=email, password=password, zipcode=zipcode, age=age)
        db.session.add(new_user)
        db.session.commit()

        flash("Registered successfully!")
        return redirect('/')


@app.route("/login", methods=["GET"])
def user_login_form():
    """ Display Login form """

    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def user_login():
    """ Validate User Login """

    email = request.form.get("email")
    password = request.form.get("password")
    query_user = User.query.filter_by(email=email).first()

    if not query_user:
        flash("That email isn't in our system.  It looks like you need to sign up!")
        return redirect("/sign-up")

    if query_user.password != password:
        flash("Incorrect password, please try signing in again")
        return redirect("/login-form")
    else:
        session['id'] = query_user.user_id
        flash("Login successful!")
        return redirect("/users/" + str(session["id"]))


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
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')
