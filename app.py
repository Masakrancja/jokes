import re
from flask import Flask, url_for, render_template, g, redirect, request, session
from museum_api import Museum_api
from db import DB
from utils import Utils
from auth import Auth

app = Flask(__name__)
app.secret_key = 'dev'
db_file = 'museum.sqlite'
default_dep_uri = 'the-robert-lehman-collection'
#default_dep_uri = ''
default_page = 0

@app.route('/')
def index():
    return redirect(url_for('gallery', dep_uri=default_dep_uri, page=default_page))

@app.route('/gallery/')
@app.route('/gallery/<string:dep_uri>/')
@app.route('/gallery/<string:dep_uri>/<int:page>')
def gallery(dep_uri=default_dep_uri, page=default_page):
    max_for_page = 10
    max_pages = 20

    parameters = {}

    # utworzenie instancji klasy DB
    db = DB(db_file)

    #Prawdzenie czy są utworzone wszystkie tabele
    db.check_tables()

    #utworzenie instancji klasy Utils
    utils = Utils(db.get_db(), Museum_api())
    parameters['utils'] = utils

    # utworzenie instancji klasy Auth do sprawdzenia czy jest zalogowany user
    auth = Auth(db.get_db())
    parameters['auth'] = auth
    user_id = auth.get_user_id()
    parameters['user_id'] = user_id

    #Auktualizacja departamentów
    if utils.check_if_update_departments():
        utils.update_departments(utils.get_departments())

    #pobranie dostępnych departamentów dla menu wyboru
    departments = utils.get_departments_from_db()
    parameters['departments'] = departments

    #Aktualizacja wszystkich id produktów w wybranym departamencie
    department_id = utils.get_department_id_from_uri(dep_uri)

    if department_id:
        department_name = utils.get_department_name_from_id(department_id)
        parameters['department_name'] = department_name

        if utils.check_if_update_arts(department_id):
            objects = utils.get_objects(department_id)
            utils.update_arts(objects, department_id)



        #Policzenie ile jest stron
        pages = utils.get_pages_count(department_id, max_for_page)

        #Przygotowanie danych do paginacji
        pagination = utils.get_pagination(dep_uri, page, pages, max_pages)
        parameters['pagination'] = pagination

        # Pobranie id produktów dla wybranej strony i departamentu
        objects = utils.get_objects_for_selected(page, department_id, max_for_page)

        # Aktualizacja contentu (o ile potrzeba) dla produktów dla wybranej strony i departamentu
        for object in objects:
            if utils.check_if_update_art_content(object, department_id):
                utils.update_content(object, department_id)

        # Wyświetlenie contentu
        contents = utils.get_contents(objects)
        parameters['contents'] = contents
        names = {name: utils.get_human_name(name) for name in utils.tables_which_need_names()}
        parameters['names'] = names

        print(parameters)

        return render_template('gallery.html', **parameters)
    parameters['contents'] = ''
    parameters['names'] = ''
    return render_template('gallery.html', **parameters)

@app.route('/favorites')
def favorites():
    return 'Under construction - ' + url_for('favorites')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' in g: #błąd !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
    return redirect(url_for('login'))

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


@app.route('/save-art-for-user', methods=['POST'])
def save_art_for_user():
    db = DB(db_file)
    db.check_tables()
    auth = Auth(db.get_db())
    user_id = auth.get_user_id()

    print('user_id')

    if user_id:
        pass
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)