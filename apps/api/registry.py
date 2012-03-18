import inspect

from breeze.apps.api import API


class Registry(object):

    def __init__(self, apps):

        self.registry = {}

        for app_name, app in apps.iteritems():

            try:
                items = [getattr(app.api, name) for name in dir(app.api)]
            except AttributeError:
                continue

            for item in items:
                if inspect.isclass(item) and issubclass(item, API) and item is not API:
                    self.registry[item.name] = item()

    def __iter__(self):
        for item in sorted(self.registry.values()):
            yield item
