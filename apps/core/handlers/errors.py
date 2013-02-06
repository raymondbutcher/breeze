import tornado.web

from breeze.handlers import RequestHandler


class NotFoundHandler(RequestHandler):

    def get(self):
        raise tornado.web.HTTPError(404)
