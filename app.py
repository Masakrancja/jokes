import re
from flask import Flask, url_for, render_template, g, redirect, request
from classes.museum_api import Museum_api
from classes.db import DB
from classes.auth import Auth
from classes.dep import Departments
from classes.arts import Arts
from classes.cont import Cont


app = Flask(__name__)
app.secret_key = 'dev'
db_file = 'db/museum.sqlite'
default_dep_uri = 'the-robert-lehman-collection'
default_page = 0
max_for_page = 10
max_pages = 20

@app.route('/')
@app.route('/gallery/')
@app.route('/gallery/<string:dep_uri>/')
@app.route('/gallery/<string:dep_uri>/<int:page>')
def index(dep_uri=default_dep_uri, page=default_page):
    parameters = {}

    # utworzenie instancji klasy DB
    db = DB(db_file)

    #Sprawdzenie czy są utworzone wszystkie tabele
    db.check_tables()

    # utworzenie instancji klasy Auth zawierającej metody związane z logowaniem i autoryzacją
    auth = Auth(db.get_db())
    parameters['auth'] = auth

    #Pobranie id zalogowanego uzytkownika jeśli jest
    user_id = auth.get_user_id()
    parameters['user_id'] = user_id

    #utworzenie instancji klasy Departments któwa zawiera metody działające na departamentach
    dep = Departments(db.get_db(), Museum_api())
    parameters['dep'] = dep

    #Auktualizacja departamentów do bazy jeśli to konieczne
    if dep.check_if_update_departments():
        dep.update_departments(dep.get_departments())

    #pobranie dostępnych departamentów dla menu wyboru
    departments = dep.get_departments_from_db()
    parameters['departments'] = departments

    #Pobranie id departamentu z db na postawie jego nazwy uri
    department_id = dep.get_department_id_from_uri(dep_uri)


    for key, val in parameters.items():
        print(key, ':', val)

    if department_id:
        department_name = dep.get_department_name_from_id(department_id)
        parameters['department_name'] = department_name

        #utworzenie instancji klasy Arts zawierającej metody obsługujące indeksy produktów
        arts = Arts(db.get_db(), Museum_api())

        # Aktualizacja wszystkich id produktów w wybranym departamencie
        if arts.check_if_update_arts(department_id):
            arts.update_arts(arts.get_arts(department_id), department_id)

        # Pobranie id produktów dla wybranej strony i departamentu
        arts_id = arts.get_arts_for_selected(page, department_id, max_for_page)


        #utworzenie instancji klasy Arts zawierającej metody obsługujące indeksy produktów
        cont = Cont(db.get_db(), Museum_api())

        print(cont.get_cols_names_from_table('users'))

        # Aktualizacja contentu do bazy (o ile potrzeba) dla produktów dla wybranej strony i departamentu
        #for art_id in arts_id:
        #    if cont.check_if_update_art_content(art_id, department_id):
        #        cont.update_content(art_id, department_id)





        '''
        #Policzenie ile jest stron
        pages = utils.get_pages_count(department_id, max_for_page)

        #Przygotowanie danych do paginacji
        pagination = utils.get_pagination(dep_uri, page, pages, max_pages)
        parameters['pagination'] = pagination





        # Utworzenie głównego contentu
        contents = utils.get_contents(objects)
        contents_user = utils.get_contents_from_user(objects, user_id)
        parameters['contents'] = contents
        parameters['contents_user'] = contents_user

        #utworzenie słownika nazw parametrów
        names = {name: utils.get_human_name(name) for name in utils.tables_which_need_names()}
        parameters['names'] = names



        for key, val in parameters.items():
            print(key,':',val)

        return render_template('gallery.html', **parameters)
        '''

    parameters['contents'] = ''
    parameters['names'] = ''

    return render_template('gallery.html', **parameters)

@app.route('/favorites')
def favorites():
    return 'Under construction - ' + url_for('favorites')


@app.route('/login', methods=['GET', 'POST'])
def login():
    db = DB(db_file)
    db.check_tables()
    auth = Auth(db.get_db())
    user_id = auth.get_user_id()
    if request.method == 'GET':
        user_id = auth.get_user_id()
        if user_id:
            return redirect(url_for('index'))
        return render_template('login.html', error='', login='')
    else:
        if 'sub_login' in request.form:
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

    print(user_id)

    if user_id:
        return str(user_id)
    else:
        return ''


if __name__ == '__main__':
    app.run(debug=True)