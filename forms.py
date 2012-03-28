import json
import re
import uimodules

import tornado.gen

from utils import is_engine


def default_label(name):
    return name.capitalize().replace('_', ' ')


class Undefined(Exception):
    pass


class ValidationError(Exception):
    pass


class FormField(object):

    _order = 0

    def __init__(self, validator_func, default=Undefined, help_text='', hidden=False, label='', type=Undefined, uimodule=uimodules.FormField):

        self._order = self.__class__._order
        self.__class__._order += 1

        if is_engine(validator_func):
            self.generator = True
        else:
            self.generator = False

        self._validator_func = validator_func
        self._label = label
        self._validated = {}

        self.default = default
        self.help_text = help_text
        self.hidden = hidden
        self.uimodule = uimodule

        if type is Undefined:
            self.type = default_label(validator_func.__name__).lower()
        else:
            self.type = type

    def __cmp__(self, other):
        return cmp(self._order, other._order)

    @tornado.gen.engine
    def validate(self, form, raw_value, callback=None):
        if raw_value is Undefined:
            if self.default is Undefined:
                raise ValidationError('This field cannot be blank')
            else:
                raw_value = self.default
        if self.generator:
            result = yield tornado.gen.Task(self._validator_func, form, raw_value)
        else:
            result = self._validator_func(form, raw_value)
        callback(result)

    @property
    def label(self):
        if not self._label:
            self._label = default_label(self.name)
        return self._label


class FormButton(object):

    def __init__(self, action_func, default=Undefined, hidden=False, label='', style=''):
        self._action_func = action_func
        self.default = default
        self.hidden = hidden
        self.label = label or default_label(action_func.__name__)
        self.style = style

    def __call__(self, form, handler):
        self._action_func(form, handler)


class FormClass(type):

    def __new__(cls, name, bases, dictionary):

        new_class = super(FormClass, cls).__new__(cls, name, bases, dictionary)

        types = (
            ('__fields__', FormField, 'formfield'),
            ('__buttons__', FormButton, None),
        )

        # Look up fields and buttons in the same way.
        for type_var, type_class, inline_flag in types:

            items = {}

            # Find all of the fields/buttons in the parent classes.
            for base in bases:
                for item in base.__dict__.get(type_var, []):
                    items.setdefault(item.name, item)

            # Find all of the fields/buttons in this class. These override
            # any existing parent class items with the same name.
            for name, item in new_class.__dict__.iteritems():

                # Allow for inline fields defined within a form.
                if inline_flag and getattr(item, inline_flag, False):
                    item = item()
                    setattr(new_class, name, item)

                if isinstance(item, type_class):
                    item.name = name
                    items[name] = item

            # Sort and remember the results.
            setattr(new_class, type_var, sorted(items.values()))

        return new_class


class Form(object):
    """The base Form class to be used in Breeze apps."""

    __metaclass__ = FormClass
    __method__ = 'post'
    __uimodule__ = uimodules.WebForm

    @tornado.gen.engine
    def __init__(self, handler, callback=None):
        """
        Validates and processes the given data.
        Performs a button action if necessary.

        """

        self.__handler__ = handler
        self.__data__ = data = {}
        self.__validated__ = validated = {}
        self.__errors__ = errors = {}
        self.__button__ = None

        # Get the data from the request.
        for key in handler.request.arguments:
            data[key] = handler.get_argument(key)

        # Find the button/action that should happen.
        for button in self.__buttons__:
            if button.name in data:
                default_button = None
                break
        else:
            for button in self.__buttons__:
                if button.default is not Undefined:
                    default_button = button
                    break
            else:
                button = None
                default_button = None

        # Process all provided field data.
        for field in self.__fields__:

            raw_value = data.get(field.name, Undefined)

            if raw_value is Undefined and (not button or default_button):
                # A value was not supplied, but we're only displaying the form
                # since there was no specific button action.
                if field.default is Undefined:
                    # This field has no value, but that is OK since there was
                    # no requested action. Skip it and it will be blank.
                    continue
                else:
                    # Use the default value. This will show up in the form.
                    raw_value = field.default

            # Set the value of the field.
            if raw_value is Undefined:
                data[field.name] = ''
            else:
                data[field.name] = raw_value

            # And perform validation.
            try:
                validated[field.name] = yield tornado.gen.Task(field.validate, self, raw_value)
            except ValidationError, error:
                errors[field.name] = error

        if button and not errors:
            self.__button__ = button
        else:
            self.__button__ = None
            if button and errors:
                errors[button.name] = True

        callback(self)

    def __call__(self):
        """Perform a button action, if there was one, returning the result."""
        if self.__button__ and not self.__errors__:
            return self.__button__(self, self.__handler__)

    def __iter__(self):
        """
        Allows simple conversion of a form instance into a dictionary
        of its field names and processed (validated) values.

        """

        for field in self.__fields__:
            try:
                yield field.name, self[field.name]
            except KeyError:
                yield field.name, field.default

    def __getitem__(self, field_name):
        return self.__data__.get(field_name, '')

    def __setitem__(self, field_name, raw_value):
        self.__data__[field_name] = raw_value


