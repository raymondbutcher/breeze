import tornado.gen
import tornado.web

from breeze.handlers.base import MongoBaseHandler


class SetupHandler(MongoBaseHandler):

    def get(self):
        context = {
            'superuser': self.get_argument('superuser', None),
        }
        self.render('templates/setup.html', **context)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):

        superuser_email = self.get_argument('superuser_email', None)
        if superuser_email:
            data = {'superuser': True}
            superuser_name = self.get_argument('superuser_name', None)
            if superuser_name:
                data['superuser_name'] = superuser_name
            result = yield tornado.gen.Task(
                self.db.users.update,
                spec={'email': superuser_email},
                document={'$set': data},
                upsert=True
            )
            result = self.get_mongo_result(result)
            if result:
                if result[0]['updatedExisting']:
                    self.redirect('/?superuser=updated')
                else:
                    self.redirect('/?superuser=created')
            return

        self.redirect('/')
