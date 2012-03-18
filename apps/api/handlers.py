import tornado.gen
import tornado.web

from breeze.apps.api.registry import Registry
from breeze.handlers import MongoRequestHandler


class ApiHandler(MongoRequestHandler):

    def __init__(self, *args, **kwargs):

        super(ApiHandler, self).__init__(*args, **kwargs)

        self.registry = Registry(self.application.breeze.apps)


class WebApiHandler(ApiHandler):

    @tornado.web.addslash
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, namespace=None, method_name=None):

        if namespace:
            if namespace in self.registry:
                registry = self.registry[namespace]
            else:
                raise tornado.web.HTTPError(404, 'There is no API for %s' % namespace)
        else:
            registry = self.registry

        if method_name:
            template = 'api/method.html'
        else:
            template = 'api/browse.html'

        if method_name:
            if method_name in registry:
                method = registry[method_name]
            else:
                raise tornado.web.HTTPError(404, 'There is no API method %s.%s' % (namespace, method_name))
        else:
            method = None

        #print registry.registry

        context = {
            'method': method,
            'registry': registry,
        }

        self.render(template, **context)
