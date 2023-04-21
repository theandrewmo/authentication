from flask import Flask, request, session, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import AddUserForm, LoginForm, FeedbackForm
from werkzeug.exceptions import Unauthorized

app=Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# pass app into function from models
connect_db(app)
db.create_all()

@app.route('/')
def index():
    """ shows homepage """

    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """ shows registration form that will create user """

    if 'username' in session:
        return redirect(f'/users/{session["username"]}')

    form = AddUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username, password, first_name, last_name, email)
        db.session.add(user)
        db.session.commit()

        session['username'] = user.username

        return redirect(f'/users/{user.username}')
        
    else: 
        return render_template('register.html', form=form)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    """ shows login form """

    if 'username' in session:
        return redirect(f'/users/{session["username"]}')

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
            return render_template('login.html', form=form)
        
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def user_details(username):
    """ shows user details"""

    if 'username' not in session or username != session['username']:
        raise Unauthorized()   
        
    user = User.query.get(username)

    return render_template('user_detail.html', user=user)

@app.route('/logout', methods=['POST'])
def logout():
    """ logs user out """

    session.pop('username')

    return redirect('/login')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
     """ deletes user """

     if 'username' not in session or username != session['username']:
        raise Unauthorized()   
     
     User.query.filter_by(username=username).delete()
     db.session.commit()
     session.pop('username')

     return redirect('/')

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def feedback(username):
    """ shows feedback form """

    if 'username' not in session or username != session['username']:
        raise Unauthorized()  

    form = FeedbackForm() 

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username=username)

        db.session.add(new_feedback)
        db.session.commit()

        return redirect(f'/users/{new_feedback.username}')
    
    return render_template('feedback_form.html', form=form)

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """ shows feedback update form and handles form submission """

    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()  
    
    form = FeedbackForm(obj=feedback) 

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        
        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{feedback.username}')
    
    return render_template('feedback_form.html', form=form)

@app.route('/feedback/<feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """ deletes feedback """

    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()  
    
    username = feedback.username

    Feedback.query.filter_by(id=feedback_id).delete()
    db.session.commit()

    return redirect(f'/users/{username}')

@app.errorhandler(404)
def page_not_found(e):
    """ Shows custom 404 page """

    return render_template('404.html')