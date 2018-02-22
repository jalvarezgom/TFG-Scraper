from app import app
from flask import render_template


@app.route('/')
@app.route('/index')
def index():
    print('Hello world!')
    return render_template('index.html')

@app.route('/user/<username>')
def user(username):
    return render_template('search.html', username=username)

