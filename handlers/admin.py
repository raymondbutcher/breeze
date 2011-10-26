import tornado.web
from breeze.handlers.error import ErrorHandler

class AdminHandler(ErrorHandler):

    @tornado.web.addslash
    def get(self):
        self.render('templates/menu.html')
