from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import psycopg2
import os

app = Flask(__name__) # create the application instance

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)
ma = Marshmallow(app)


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


class PostListAPIView(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'subtitle', 'author', 'text', 'created_at')

postlist = PostListAPIView()
postlist = PostListAPIView(many=True)

@app.route('/api/v1.0/posts/', methods=['GET'])
def get_posts():
    queryset = Postblog.query.all()
    posts = postlist.dump(queryset)
    return jsonify(posts.data)

@app.route("/")
def list_articles():
    posts = Postblog.query.all()
    weather = Weatherdb.query.order_by(Weatherdb.dateandtime.desc()).first()
    return render_template('listarticles.html', posts=posts, weather=weather)

@app.route("/detailarticles/<int:pk>")
def detail_articles(pk):
    post = Postblog.query.filter_by(id=pk).one()
    return render_template('detailarticles.html', post=post)

@app.route("/createarticle/")
def create_articles():
    return render_template('createarticle.html')

@app.route("/createpost/", methods=['POST'])
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
def delete_post(id):
    post = db.session.query(Postblog).filter(Postblog.id==id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('list_articles'))

if __name__ == "__main__":
    app.run()
