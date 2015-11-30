from wsgiref.simple_server import make_server
import os

port = os.environ.get("PORT", "5000")
def hello_world_app(environ, start_response):
    headers = [('Content-type', 'text/html')]
    start_response('200 OK', headers)
    return ["hello, world"]

httpd = make_server('', int(port), hello_world_app)
print "Serving HTTP on port " + port + "..."

httpd.serve_forever()