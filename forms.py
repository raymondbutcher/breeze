import json
import re


def default_label(func):
    return func.__name__.capitalize().replace('_', ' ')


class Undefined(Exception):
    pass


class ValidationError(Exception):
    pass


class FormField(object):

    _order = 0

    def __init__(self, validator_func, default=Undefined, help_text='', hidden=False, label='', type=Undefined):

        self._validator_func = validator_func
        self._order = self.__class__._order
        self.__class__._order += 1

        self.default = default
        self.help_text = help_text
        self.hidden = hidden
        self.label = label or default_label(validator_func)

        if type is Undefined:
            self.type = default_label(validator_func).lower()
        else:
            self.type = type

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
        if raw_value is not Undefined:
            form[self.name] = raw_value
        self.clean(raw_value)

    def clean(self, raw_value):
        if raw_value is Undefined:
            if self.default is Undefined:
                raise ValidationError('This field cannot be blank')
        return self._validator_func(raw_value)


class FormButton(object):

    def __init__(self, action_func, default=Undefined, hidden=False, label='', style=''):
        self._action_func = action_func
        self.default = default
        self.hidden = hidden
        self.label = label or default_label(action_func)
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

    def __init__(self, handler):
        """
        Validates and processes the given data.
        Performs a button action if necessary.???
        """

        self.__handler__ = handler

        self.__errors__ = errors = {}
        self.__values__ = data = {}

        data = {}
        for key in handler.request.arguments:
            data[key] = handler.get_argument(key)

        # Find the button/action that should happen.
        for button in self.__buttons__:
            if button.name in data:
                break
        else:
            for button in self.__buttons__:
                if button.default is not Undefined:
                    break
            else:
                button = None

        # Process the supplied data, if any.
        for field in self.__fields__:

            raw_value = data.get(field.name, Undefined)

            if raw_value is Undefined and not button:
                # No action is being performed, and no value was supplied.
                # Use a default value if possible, otherwise skip the field.
                if field.default is Undefined:
                    continue
                else:
                    raw_value = field.default

            # Set the value of the field, which performs validation.
            try:
                setattr(self, field.name, raw_value)
            except (ValidationError, Undefined), error:
                errors[field.name] = error

        # Perform the button action.
        if button:
            if errors:
                errors[button.name] = True
            else:
                button(self, handler)

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
    Creates a FormField instance that uses the given function as its validator.
    The resulting form field can then be used when defining a Form class.

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
def integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError('This is not an integer.')


@formfield(type='1+')
def positive_integer(value):
    try:
        value = int(value)
        assert value >= 1
    except (TypeError, ValueError):
        raise ValidationError('This is not a positive integer.')


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
