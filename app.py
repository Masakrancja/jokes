import re
from flask import Flask, url_for, render_template, redirect, request, session
from classes.museum_api import Museum_api
from classes.db import DB
from classes.auth import Auth
from classes.dep import Departments
from classes.arts import Arts
from classes.cont import Cont
from classes.fav import Fav
from classes.pages import Pages
from classes.process import Process


app = Flask(__name__)
app.secret_key = 'dev'
db_file = 'db/museum.sqlite'
default_dep_uri = 'the-robert-lehman-collection'
default_page = 0
max_for_page = 10
max_pages_in_pagination = 20

@app.route('/')
@app.route('/gallery/')
@app.route('/gallery/<string:dep_uri>/')
@app.route('/gallery/<string:dep_uri>/<int:page>')
def index(dep_uri=default_dep_uri, page=default_page):
    parameters = {}
    session['dep_uri'] = dep_uri
    session['page'] = page
    parameters['dep_uri'] = dep_uri
    parameters['page'] = page

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

    #utworzenie instancji klasy Departments która zawiera metody działające na departamentach
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

    if department_id:
        department_name = dep.get_department_name_from_id(department_id)
        parameters['department_name'] = department_name

        #utworzenie instancji klasy Arts zawierającej metody obsługujące indeksy produktów
        arts = Arts(db.get_db(), Museum_api())

        # Aktualizacja wszystkich id produktów w wybranym departamencie
        if arts.check_if_update_arts_is_needed(department_id):
            arts.update_arts(arts.get_arts(department_id), department_id)

        # Pobranie id produktów dla wybranej strony i departamentu
        arts_id = arts.get_arts_for_selected_page(page, department_id, max_for_page)

        #utworzenie instancji klasy Arts zawierającej metody obsługujące indeksy produktów
        cont = Cont(db.get_db(), Museum_api())
        parameters['cont'] = cont

        #Aktualizacja contentu do bazy (o ile potrzeba) dla produktów dla wybranej strony i departamentu
        for art_id in arts_id:
            if cont.check_if_update_art_content_is_needed(art_id, department_id):
                cont.update_content(art_id, department_id)

        #Przygotowanie contentu do wyświetlenia
        contents = cont.get_contents(arts_id)

        #utworzenie słownika nazw parametrów
        names = {name: cont.get_human_name(name) for name in cont.get_cols_to_need_names()}
        parameters['names'] = names

        #Dodatnie contentu zalogowanego użytkownika
        contents = cont.get_contents_from_user(contents, user_id)
        parameters['contents'] = contents

        #Policzenie ile jest stron
        pages = Pages(db.get_db())
        all_pages = pages.get_pages_count(department_id, max_for_page)

        #Przygotowanie danych do paginacji
        pagination = pages.get_pagination(dep_uri, page, all_pages, max_pages_in_pagination)
        parameters['pagination'] = pagination
        return render_template('index.html', **parameters)

    parameters['contents'] = ''
    parameters['names'] = ''
    return render_template('index.html', **parameters)


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


@app.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        db = DB(db_file)
        auth = Auth(db.get_db())
        user_id = auth.get_user_id()
        if user_id:
            fav = Fav(db.get_db())
            dep_uri = session.get('dep_uri', '')
            page = session.get('page', 0)
            hash = request.form.get('hash', '')
            art_id = request.form.get('art_id', '')
            action = request.form.get('action', '')
            if (action == 'add'):
                fav.add_to_favorites(user_id, art_id, hash)
            elif (action == 'remove'):
                fav.remove_from_favorites(hash)
    return redirect(url_for('index', dep_uri=dep_uri, page=page))


@app.route('/process_get_info', methods=['POST'])
def process_get_info():
    if request.method == 'POST':
        db = DB(db_file)
        process = Process(db.get_db())
        hash = request.form.get('hash', '')
        return process.get_value(hash, 'info')
    return ''

@app.route('/process_set_info', methods=['POST'])
def process_set_info():
    if request.method == 'POST':
        db = DB(db_file)
        process = Process(db.get_db())
        text = request.form.get('text', '')
        hash = request.form.get('hash', '')
        return process.set_value(text, hash, 'info')
    return ''


@app.route('/process_get_note', methods=['POST'])
def process_get_note():
    if request.method == 'POST':
        db = DB(db_file)
        process = Process(db.get_db())
        hash = request.form.get('hash', '')
        return process.get_value(hash, 'note')
    return ''


@app.route('/process_set_note', methods=['POST'])
def process_set_note():
    if request.method == 'POST':
        db = DB(db_file)
        process = Process(db.get_db())
        note = request.form.get('note', '')
        hash = request.form.get('hash', '')
        return process.set_value(note, hash, 'note')
    return ''


if __name__ == '__main__':
    app.run(debug=True)