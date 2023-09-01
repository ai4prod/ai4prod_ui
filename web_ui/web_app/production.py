import http
from gevent import monkey
monkey.patch_all()
import os 

from gevent.pywsgi import WSGIServer
from run_app import application


if __name__ == "__main__":
    http_server= WSGIServer(('0.0.0.0',4040),application)
    print(http_server)
    http_server.serve_forever()