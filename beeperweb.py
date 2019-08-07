from bottle import TEMPLATE_PATH, jinja2_view, route, run, template, static_file

TEMPLATE_PATH[:] = ['templates']


@route('/')
@jinja2_view('index-vue.html')
def index():
    return {}

@route('/static/<path:path>')
def static_files(path):
    return static_file(path, 'static')

run(host='localhost', port=8080, debug=True)
