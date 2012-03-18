from handlers.auth import GoogleAuthHandler, LogoutAuthHandler, RegisterAuthHandler, SignInAuthHandler
from handlers.setup import SetupHandler


# Core URLs for all Breeze installations.
urls = (
    ('/auth/google/', GoogleAuthHandler),
    ('/logout/', LogoutAuthHandler),
    ('/register/', RegisterAuthHandler),
    ('/sign-in/', SignInAuthHandler),
)


# These will be used only in setup mode.
setup_urls = (
    (r'.*', SetupHandler),
)
