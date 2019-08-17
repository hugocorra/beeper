import json

from flask import Flask, render_template, abort

app = Flask(__name__, static_url_path='/static')


#TEMPLATE_PATH[:] = ['templates']


# @app.route('/login')
# #@jinja2_view('login.html')
# def login():
#     return {}

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
