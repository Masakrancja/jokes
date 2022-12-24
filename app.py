from flask import Flask, url_for, render_template, g
from db import get_db
from humorapi import *

app = Flask(__name__)
app.secret_key = 'dev'
token = '182caef7b40a4bf397b4c6901518250e'

api = Humor_api(token)

@app.route('/')
def index():
    print(g)
    get_db()

    for method in g:
        print(method)


    return render_template('base.html')


@app.route('/jokes/')
@app.route('/jokes/<int:site>')
def jokes(site=0):
    return 'Under construction - ' + url_for('jokes', site=site)


@app.route('/favorites')
def favorites():
    return 'Under construction - ' + url_for('favorites')


@app.route('/login')
def login():
    return 'Under construction - ' + url_for('login')


@app.route('/logout')
def logout():
    return 'Under construction - ' + url_for('logout')

@app.route('/create_user')
def create_user():
    return render_template('create_user.html')








if __name__ == '__main__':
    app.run(debug=True)