from bottle import TEMPLATE_PATH, jinja2_view, route, run, template

TEMPLATE_PATH[:] = ['templates']


@route('/')
@jinja2_view('index.html')
def index():
    return {'title': 'Hello world'}


@route('/newpanel/<name>')
@jinja2_view('panel.html')
def newpanel(name):
    return {'name': 'hugo'}


@route('/newtimer/<panel>/<id>')
@jinja2_view('timer.html')
def newtimer(panel, id):
    return {}

run(host='localhost', port=8080, debug=True)
