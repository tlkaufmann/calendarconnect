from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, g
import sqlite3
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from os import urandom
from functools import wraps

app = Flask(__name__)
app.debug = True

# SQlite stuff
DATABASE = 'database.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles/<string:id>/')
def article(id):
    return render_template('article.html', id = id)

class RegisterForm(Form):
    name = StringField('Name', validators=[validators.input_required()])
    username = StringField('Username', validators=[validators.input_required()])
    email  = StringField('Email', validators=[validators.Length(min = 3, max = 30)])
    password  = PasswordField('Password', validators= [
        validators.Length(min = 3, max = 30),
        validators.DataRequired(),
        validators.EqualTo('pw_confirm', message='PW do not match')])
    pw_confirm = PasswordField('Confirm Password')

class LoginForm(Form):
    username = StringField('Username', validators=[validators.input_required()])
    password  = PasswordField('Password', validators= [
        validators.Length(min = 3, max = 30),
        validators.DataRequired()])

class WebsiteForm(Form):
    website = StringField('Website', validators=[validators.input_required()])
    sample_title = StringField('Sample Title', validators=[validators.input_required()])
    
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = str(sha256_crypt.encrypt((form.password.data)))

        #SQlite stuff
        cursor = get_db().cursor()
        cursor.execute("""INSERT INTO users(name, email, username, password) VALUES(?, ?, ?, ?)""", (name, email, username, password))
        get_db().commit()
        get_db().close()

        flash('You are now registered', 'success')

        return redirect(url_for('login'))


    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        # Get Form Fields
        username = form.username.data
        password_candidate = form.password.data

        # Create cursor
        cursor = get_db().cursor()

        # Get user by username
        result = query_db('select * from users where username = ?', (username, ))

        if result:
            # Get stored hash
            password = result[0]['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', form = form, error=error)
            # Close connection
            get_db().close()
        else:
            error = 'Username not found'
            return render_template('login.html', form = form, error=error)

    return render_template('login.html', form = form)


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html', session=session)

@app.route('/settings', methods=['GET', 'POST'])
@is_logged_in
def settings():
    form = WebsiteForm(request.form)

    if request.method == 'POST':
        # Get Form Fields
        website = form.website.data
        sample_title = form.sample_title.data

        cursor = get_db().cursor()
        cursor.execute("""INSERT INTO websites(user, url, sample_title) VALUES(?, ?, ?)""", 
                                        (session['username'], website, sample_title))
        get_db().commit()

        flash('Page submitted', 'success')
    

    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM websites WHERE user='{}'".format(session['username']))
    data = cursor.fetchall()
    get_db().close()

    return render_template('settings.html', session=session, form = form, data = data)



if __name__ == '__main__':
    app.secret_key = urandom(24)
    app.run()