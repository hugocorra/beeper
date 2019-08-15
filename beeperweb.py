import json
from bottle import TEMPLATE_PATH, jinja2_view, request, route, run, template, static_file

TEMPLATE_PATH[:] = ['templates']


@route('/login')
@jinja2_view('login.html')
def login():
    return {}


@route('/')
@jinja2_view('index-vue.html')
def index():
    return {}


@route('/save', method='POST')
def save():
    try:
        #from IPython import embed; embed()
        with open('mydb.txt', 'w') as db:
            print('salvando...')
            json.dump(request.json, db)
    except Exception as e:
        return {'status': 'NOK', 'what': str(e)}

    return {'satatus': 'OK'}


@route('/load', method='GET')
def load():
    try:
        with open('mydb.txt') as db:
            json_contents = json.load(db)
    except Exception as e:
        return {'status': 'NOK', 'what': str(e)}

    return {'status': 'OK', 'data': json_contents['data']}


@route('/static/<path:path>')
def static_files(path):
    return static_file(path, 'static')


run(host='localhost', port=8080, debug=True)
