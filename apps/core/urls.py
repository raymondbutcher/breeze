from handlers.admin import AdminHandler
from handlers.auth import GoogleAuthHandler, LogoutAuthHandler, RegisterAuthHandler, SignInAuthHandler
from handlers.forms import FormValidationHandler


# Core URLs for all Breeze installations.
urls = (

    ('/admin/([a-zA-Z]+\.[a-zA-Z]+)?', AdminHandler),

    ('/form-validation/([a-zA-Z]+\.[a-zA-Z]+)', FormValidationHandler),

    ('/auth/google/', GoogleAuthHandler),
    ('/logout/', LogoutAuthHandler),
    ('/register/', RegisterAuthHandler),
    ('/sign-in/', SignInAuthHandler),

)


# These will be used only in setup mode, in addition to normal URLs.
# It just makes the Admin require no authentication.
setup_urls = (
    ('/admin/([a-zA-Z]+\.[a-zA-Z]+)?', AdminHandler, {'require_authentication': False}),
)
