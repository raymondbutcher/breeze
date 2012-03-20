import inspect
import re

from forms import Form


class AdminClass(type):

    def __new__(cls, name, bases, dictionary):

        new_class = super(AdminClass, cls).__new__(cls, name, bases, dictionary)

        form_dict = {}

        # Find all of the forms in the parent classes.
        for base in bases:
            for name, form in base.__dict__.get('__forms__', []):
                form_dict.setdefault(name, form)

        # Find all of the forms in this class. These override
        # any existing parent class forms with the same name.
        for name, form in new_class.__dict__.iteritems():
            if inspect.isclass(form) and issubclass(form, Form):
                form_dict[name] = form

        # Sort the forms by their names
        new_class.__forms__ = sorted(form_dict.iteritems())

        return new_class


class Admin(object):

    __metaclass__ = AdminClass

    def __init__(self):

        if not hasattr(self, 'app_name'):
            self.app_name = self.__module__.split('.')[-2]

        if not hasattr(self, 'key'):
            self.key = '%s.%s' % (self.app_name, self.__class__.__name__)

        for field in ('name', 'description'):
            assert hasattr(self, field), '%s requires a %s' % (self.__class__, field)

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __iter__(self):
        for name, form in self.__forms__:
            yield name, form
