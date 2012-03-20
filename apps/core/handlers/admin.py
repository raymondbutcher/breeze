import tornado.gen
import tornado.web

from breeze.handlers import MongoRequestHandler


class AdminHandler(MongoRequestHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, key=None):

        if key:
            form = self.application.breeze.forms.get(key)
            if form:
                admin = self.application.breeze.admins.with_form(form)
                print admin
            else:
                admin = self.application.breeze.admins.get(key)
            if not admin and not form:
                raise tornado.web.HTTPError(404, 'Admin "%s" not found.' % key)
        else:
            admin = None
            form = None

        context = {
            'key': key,
            'current_admin': admin,
            'current_form': form,
            'admin_registry': self.application.breeze.admins,
            'form_registry': self.application.breeze.forms,
        }

        self.render('core/admin/admin.html', **context)
