import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

STORAGE_PATH = pathlib.Path().joinpath('storage')
STORAGE_PATH.mkdir(exist_ok=True)
DATA_FILE = STORAGE_PATH.joinpath('data.json')

env = Environment(loader=FileSystemLoader('templates'))

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        try:
            with open(DATA_FILE, 'r') as fd:
                data = json.load(fd)
        except FileNotFoundError:
            data = {}
        
        data[timestamp] = data_dict
        
        with open(DATA_FILE, 'w') as fd:
            json.dump(data, fd, indent=2)
        
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            self.read_data()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(f'templates/{filename}', 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())
            
    def read_data(self):
        try:
            with open(DATA_FILE, 'r') as fd:
                data = json.load(fd)
        except FileNotFoundError:
            data = {}
        
        template = env.get_template('messages.html')
        html = template.render(messages=data)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        print("Server started! On http://localhost:3000")
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

if __name__ == '__main__':
    run()
