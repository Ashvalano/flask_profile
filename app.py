from flask import Flask, render_template, request, redirect,url_for,session
from functools import wraps
import hashlib
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.config.update(SECRET_KEY = '1234')
app.config['MYSQL_HOST'] = '192.168.2.125' #'192.168.123.82'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_interns_demo'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)

@app.route("/")
def index():
    if 'loggedin' in session:
        username = session['username']
        firstname = session['firstname']
        lastname = session['lastname']
        return render_template('index.html', username = username, firstname = firstname, lastname = lastname)
    return redirect(url_for('login'))

def LoginRequired(f):
    @wraps(f)
    def DecoratedFunction(*args, **kwargs):
        if session.get('loggedin') is None:
            return redirect('/login', code=302)
        else:
            return f(*args, **kwargs)
    return DecoratedFunction

def LoginNotRequired(f):
    @wraps(f)
    def DecoratedFunction(*args, **kwaargs):
        if 'loggedin' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, **kwaargs)
    return DecoratedFunction


@app.route('/register')
@LoginNotRequired
def register():
    return render_template('register.html')

@app.route('/register', methods = ['GET', 'POST'])
def register_post():
    msg = ''
    if request.method == 'POST' and 'fname' in request.form and 'lname' in request.form and 'uname' in request.form and 'pwd' in request.form and 'confirmPass' in request.form:
        firstname = request.form['fname']
        lastname = request.form['lname']
        username = request.form['uname']
        password = request.form['pwd']
        confirm_password = request.form['confirmPass']
        hashed = hashlib.md5(password.encode())
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        hashed_password = hashed.hexdigest()
        cursor.execute('SELECT * FROM interns_table_2 WHERE username = % s', (username, ))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists'
        elif confirm_password != password:
            msg = 'Password does not match!'
        elif firstname =='' or lastname =='' or username =='' or password=='' or confirm_password =='': 
            msg = 'Please Complete the Form'
        else:
            cursor.execute('INSERT INTO interns_table_2 (fname,lname,username,password) VALUES(%s,%s,%s,%s)', (firstname,lastname,username,hashed_password))
            mysql.connection.commit()
            msg = 'Successfully Registered'
            # return render_template('login,html', msg=msg)
            return redirect(url_for('login'))
    elif request.method == 'POST':
        msg = 'Please Fill out the Form'
    return render_template('register.html', msg=msg)

@app.route('/login')
@LoginNotRequired
def login():
    return render_template('login.html')

@app.route('/login', methods = ['GET', 'POST'])
def login_post():
    msg = ''
    if request.method == 'POST' and 'uname' in request.form and 'pwd' in request.form:
        username = request.form['uname']
        password = request.form['pwd']
        hashed = hashlib.md5(password.encode())
        hashed_password = hashed.hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM interns_table_2 WHERE username = %s AND password = %s', (username, hashed_password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['firstname'] = account['fname']
            session['lastname'] = account['lname']
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/password'
    return render_template('login.html', msg = msg)

@app.route('/logout')
@LoginRequired
def logout():
    session.pop('loggedin', None)
    session.pop('uname', None)
    return redirect(url_for('login'))