import asyncmongo
import json
import tornado.web
import bson.json_util
from tornado.options import options

from breeze.handlers.error import ErrorHandler


class MongoHandler(ErrorHandler):

    @staticmethod
    def json_decode(data):
        return json.loads(data, default=bson.json_util.object_hook)

    @staticmethod
    def json_encode(data):
        return json.dumps(data, default=bson.json_util.default)

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = asyncmongo.Client(
                pool_id='breeze',
                host=options.mongo_host,
                port=options.mongo_port,
                maxcached=10,
                maxconnections=50,
                dbname=options.mongo_dbname,
                dbuser=options.mongo_dbuser,
                dbpass=options.mongo_dbpass,
            )
        return self._db

    @staticmethod
    def get_mongo_result(gen_result, allow_none=False):
        args, kwargs = gen_result
        result, error = (lambda results, error=None: (results[0], error))(args, **kwargs)
        if error:
            raise tornado.web.HTTPError(500, str(error))
        if not result:
            if allow_none:
                return None
            raise tornado.web.HTTPError(404)
        return result
