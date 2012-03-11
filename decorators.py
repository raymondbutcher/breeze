def unauthenticated(handler_method):
    """
    A RequestHandler method decorator that redirects to the 'after' page,
    which defaults to the homepage, if the user is authenticated.

    """

    def decorated(self, *args, **kwargs):
        if self.get_current_user():
            self.redirect(self.get_argument('after', '/'))
        else:
            return handler_method(self, *args, **kwargs)

    return decorated
