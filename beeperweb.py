import json
import os

from flask import Flask, render_template, abort, redirect, url_for, session, request
import google_auth


app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY")

app.register_blueprint(google_auth.app)

#########################

# @app.route("/login/callback")
# def login_callback():
#     if google_auth.is_logged_in():
#         session['USER'] = google_auth.get_user_info()

#     return redirect('/')


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
        with open(outfile, 'w') as db:
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
        with open(infile) as db:
            json_contents = json.load(db)
    except Exception as e:
        return {'status': 'NOK', 'what': str(e)}

    return {'status': 'OK', 'data': json_contents['data']}


@app.route('/static/<path:path>')
def static_files(path):
    return static_file(path, 'static')


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
