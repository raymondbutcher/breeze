import tornado.auth
import tornado.escape
import tornado.gen
import tornado.web

from tornado.options import options

from breeze.handlers.error import ErrorHandler
from breeze.handlers.mongo import MongoHandler


class AuthHandler(ErrorHandler):

    def clear_auth_cookies(self):
        """Clear all auth cookies, logging the user out."""
        self.clear_cookie('auth')
        self.clear_cookie('auth_staff')
        self.clear_cookie('auth_superuser')

    def get_current_user(self):
        """
        Return the user's email address if they are logged in. This is not
        returning an actual user object because that needs to be done
        asynchronously.
        """
        return self.get_secure_cookie('auth')

    def set_auth_cookies(self, user):
        """Set all necessary auth cookies for the given user."""

        self.set_secure_cookie('auth', user['email'])

        if user.get('staff'):
            self.set_secure_cookie('auth_staff', '1')
        else:
            self.clear_cookie('auth_staff')

        if user.get('superuser'):
            self.set_secure_cookie('auth_superuser', '1')
        else:
            self.clear_cookie('auth_superuser')


class AuthLogoutHandler(AuthHandler):
    def get(self):
        """Log the user out and redirect to the 'next' page or homepage."""
        self.clear_auth_cookies()
        self.redirect(self.get_argument('next', '/'))


class AuthGoogleHandler(AuthHandler, MongoHandler, tornado.auth.GoogleMixin):

    @tornado.web.addslash
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
                    upsert=True
                )

                # Get the user data, so we can see if they are an admin user.
                result = yield tornado.gen.Task(self.db.users.find_one, {'email': data['email']})
                user = self.get_mongo_result(result, allow_none=True)

                # Set cookies and redirect.
                self.set_auth_cookies(user)
                self.redirect(self.get_argument('next', '/'))
                return

        self.authenticate_redirect()
