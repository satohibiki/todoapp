from datetime import datetime, date

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required

from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todoapp.db"
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

login_manager=LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(15))
    due = db.Column(db.DateTime, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(15))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=("GET", "POST"))
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/index')
        else:
            return redirect('/')
    else:
        return render_template("login.html")

@app.route('/index', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.due).all()
        return render_template("index.html", posts=posts, today=date.today())

@app.route('/signup', methods=("GET", "POST"))
def signup():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = User(username=username, password=generate_password_hash(password, method='sha256'))

        db.session.add(user)
        db.session.commit()
        return redirect('/')
    else:
        return render_template("signup.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/create', methods=("GET", "POST"))
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get("title")
        detail = request.form.get("detail")
        due = request.form.get("due")

        due = datetime.strptime(due, "%Y-%m-%dT%H:%M")
        new_post = Post(title=title, detail=detail, due=due)

        db.session.add(new_post)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template("create.html")

@app.route('/detail/<int:id>')
@login_required
def read(id):
    post = Post.query.get(id)
    return render_template("detail.html", post = post)

@app.route('/update/<int:id>', methods=("GET", "POST"))
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == "GET":
        return render_template("update.html", post=post)
    else:
        post.title = request.form.get("title")
        post.detail = request.form.get("detail")
        post.due = datetime.strptime(request.form.get("due"), "%Y-%m-%dT%H:%M")

        db.session.commit()
        return redirect("/index")

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect("/index")

if __name__ == '__main__' :
    app.run(debug=True)
