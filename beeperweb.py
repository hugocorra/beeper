from bottle import TEMPLATE_PATH, jinja2_view, route, run, template

TEMPLATE_PATH[:] = ['templates']

@route('/')
@jinja2_view('index.html')
def index():
    return {'title': 'Hello world'}

run(host='localhost', port=8080, debug=True)