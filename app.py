from flask import Flask, url_for, render_template, g, redirect, request
from museum_of_art_api import Museum_api
from db import DB
from utils import Utils
from auth import Auth

app = Flask(__name__)
app.secret_key = 'dev'
db_file = 'museum.sqlite'
museum_api = Museum_api()

@app.route('/')
def index():
    return redirect(url_for('gallery'))


@app.route('/gallery/')
@app.route('/gallery/<string:dep>/')
@app.route('/gallery/<string:dep>/<int:site>')
def gallery(dep='american-decorative-arts', site=0):
    cookies = request.cookies
    g.max_page = 10
    db = DB(db_file)
    db.check_tables()
    utils = Utils(db.get_db())

    print('site',site)
    print('dep',dep)

    #Pobranie wszystkich departamentów
    departments = museum_api.get_departments()
    if departments.status_code == 200:
        # Zapisanie ich do db jeżeli nie istnieją
        utils.update_departments(departments.text)
    else:
        abort(departments.status_code)

    for item in g:
        print(item)


    if 'items' not in g:
        # Pobranie listy indeksów dzieł w wybranym departamencie
        result = museum_api.get_objects(utils.get_departament_id(dep))
        if result.status_code == 200:
            items = utils.get_items(result)
            g['items'] = items

        #Odfiltrowanie już zapisanych dzieł. Usuwane są indeksy które user dodał do ulubionych
        #user_id = 1
        #items = utils.filter_items(items, user_id, dep)



        '''
@app.route('/')
def index():
    cookies = request.cookies

    cookie_ses = request.cookies.get('moje_ciastko_na_sesje')
    cookie_30 = request.cookies.get('moje_ciastko_na_30_sekund')

    return render_template('index.html',
                           cookies=cookies,
                           cookie_ses=cookie_ses,
                           cookie_30=cookie_30)


@app.route('/add_cookie_for_session')
def add_cookie_for_session():
    cookies = request.cookies
    rendered_template = render_template('cookie_set.html', cookies=cookies)

    response = make_response(rendered_template)
    response.set_cookie(key='moje_ciastko_na_sesje',
                        value='moja_wartosc_na_sesję',
                        max_age=None)
    return response


@app.route('/add_cookie_for_30_secs')
def add_cookie_for_30_secs():
    cookies = request.cookies
    rendered_template = render_template('cookie_set.html', cookies=cookies)

    response = make_response(rendered_template)
    response.set_cookie(key='moje_ciastko_na_30_sekund',
                        value='moja_wartosc_na_30_sekund',
                        max_age=30)
    return response
        
        
        
        '''


    return 'Under construction - ' + url_for('gallery', site=site, dep=dep)


@app.route('/favorites')
def favorites():
    return 'Under construction - ' + url_for('favorites')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in g:
            return redirect(url_for('gallery'))
        return render_template('login.html')
    else:
        if 'sub_login' in request.form:
            db = DB(db_file)
            db.check_tables()
            auth = Auth(db.get_db())
            user_id = auth.get_user_id()
            if user_id:
                return redirect(url_for('index'))
            else:
                login = request.form.get('login', '')
                password = request.form.get('password', '')

                if auth.check_user(login, password):
                   return redirect(url_for('index'))
                else:
                    pass


        return redirect(url_for('index'))



@app.route('/logout')
def logout():
    return 'Under construction - ' + url_for('logout')

@app.route('/create_user')
def create_user():
    return render_template('create_user.html')








if __name__ == '__main__':
    app.run(debug=True)