from flask import Flask, request, redirect, render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(900))
    pub_date = db.Column(db.DateTime())

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date


#workers
def is_empty(val):
    if val == "":
        return True
    else:
        return False

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    blogs = Blog.query.all()

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        title_error = ''
        body_error = ''

        if is_empty(blog_title):
            title_error = 'Please enter a title for your blog entry'
        if is_empty(blog_body):
            body_error = 'Please enter some words for your blog entry'

        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()

            link = '/blog?id=' + str(new_blog.id)
            return redirect(link)
        
        else:
            return render_template('newpost.html',title='Build-A-Blog',
            blogs=blogs,title_error=title_error,body_error=body_error,
            blog_title=blog_title,blog_body=blog_body)
    else:
        return render_template('newpost.html',title='Build-A-Blog',blogs=blogs)

@app.route('/blog')
def entries():
    entry_id = request.args.get("id")

    if entry_id == None:
        blogs = Blog.query.order_by(Blog.pub_date.desc()).all()
        return render_template('blog.html',title='Build-A-Blog',blogs=blogs)
    else:
        blog = Blog.query.filter_by(id=entry_id).one()
        return render_template('entry.html',blog=blog, title=blog.title)

if __name__ == '__main__':
    app.run()