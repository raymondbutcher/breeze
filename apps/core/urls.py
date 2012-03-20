from handlers.admin import AdminHandler
from handlers.auth import GoogleAuthHandler, LogoutAuthHandler, RegisterAuthHandler, SignInAuthHandler
from handlers.setup import SetupHandler


# Core URLs for all Breeze installations.
urls = (
    ('/admin/([a-zA-Z]+\.[a-zA-Z]+)?', AdminHandler),
    ('/auth/google/', GoogleAuthHandler),
    ('/logout/', LogoutAuthHandler),
    ('/register/', RegisterAuthHandler),
    ('/sign-in/', SignInAuthHandler),
)


# These will be used only in setup mode.
setup_urls = (
    (r'.*', SetupHandler),
)
