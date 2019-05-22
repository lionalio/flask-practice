import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_dance.contrib.facebook import facebook, make_facebook_blueprint
from flask_dance.contrib.google import google, make_google_blueprint
import pymysql

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

# Configure for facebook
app.config["FACEBOOK_OAUTH_CLIENT_ID"] = os.environ.get("FACEBOOK_OAUTH_CLIENT_ID")
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = os.environ.get("FACEBOOK_OAUTH_CLIENT_SECRET")
facebook_bp = make_facebook_blueprint()
app.register_blueprint(facebook_bp, url_prefix="/login")

# Configure for google
app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
google_bp = make_google_blueprint(scope=["profile", "email"])
app.register_blueprint(google_bp, url_prefix="/login")


class Database:
    def __init__(self):
        host = "127.0.0.1"
        user = "root"
        password = ""
        db = "blog"
        self.connection = pymysql.connect(host = host,
                                          user = user,
                                          password = password,
                                          db = db,
                                          cursorclass = pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()

    def add_member(self, new_user, new_password, new_email):
        print("-- " + new_user)
        self.cursor.execute('INSERT INTO members (username, password, email) VALUES (%s, %s, %s)', (new_user, new_password, new_email))
        self.connection.commit()

    def exist_member(self, user_check):
        self.cursor.execute("SELECT id FROM members WHERE username = %s", (user_check,))
        data = self.cursor.fetchone()
        if data is not None:
            return True
        else:
            return False

    def is_member(self, username, passwd):
        self.cursor.execute("SELECT id FROM members WHERE username = %s AND password = %s", (username, passwd))
        data = self.cursor.fetchone()
        if data is not None:
            return True
        else:
            return False
        
    def list_all_blogs(self):
        self.cursor.execute("SELECT title, body FROM entries")
        return self.cursor.fetchall()

    def list_entries(self, username):
        self.cursor.execute("SELECT id, title, body FROM entries  WHERE username = %s", (username))
        return self.cursor.fetchall()
    
    def add_entry(self):
        self.cursor.execute("SELECT id FROM members WHERE username = %s", (session['username']))
        author_id = self.cursor.fetchone()
        self.cursor.execute("INSERT INTO entries (author_id, username, title, body) VALUES (%s, %s, %s, %s)", (author_id['id'], session['username'], request.form['title'], request.form['body']))
        self.connection.commit()
        return redirect(url_for('show_entries'))

    def get_entry(self, entry_id):
        self.cursor.execute("SELECT title, body FROM entries WHERE id = %s", (entry_id))
        return self.cursor.fetchone()
    
db = Database()
    
@app.route('/', methods=['GET', 'POST'])
def show_entries():
    entries = db.list_all_blogs()
    return render_template('home.html', entries = entries)


@app.route('/private', methods=['GET', 'POST'])
def private():
    if request.method == 'POST':
        db.add_entry()
    entries = db.list_entries(session['username'])
    return render_template('private.html', entries = entries)


@app.route('/detailed/<int:entry_id>', methods=['GET'])
def detailed(entry_id):
    entry = db.get_entry(entry_id)      
    return render_template('detailed.html', entry = entry)
    
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    db = Database()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        if db.is_member(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('private'))
        else:
            error = 'Incorrect username or password'
    return render_template('login.html', error = error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('show_entries'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif not email:
            error = 'Email is required'
        elif db.exist_member(username):
            error = 'User {} is already existed'.format(username)
        else:
            session['username'] = username
            db.add_member(username, password, email)
            return redirect(url_for('login'))
    return render_template('register.html', error = error)
        

@app.route('/register_facebook')
def register_facebook():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("/me")
    assert resp.ok, resp.text
    return "Welcome, {name}".format(name=resp.json()['name'])


@app.route('/register_google')
def register_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    assert resp.ok, resp.text
    return "Welcome, {email}".format(email=resp.json()["email"])


if __name__ == "__main__":
    app.run()
