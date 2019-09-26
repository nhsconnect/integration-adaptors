import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line


class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write("Hello, world")


def build_application():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    parse_command_line()

    application = build_application()
    server = tornado.httpserver.HTTPServer(application)
    server.listen(80)
    tornado.ioloop.IOLoop.current().start()
