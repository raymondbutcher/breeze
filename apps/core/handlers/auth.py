import breeze.decorators

import tornado.auth
import tornado.escape
import tornado.gen
import tornado.web

from breeze.handlers import RequestHandler, MongoRequestHandler


class RegisterAuthHandler(RequestHandler):

    @breeze.decorators.unauthenticated
    def get(self):
        context = {
            'after': self.get_argument('after', '/'),
            'js': False,
        }
        self.render('core/auth/register.html', **context)


class SignInAuthHandler(RequestHandler):

    @breeze.decorators.unauthenticated
    def get(self):
        context = {
            'after': self.get_argument('after', '/'),
            'js': False,
        }
        self.render('core/auth/sign-in.html', **context)


class LogoutAuthHandler(RequestHandler):

    def get(self):
        """Log the user out and redirect to the 'after' page or homepage."""
        self.clear_auth_cookies()
        self.redirect(self.get_argument('after', '/'))


class GoogleAuthHandler(MongoRequestHandler, tornado.auth.GoogleMixin):

    @tornado.web.addslash
    @breeze.decorators.unauthenticated
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):

        if self.get_argument('openid.mode', None):
            data = yield tornado.gen.Task(self.get_authenticated_user)
            if data:

                # User data has been returned from Google.
                # Create or update a matching User object in Mongo.
                yield tornado.gen.Task(
                    self.db.users.update,
                    spec={'email': data['email']},
                    document={'$set': data},
                    upsert=True,
                )

                # Get the user data, so we can see if they are an admin user.
                result = yield tornado.gen.Task(self.db.users.find_one, {'email': data['email']})
                user = self.get_mongo_result(result, allow_none=True)

                # Set cookies and redirect.
                self.set_auth_cookies(user)
                self.redirect(self.get_argument('after', '/'))
                return

        self.authenticate_redirect()
