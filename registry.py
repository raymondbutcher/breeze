import glob
import inspect
import os
import sys

from breeze.admin import Admin
from breeze.forms import Form
from breeze.utils import unique_items

# Import the following when loading apps.
APP_IMPORTS = ('admin', 'forms', 'uimodules', 'urls')


class Registry(dict):

    def get_key(self, value):
        if not hasattr(self, 'inverted'):
            self.inverted = dict((value, key) for (key, value) in self.iteritems())
        return self.inverted.get(value)


class AppRegistry(Registry):

    def __init__(self, paths, exclude=()):
        for root in unique_items(paths):
            app_dir = os.path.join(root, 'apps')
            project_name = os.path.basename(root)
            pattern = os.path.join(app_dir, '*', '__init__.py')
            for path in glob.iglob(pattern):
                app_name = os.path.basename(os.path.dirname(path))
                if app_name in exclude:
                    continue
                elif app_name == 'breeze':
                    raise ValueError('You cannot name an app "breeze"')
                app_path = '%s.apps.%s' % (project_name, app_name)
                __import__(app_path, fromlist=APP_IMPORTS)
                self[app_name] = sys.modules[app_path]
                if not hasattr(self[app_name], 'title'):
                    self[app_name].title = app_name.title()


class AdminRegistry(Registry):

    def __init__(self, apps):

        for app_name, app in apps.iteritems():

            try:
                items = [getattr(app.admin, name) for name in dir(app.admin)]
            except AttributeError:
                continue

            for item in items:
                if self.is_admin(item):
                    admin = item()
                    self[admin.key] = admin

    def with_form(self, form):
        for admin in self.values():
            for name, form_class in admin:
                if isinstance(form, form_class):
                    return admin

    @staticmethod
    def is_admin(item):
        """Checks if the given item is an Admin subclass."""

        if not inspect.isclass(item):
            return False
        if not issubclass(item, Admin):
            return False
        if item is Admin:
            return False
        return True


class FormRegistry(Registry):

    def __init__(self, apps):

        for app_name, app in apps.iteritems():

            try:
                items = [getattr(app.forms, name) for name in dir(app.forms)]
            except AttributeError:
                continue

            for item in items:
                if self.is_form(item):
                    self['%s.%s' % (app_name, item.__name__)] = item

    def get_key(self, form):
        if isinstance(form, Form):
            form = type(form)
        for key, test_form in self.iteritems():
            if form is test_form:
                return key

    @staticmethod
    def is_form(item):
        """Checks if the given item is a Form subclass."""

        if not inspect.isclass(item):
            return False
        if not issubclass(item, Form):
            return False
        if item is Form:
            return False
        return True
