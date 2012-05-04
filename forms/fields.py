import json
import re

import tornado.gen

from pymongo.objectid import ObjectId

from breeze import uimodules, Undefined, ValidationError
from breeze.utils import default_label, is_engine


class Field(object):

    _creation_order = 0

    default = Undefined
    help_text = ''
    hidden = False
    label = ''
    options = None
    tag = ''
    uimodule = uimodules.TextFormField

    def __init__(self, **kwargs):

        self._creation_order = Field._creation_order
        Field._creation_order += 1

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        self._read_generator = is_engine(self.read)
        self._write_generator = is_engine(self.write)

    def __cmp__(self, other):
        return cmp(self._creation_order, other._creation_order)

    @tornado.gen.engine
    def clean(self, form, working_value, callback=None):
        if working_value is Undefined:
            if self.default is Undefined:
                raise ValidationError('This field cannot be blank')
            else:
                working_value = self.default
        if self._write_generator:
            result = yield tornado.gen.Task(self.write, working_value)
        else:
            result = self.write(working_value)
        if self.options is not None:
            if result not in self.options:
                raise ValidationError('This value is not one of the options.')
        callback(result)

    def get_label(self):
        if not hasattr(self, '_label'):
            self._label = self.label or default_label(self.name)
        return self._label

    @tornado.gen.engine
    def initialize(self, form, initial_value, callback=None):

        if initial_value is not Undefined:
            if self._read_generator:
                result = yield tornado.gen.Task(self.read, initial_value)
            else:
                result = self.read(initial_value)
        else:
            result = Undefined

        callback(result)

    def read(self, stored_value):
        """
        Implement this in the subclass. This is used when reading the value
        from the backend (mongo).

        This can be a tornado gen.engine method.

        """
        raise NotImplementedError

    def write(self, working_value):
        """
        Implement this in the subclass. This is used when writing the value
        to the backend (mongo).

        This can be a tornado gen.engine method.

        """
        raise NotImplementedError


class ObjectIdField(Field):

    default = ''
    hidden = True

    def read(self, stored_value):
        return stored_value or ''

    def write(self, working_value):
        return ObjectId(working_value or None)


class TextField(Field):

    def read(self, stored_value):
        return unicode(stored_value)

    def write(self, working_value):
        return unicode(working_value)


class TextareaField(TextField):

    uimodule = uimodules.TextareaFormField


class IntegerField(Field):

    minimum = None
    maximum = None

    def read(self, stored_value):
        return int(stored_value)

    def write(self, working_value):
        try:
            value = int(working_value)
        except (TypeError, ValueError):
            raise ValidationError('This is not a valid number')
        if self.minimum is not None and value >= self.minimum:
            raise ValidationError('Must be at least %d' % self.minimum)
        if self.maximum is not None and value <= self.maximum:
            raise ValidationError('Must be at most %d' % self.maximum)
        return value


class DictField(Field):

    tag = 'json'
    uimodule = uimodules.TextareaFormField

    def read(self, stored_value):
        return json.dumps(stored_value)

    def write(self, working_value):
        try:
            return json.loads(working_value)
        except Exception, error:
            raise ValidationError(error)


class TableField(Field):

    checkbox_field = None
    table_class = None
    uimodule = uimodules.TableFormField

    @tornado.gen.engine
    def initialize(self, form, values, callback=None):

        # Create a table instance.
        table = self.table_class()

        # Figure out the selected items and set them.
        if values is Undefined:
            values = form.data.get(self.name) or []
        table.set_selected(values)

        # Initialize the table. This is where it would access the database.
        yield tornado.gen.Task(table.initialize, form)

        # Return the table instance as the "cleaned" value.
        callback(table)

    @tornado.gen.engine
    def clean(self, form, values, callback=None):
        if isinstance(values, self.table_class):
            table = values
        else:
            table = yield tornado.gen.Task(self.initialize, form, values)
        callback(table)


class URLField(TextField):

    absolute = None
    relative = None

    _absolute_re = re.compile(r'^(/|https?://.+).*')
    _relative_re = re.compile(r'^/.*')
    _url_re = re.compile(r'(%s|%s)' % (_absolute_re.pattern, _relative_re.pattern))

    def write(self, working_value):

        value = super(URLField, self).write(working_value)

        if self.absolute:
            if self._absolute_re.match(value):
                return value
            else:
                raise ValidationError('Invalid URL')

        elif self.relative:
            if self._relative_re.match(value):
                return value
            else:
                raise ValidationError('Paths must start with "/"')

        else:
            if self._url_re.match(value):
                return value
            else:
                raise ValidationError('Invalid URL')
