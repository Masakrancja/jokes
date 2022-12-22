from flask import Flask, url_for, render_template, g


app = Flask(__name__)
app.secret_key = 'dev'

@app.route('/')
def index():
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








if __name__ == '__main__':
    app.run(debug=True)