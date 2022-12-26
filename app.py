from flask import Flask, url_for, render_template, g, redirect
from db import get_db, close_db
from museum_of_art_api import *
from utils import *

app = Flask(__name__)
app.secret_key = 'dev'
museum_api = Museum_api()


@app.route('/')
def index():
    return redirect(url_for('gallery'))


@app.route('/gallery/')
@app.route('/gallery/<string:dep>/')
@app.route('/gallery/<string:dep>/<int:site>')
def gallery(dep='american-decorative-arts', site=0):
    g.max_page = 10
    conn = get_db()
    if conn:
        utils = Utils(conn)

        print('site',site)
        print('dep',dep)

        #Pobranie wszystkich departamentów
        departments = museum_api.get_departments()
        if departments.status_code == 200:
            # Zapisanie ich do db jeżeli nie istnieją
            utils.update_departments(departments.text)
        else:
            abort(departments.status_code)

        if 'items' not in g:
            # Pobranie listy indeksów dzieł w wybranym departamencie
            result = museum_api.get_objects(utils.get_departament_id(dep))
            if result.status_code == 200:
                items = utils.get_items(result)

            #Odfiltrowanie już zapisanych dzieł. Usuwane są indeksy które user dodał do ulubionych
            items = utils.filter_items(items, user_id)





        close_db()



    return 'Under construction - ' + url_for('gallery', site=site, dep=dep)


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