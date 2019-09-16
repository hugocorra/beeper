import json
import os

from flask import Flask, render_template, abort, redirect, url_for, session, request
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY")

#app.register_blueprint(google_auth.app)

#########################

@app.route("/login/callback")
def login_callback():
    if google_auth.is_logged_in():
        session['USER'] = google_auth.get_user_info()
        print('usuario está logado')

    return redirect('/')


@app.route("/login")
def login():
    return render_template('login2.html')


@app.route("/logout")
def logout():
    if google_auth.is_logged_in():
        redirect_dest = redirect('/google/logout')
        if 'USER' in session:
            del session['USER']

        return redirect_dest

    return redirect('/')


@app.route('/')
def index():
    user = session.get('user')
    print(user)
    return render_template('index-vue.html', user=user)


@app.route('/save', methods=['POST'])
def save():
    outfile = 'mydb.txt'

    if 'user' in session:
        outfile = 'mydb_{}.txt'.format(session['user']['email'])

    try:
        with open(outfile, 'w') as db:
            print('salvando...')
            json.dump(request.json, db)

    except Exception as e:
        return {'status': 'NOK', 'what': str(e)}

    return {'satatus': 'OK'}


@app.route('/load', methods=['GET'])
def load():
    infile = 'mydb.txt'

    if 'user' in session:
        print(session['user'])
        infile_user = 'mydb_{}.txt'.format(session['user']['email'])
        if os.path.isfile(infile_user):
            infile = infile_user

    try:
        with open(infile) as db:
            json_contents = json.load(db)
    except Exception as e:
        raise
        return {'status': 'NOK', 'what': str(e)}

    return {'status': 'OK', 'data': json_contents['data']}


@app.route('/authme')
def authme():
    return render_template('authme.html', user=session.get('user'))


@app.route('/google_auth_tokensignin', methods=['POST'])
def google_auth_tokensignin():
    try:
        token = request.form['idtoken']

        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), 
            '813782014106-ltdme6ehsgmt9pofimbdel2rv7sg6heg.apps.googleusercontent.com') #TODO: ler da variável de ambiente.

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        session['user'] = idinfo

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        return idinfo
    except ValueError:
        # Invalid token
        pass


@app.route('/google_signout')
def google_signout():
    session.pop('user')
    return 'OK'



@app.route('/static/<path:path>')
def static_files(path):
    return static_file(path, 'static')


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
