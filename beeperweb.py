import json
import os

from flask import Flask, render_template, abort, redirect, url_for, session
# from flask_oauth import OAuth
# from google_auth import login as glogin
# from google_auth import logout as glogout

import google_auth


app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY")

app.register_blueprint(google_auth.app)

# REDIRECT_URI = '/authorized'
# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
# GOOGLE_DISCOVERY_URL = (
#     "https://accounts.google.com/.well-known/openid-configuration"
# )



#TEMPLATE_PATH[:] = ['templates']


# @app.route('/login')
# #@jinja2_view('login.html')
# def login():
#     return {}




########################


# app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# # User session management setup
# # https://flask-login.readthedocs.io/en/latest
# login_manager = LoginManager()
# login_manager.init_app(app)

# # Naive database setup
# try:
#     init_db_command()
# except sqlite3.OperationalError:
#     # Assume it's already been created
#     pass

# # OAuth 2 client setup
# client = WebApplicationClient(GOOGLE_CLIENT_ID)

# # Flask-Login helper to retrieve a user from our db
# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)


#########################

@app.route("/login/callback")
def login_callback():
    return redirect('/')


@app.route("/login")
def login():
    return render_template('login2.html')
    # # Find out what URL to hit for Google login
    # google_provider_cfg = get_google_provider_cfg()
    # authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # # Use library to construct the request for Google login and provide
    # # scopes that let you retrieve user's profile from Google
    # request_uri = client.prepare_request_uri(
    #     authorization_endpoint,
    #     redirect_uri=request.base_url + "/callback",
    #     scope=["openid", "email", "profile"],
    # )
    # return redirect(request_uri)



@app.route('/')
#@jinja2_view('index-vue.html')
def index():
    return render_template('index-vue.html')


@app.route('/save', methods=['POST'])
def save():
    try:
        #from IPython import embed; embed()
        with open('mydb.txt', 'w') as db:
            print('salvando...')
            json.dump(request.json, db)
    except Exception as e:
        return {'status': 'NOK', 'what': str(e)}

    return {'satatus': 'OK'}


@app.route('/load', methods=['GET'])
def load():
    try:
        with open('mydb.txt') as db:
            json_contents = json.load(db)
    except Exception as e:
        return {'status': 'NOK', 'what': str(e)}

    return {'status': 'OK', 'data': json_contents['data']}


@app.route('/static/<path:path>')
def static_files(path):
    return static_file(path, 'static')


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
#run(host='localhost', port=8080, debug=True)
