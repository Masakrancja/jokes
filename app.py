from flask import Flask, url_for, render_template, g
from db import get_db, close_db
from museum_of_art_api import *
from utils import *

app = Flask(__name__)
app.secret_key = 'dev'
museum_api = Museum_api()


@app.route('/')
def index():
    g.max_page = 10
    print(g)
    conn = get_db()
    if conn:
        utils = Utils(conn)

        #Pobranie wszystkich departamentów
        departments = museum_api.get_departments()
        if departments.status_code == 200:
            # Zapisanie ich do db jeżeli nie istnieją
            utils.update_departments(departments.text)
        else:
            abort(departments.status_code)











        close_db()
    else:
        abort(404)


    for method in g:
        print(method)


    return render_template('base.html')


@app.route('/gallery/')
@app.route('/gallery/<string:dep>/')
@app.route('/gallery/<int:dep>/<int:site>')
def jokes(dep='american-decorative-arts', site=0):
    return 'Under construction - ' + url_for('jokes', site=site, dep=dep)


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