################################################################################
# Decorators for building form elements                                        #
################################################################################


def button(*args, **button_options):
    """
    Creates a Button instance that will trigger an action.

    """

    if button_options:
        def create_button(action_func):
            return FormButton(action_func, **button_options)
        return create_button
    else:
        action_func = args[0]
        return FormButton(action_func, **button_options)


def formfield(*args, **field_options):
    """
    Creates a function that returns a customized FormField instance The
    resulting form field can be used when defining a Form class.

    """

    if field_options:
        def decorator(validator_func):
            def create_field(**form_options):
                options = field_options.copy()
                options.update(form_options)
                return FormField(validator_func, **options)
            create_field.formfield = True
            return create_field
        return decorator
    else:
        validator_func = args[0]
        def create_field(**form_options):
            options = field_options.copy()
            options.update(form_options)
            return FormField(validator_func, **options)
        create_field.formfield = True
        return create_field


################################################################################
# Form fields                                                                  #
################################################################################


@formfield
def integer(form, value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError('This is not a valid number')


@formfield(type='integer')
def positive_integer(form, value):
    try:
        value = int(value)
        assert value >= 1
        return value
    except (TypeError, ValueError):
        raise ValidationError('This is not a valid number')


@formfield(type='json')
def json_string(form, value):
    try:
        return json.loads(value)
    except ValueError, error:
        raise ValidationError(error)


@formfield
def text(form, value):
    return unicode(value)


@formfield
def url(form, value):
    value = unicode(value)
    if re.match(r'^(/|https?://.+).*', value):
        return value
    else:
        raise ValidationError('Invalid URL')


@formfield(type='path')
def url_path(form, value):
    value = unicode(value)
    if re.match(r'^/.*', value):
        return value
    else:
        raise ValidationError('Paths must start with "/"')


def table(table_class, **kwargs):
    options = {
        'default': None,
        'uimodule': uimodules.TableFormField,
    }
    options.update(kwargs)
    @formfield
    @tornado.gen.engine #added automatically
    def table(self, value, callback=None):
        table = yield tornado.gen.Task(table_class, self)
        callback(table)
    return table(**options)


################################################################################
# Form tables for displaying data                                              #
################################################################################


class FormTable(object):

    @tornado.gen.engine
    def __init__(self, form, callback=None):
        assert hasattr(self, 'headers')
        assert hasattr(self, 'columns')
        self.form = form
        self.data = yield tornado.gen.Task(self.source)
        callback(self)

    def __iter__(self):
        for item in self.data:
            yield tuple(self.create_row(item))

    def create_row(self, item):
        for column in self.columns:
            text = item.get(column)
            get_url = getattr(self, '%s_url' % column, None)
            url = get_url and get_url(item) or ''
            yield (text, url)

    @tornado.gen.engine
    def source(self, callback=None):
        raise NotImplementedError
        callback(None)
