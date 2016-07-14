import ssl
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application
from connectorProcess import app
import tornado.httpserver


class MainHandler(RequestHandler):
    def get(self):
        pass


tr = WSGIContainer(app)

application = Application([
    (r"/tornado", MainHandler),
    (r".*", FallbackHandler, dict(fallback=tr)),
])

if __name__ == "__main__":
    application.listen(port=80)

    http_server = tornado.httpserver.HTTPServer(application, ssl_options={
        "certfile": "astute_social_cert/ssl-bundle.crt",
        "keyfile": "astute_social_cert/server.key",
    })
    http_server.listen(443)

    print("Running Conversation Connector Server")
    IOLoop.instance().start()
