import re
from flask import Flask, url_for, render_template, g, redirect, request
from museum_api import Museum_api
from db import DB
from utils import Utils
from auth import Auth

app = Flask(__name__)
app.secret_key = 'dev'
db_file = 'museum.sqlite'
default_dep_uri = 'greek-and-roman-art'
default_page = 0

@app.route('/')
def index():
    return redirect(url_for('gallery', dep_uri=default_dep_uri, page=default_page))

@app.route('/gallery/')
@app.route('/gallery/<string:dep_uri>/')
@app.route('/gallery/<string:dep_uri>/<int:page>')
def gallery(dep_uri=default_dep_uri, page=default_page):
    g.max_for_page = 10

    # utworzenie instancji klasy DB
    db = DB(db_file)

    #Prawdzenie czy są utworzone wszystkie tabele
    db.check_tables()

    #utworzenie instancji klasy Utils
    utils = Utils(db.get_db(), Museum_api())

    # utworzenie instancji klasy Auth do sprawdzenia czy jest zalogowany user
    auth = Auth(db.get_db())
    user_id = auth.get_user_id() #tu jest błąd!!!!

    print('user_id', user_id)

    #Auktualizacja departamentów
    if utils.check_if_update_departments():
        utils.update_departments(utils.get_departments())

    #Aktualizacja wszystkich id produktów w wybranym departamencie
    department_id = utils.get_department_id_from_uri(dep_uri)
    if utils.check_if_update_arts(department_id):
        objects = utils.get_objects(department_id)
        utils.update_arts(objects, department_id)

    #Policzenie ile jest stron
    pages = utils.get_pages_count(department_id, g.max_for_page)

    #Pobranie id produktów dla wybranej strony i departamentu
    objects = utils.get_objects_for_selected(page, department_id, g.max_for_page)

    #Aktualizacja contentu (o ile potrzeba) dla produktów dla wybranej strony i departamentu
    for object in objects:
        if utils.check_if_update_art_content(object, department_id):
            utils.update_content(object, department_id)

    #Wyświetlenie contentu
    contents = utils.get_contents(objects)
    names = {name:utils.get_human_name(name) for name in utils.tables_which_need_names()}

    return render_template('gallery.html', auth=auth, utils=utils, contents=contents, names=names, user_id=user_id)


@app.route('/favorites')
def favorites():
    return 'Under construction - ' + url_for('favorites')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in g:
            return redirect(url_for('gallery'))
        return render_template('login.html', error='', login='')
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
                error = auth.check_credentials(login, password)
                if error:
                    return render_template('login.html', error=error, login=login)
                else:
                    return redirect(url_for('index'))
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    db = DB(db_file)
    db.check_tables()
    auth = Auth(db.get_db())
    auth.logout()
    return redirect(url_for('index'))

@app.route('/create_user', methods=["GET", "POST"])
def create_user():
    if request.method == 'GET':
        return render_template('create_user.html', error='', login='', name='')
    else:
        if 'sub_create' in request.form:
            db = DB(db_file)
            db.check_tables()
            auth = Auth(db.get_db())
            login = request.form.get('login', '').lower()
            your_name = re.sub(r' +', ' ', request.form.get('your_name', '').strip())
            password = request.form.get('password', '')
            password2 = request.form.get('password2', '')
            error = auth.check_login(login)
            if error:
                return render_template('create_user.html', error=error, login=login, name=your_name)
            error = auth.check_login_isset(login)
            if error:
                return render_template('create_user.html', error=error, login=login, name=your_name)
            error = auth.check_your_name(your_name)
            if error:
                return render_template('create_user.html', error=error, login=login, name=your_name)
            error = auth.check_passwords(password, password2)
            if error:
                return render_template('create_user.html', error=error, login=login, name=your_name)
            auth.insert_user(login, your_name, password)
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)