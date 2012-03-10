import tornado.gen
import tornado.web

from breeze.handlers.mongo import MongoHandler


class PageHandler(MongoHandler):

    css_column_classes = {
        1: 'onecol',
        2: 'twocol',
        3: 'threecol',
        4: 'fourcol',
        5: 'fivecol',
        6: 'sixcol',
        7: 'sevencol',
        8: 'eightcol',
        9: 'ninecol',
        10: 'tencol',
        11: 'elevencol',
        12: 'twelvecol',
    }

    def get_css_class(self, colspan):
        return self.css_column_classes[colspan]

    @tornado.web.addslash
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, path=''):
        path = '/%s' % path
        result = yield tornado.gen.Task(self.db.pages.find_one, {'path': path})
        context = {
            'page': self.get_mongo_result(result),
            'get_css_class': self.get_css_class,
        }
        self.render('templates/page.html', **context)
