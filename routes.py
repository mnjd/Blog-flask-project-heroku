from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from urllib.parse import urlparse, urljoin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import psycopg2
import os

app = Flask(__name__) # create the application instance

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SECRET_KEY'] = '4qNdpAmAhhD$PdKayyNevkh6@&X!@Z&#E%fE2hu5'
app.config['USE_SESSION_FOR_NEXT'] = True

db = SQLAlchemy(app)
ma = Marshmallow(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Postblog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime)


class Weatherdb(db.Model):
    dateandtime = db.Column(db.DateTime, primary_key=True)
    city = db.Column(db.String(50))
    temperature = db.Column(db.Integer)
    humidity =  db.Column(db.Integer)
    pressure = db.Column(db.Integer)
    temperature_ressentie = db.Column(db.Integer)
    description = db.Column(db.String(50))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min  =3, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=6, max=80)])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class PostListAPIView(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'subtitle', 'author', 'text', 'created_at')

@app.route('/api/v1.0/posts/', methods=['GET'])
def get_posts():
    postlist = PostListAPIView(many=True)
    queryset = Postblog.query.all()
    posts = postlist.dump(queryset)
    return jsonify(posts.data)

@app.route("/")
def list_articles():
    posts = Postblog.query.all()
    return render_template('listarticles.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('list_articles'))

        return render_template('login.html', form=form)

    session['next'] = request.args.get('next')
    return render_template('login.html', form=form)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('list_articles'))

@app.route("/register/", methods = ['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('list_articles'))

    return render_template('register.html', form=form)

@app.route("/detailarticles/<int:pk>")
@login_required
def detail_articles(pk):
    post = Postblog.query.filter_by(id=pk).one()
    return render_template('detailarticles.html', post=post)

@app.route("/createarticle/")
@login_required
def create_articles():
    return render_template('createarticle.html')

@app.route("/createpost/", methods=['POST'])
@login_required
def create_post():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    text = request.form['text']
    created_at = datetime.now().strftime('%B %d, %Y at %H:%M:%S')

    post = Postblog(title=title, subtitle=subtitle, author=author, text=text, created_at=created_at)

    db.session.add(post)
    db.session.commit()
    return redirect(url_for('list_articles'))

@app.route("/editpost/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = db.session.query(Postblog).filter(Postblog.id==id).first()

    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        author = request.form['author']
        text = request.form['text']

        post.title = title
        post.subtitle = subtitle
        post.author = author
        post.text = text

        db.session.commit()

        return redirect(url_for('list_articles'))
    elif request.method == 'GET':
        return render_template('editarticle.html', post=post)

@app.route("/deletepost/<int:id>", methods=['POST'])
@login_required
def delete_post(id):
    post = db.session.query(Postblog).filter(Postblog.id==id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('list_articles'))

if __name__ == "__main__":
    app.run()
