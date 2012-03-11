from breeze.handlers import helpers


class BaseHandler(helpers.AuthHandler, helpers.ErrorHandler):
    pass


class MongoBaseHandler(BaseHandler, helpers.MongoHandler):
    pass
