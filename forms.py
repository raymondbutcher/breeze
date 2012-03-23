import json
import re


class Undefined(Exception):
    pass


class ValidationError(Exception):
    pass


class FormField(object):

    _order = 0

    optional = False

    def __init__(self, validator_func, default=Undefined, help_text='', label='', type=''):

        self._validator_func = validator_func
        self._order = self.__class__._order
        self.__class__._order += 1

        self.default = default
        self.help_text = help_text
        self.label = label
        self.type = type or validator_func.__name__

    def __bool__(self):
        return hasattr(self, 'value')

    def __cmp__(self, other):
        return cmp(self._order, other._order)

    def __get__(self, form, obj_type):
        return form[self.name]

    def __repr__(self):
        try:
            return self.name
        except AttributeError:
            return super(FormField, self).__repr__()

    def __set__(self, form, raw_value):

        if self.name in form:
            del form[self.name]

        if raw_value is Undefined:
            if self.default is Undefined:
                raise Undefined('%r is a required field.' % self)
            else:
                form[self.name] = self.default
        else:
            form[self.name] = raw_value
            self.clean(raw_value)

    def clean(self, raw_value):
        if raw_value is Undefined:
            if self.default is Undefined:
                raise ValidationError('This field cannot be blank')
        return self._validator_func(raw_value)


class FormClass(type):

    def __new__(cls, name, bases, dictionary):

        new_class = super(FormClass, cls).__new__(cls, name, bases, dictionary)

        field_dict = {}

        # Find all of the fields in the parent classes.
        for base in bases:
            for field in base.__dict__.get('__fields__', []):
                field_dict.setdefault(field.name, field)

        # Find all of the fields in this class. These override
        # any existing parent class fields with the same name.
        for name, field in new_class.__dict__.iteritems():
            if isinstance(field, FormField):
                field.name = name
                field_dict[name] = field

        # Sort the fields by the order in which they were defined.
        new_class.__fields__ = sorted(field_dict.values())
        new_class.__buttons__ = []

        return new_class


class Form(object):
    """The base Form class to be used in Breeze apps."""

    __metaclass__ = FormClass

    def __init__(self, handler):
        """
        Validates and processes the given data.
        Performs a button action if necessary.???
        """

        self.__errors__ = errors = {}
        self.__values__ = data = {}

        data = {}
        for key in handler.request.arguments:
            data[key] = handler.get_argument(key)

        for button in self.__buttons__:
            if button.name in data:
                break
        else:
            button = None

        for field in self.__fields__:

            raw_value = data.get(field.name, Undefined)

            # Skip the validation of this field if an action is not being
            # performed, or there is no default value and no value was sent.
            if not button and raw_value is field.default is Undefined:
                continue

            # Set the value of the field, which performs validation.
            try:
                setattr(self, field.name, raw_value)
            except (ValidationError, Undefined), error:
                print 'errors', field.name, raw_value

                errors[field.name] = error

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
        return self.__values__[field_name]

    def __setitem__(self, field_name, raw_value):
        self.__values__[field_name] = raw_value

    def __delitem__(self, field_name):
        del self.__values__[field_name]
        if field_name in self.__errors__:
            del self.__errors__[field_name]

    def __repr__(self):
        kwargs = ('%s=%r' % item for item in self)
        return '%s(%s)' % (self.__class__.__name__, ', '.join(kwargs))


class FormButton(object):

    def __init__(self, action_func, **button_options):
        pass


def button(*args, **button_options):
    """
    TODO
    Creates a Button instance that will trigger something ????

    """

    if button_options:
        def decorator(action_func):
            def create_button(**form_options):
                button_options.update(form_options)
                return FormButton(action_func, **button_options)
            return create_button
        return decorator
    else:
        action_func = args[0]
        def create_button(**form_options):
            button_options.update(form_options)
            return FormButton(action_func, **button_options)
        return create_button




def formfield(*args, **field_options):
    """
    Creates a FormField instance that uses the given function as its validator.
    The resulting form field can then be used when defining a Form class.

    """

    if field_options:
        def decorator(validator_func):
            def create_field(**form_options):
                field_options.update(form_options)
                return FormField(validator_func, **field_options)
            return create_field
        return decorator
    else:
        validator_func = args[0]
        def create_field(**form_options):
            field_options.update(form_options)
            return FormField(validator_func, **field_options)
        return create_field


################################################################################
# Form fields                                                                  #
################################################################################


@formfield
def integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError('That is not a whole number')


@formfield(type='json')
def json_string(value):
    try:
        return json.loads(value)
    except ValueError, error:
        raise ValidationError(error)


@formfield
def text(value):
    return unicode(value)


@formfield
def url(value):
    value = unicode(value)
    if re.match(r'^(/|https?://.+).*', value):
        return value
    else:
        raise ValidationError('Invalid URL')


@formfield(type='path')
def url_path(value):
    value = unicode(value)
    if re.match(r'^/.*', value):
        return value
    else:
        raise ValidationError('Paths must start with "/"')
