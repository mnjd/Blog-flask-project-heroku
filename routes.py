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
    return render_template('listarticles.html', posts=posts)

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

if __name__ == "__main__":
    app.run()
