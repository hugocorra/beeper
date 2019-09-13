import json
import os

from flask import Flask, render_template, abort, redirect, url_for, session, request
import google_auth


app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY")

app.register_blueprint(google_auth.app)

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
    if google_auth.is_logged_in():
        user = google_auth.get_user_info()
        session['USER'] = user
        print('user', session['USER'])
    else:
        print('client not logged in')
        user = None


    return render_template('index-vue.html', user=user)


@app.route('/save', methods=['POST'])
def save():
    outfile = 'mydb.txt'

    if 'USER' in session:
        outfile = 'mydb_{}.txt'.format(session['USER']['id'])

    try:
        if google_auth.is_logged_in():
            user = google_auth.get_user_info().get('username', None)
            print(google_auth.get_user_info())

            if user is not None:
                filename = 'mydb_{}.txt'.format()
                with open(filename, 'w') as db:
                    print('salvando...')
                    json.dump(request.json, db)

    except Exception as e:
        return {'status': 'NOK', 'what': str(e)}

    return {'satatus': 'OK'}


@app.route('/load', methods=['GET'])
def load():
    infile = 'mydb.txt'

    if 'USER' in session:
        infile_user = 'mydb_{}.txt'.format(session['USER']['id'])
        if os.path.isfile(infile_user):
            infile = infile_user

    try:
        filename = 'mydb.txt'

        if google_auth.is_logged_in():
            user = google_auth.get_user_info().get('username', None)
            print(google_auth.get_user_info())

            if user is not None:
                filename_user = 'mydb_{}.txt'.format()
                if os.path.isfile(filename_user):
                    filename = filename_user

        with open(filename) as db:
            json_contents = json.load(db)
    except Exception as e:
        return {'status': 'NOK', 'what': str(e)}

    return {'status': 'OK', 'data': json_contents['data']}


@app.route('/authme')
def authme():
    return render_template('authme.html')


@app.route('/tokensignin', methods=['POST'])
def tokensignin():
    from google.oauth2 import id_token
    from google.auth.transport import requests

    # (Receive token by HTTPS POST)
    # ...

    try:
        token = request.form['idtoken']
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), '813782014106-ltdme6ehsgmt9pofimbdel2rv7sg6heg.apps.googleusercontent.com')

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        from IPython import embed; embed()
        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
    except ValueError:
        # Invalid token
        pass

    return redirect('/')

@app.route('/static/<path:path>')
def static_files(path):
    return static_file(path, 'static')


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
