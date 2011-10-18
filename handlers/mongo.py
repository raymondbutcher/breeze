import asyncmongo
import tornado.web
from tornado.options import options

class MongoHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(pool_id='mydb', host=options.mongohost, port=options.mongoport, maxcached=10, maxconnections=50, dbname='test')
        return self._db

    def get_mongo_result(self, gen_result):
        args, kwargs = gen_result
        result, error = (lambda results, error=None: (results[0], error))(args, **kwargs)
        if error:
            raise tornado.web.HTTPError(500, error)
        if not result:
            raise tornado.web.HTTPError(404)
        return result
