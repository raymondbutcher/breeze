import tornado.gen
import tornado.web

from breeze.handlers.mongo import MongoHandler


class AdminHandler(MongoHandler):

    @tornado.web.addslash
    #@tornado.web.asynchronous
    #@tornado.gen.engine
    def get(self):

        menu = self.get_argument('menu', False)
        if menu:
            return self.render_menu()

        tab = self.get_argument('tab', None)
        if tab:
            return self.render_tab(tab)

        if self.get_argument('blank', False):
            return self.render('templates/base.html')

        raise tornado.web.HTTPError(404)

    def render_menu(self):
        self.render('templates/menu.html')

    def render_tab(self, tab):
        self.write('TODO: %s' % tab)
        #self.finish()