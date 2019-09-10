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
    return redirect('/')


@app.route("/login")
def login():
    return render_template('login2.html')


@app.route('/')
def index():
    return render_template('index-vue.html')


@app.route('/save', methods=['POST'])
def save():
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


@app.route('/static/<path:path>')
def static_files(path):
    return static_file(path, 'static')


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
