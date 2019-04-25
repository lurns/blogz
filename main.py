from flask import Flask, request, redirect, render_template, flash, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'reallygoodstring'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(900))
    pub_date = db.Column(db.DateTime())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id, pub_date=None):
        self.title = title
        self.body = body
        self.owner_id = owner_id
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#workers
def is_empty(val):
    if val == "":
        return True
    else:
        return False

accepted_routes = ['login', 'entries', 'signup', 'index']

@app.before_request
def require_login():
    if not ('username' in session or request.endpoint in accepted_routes):
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('Welcome back ' + username,'success')
            return redirect('/newpost')
        else:
            flash('Invalid username or password.','error')
            return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            #Validate signup input
            if username == '' or password == '':
                flash('Please enter a valid username and password','error')
                return render_template('signup.html', username=username)
            elif len(username) < 3:
                flash('Username must be 3 or more characters','error')
                return redirect('/signup')
            elif len(password) < 3:
                flash('Password must be 3 or more characters','error')
                return redirect('/signup')
            #Finish validation! Create a user! Woooo
            if password == verify:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('Please make sure passwords match.','error')
                return render_template('signup.html', username=username)
        else:
            flash('Duplicate user.','error')
            return redirect('/signup')
        

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    blogs = Blog.query.all()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        if is_empty(blog_title):
            flash('Please enter a title for your blog entry','error')
        if is_empty(blog_body):
            flash('Please enter some words for your blog entry','error')

        if not is_empty(blog_title) and not is_empty(blog_body):
            if 'username' in session:
                blog_owner  = str(session['username'])
                blog_user = User.query.filter_by(username=blog_owner).one()
                blog_owner_id = int(blog_user.id)


            new_blog = Blog(blog_title, blog_body, blog_owner_id)
            db.session.add(new_blog)
            db.session.commit()

            link = '/blog?id=' + str(new_blog.id)
            return redirect(link)
        
        else:
            return render_template('newpost.html',title='Blogz',
            blogs=blogs,blog_title=blog_title,blog_body=blog_body)
    else:
        return render_template('newpost.html',title='Blogz',blogs=blogs)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/blog')
def entries():
    entry_id = request.args.get("id")
    user_id = request.args.get("user")

    blogs = Blog.query.order_by(Blog.pub_date.desc()).all()
    users = User.query.all()

    if entry_id == None and user_id == None:
        return render_template('blog.html',title='Blogz',blogs=blogs, users=users)
    elif entry_id:
        blog = Blog.query.filter_by(id=entry_id).one()
        return render_template('entry.html',blog=blog, title=blog.title)
    elif user_id:
        user = User.query.filter_by(id=user_id).one()
        user_blogs = Blog.query.filter_by(owner_id=user_id).order_by(Blog.pub_date.desc()).all()
        return render_template('user.html', user=user, user_blogs=user_blogs)

if __name__ == '__main__':
    app.run()