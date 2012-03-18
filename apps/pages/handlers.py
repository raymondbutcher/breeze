import tornado.gen
import tornado.web

from breeze.handlers import MongoRequestHandler


class PageHandler(MongoRequestHandler):

    @tornado.web.addslash
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, path=''):
        result = yield tornado.gen.Task(self.db.pages.find_one, {
            'path': '/%s' % path
        })
        context = {
            'page': self.get_mongo_result(result),
        }
        self.render('pages/page.html', **context)
