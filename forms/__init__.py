import tornado.gen

from breeze import uimodules, Undefined, ValidationError
from breeze.forms.fields import Field
from breeze.utils import default_label, is_engine


class FormButton(object):

    def __init__(self, action_func, confirm=False, default=Undefined, hidden=False, label='', style='', extra_classes='', require_valid_data=True):
        self._action_func = action_func
        self._generator = is_engine(action_func)
        self.confirm = confirm
        self.default = default
        self.hidden = hidden
        self.label = label or default_label(action_func.__name__)
        self.style = style
        self.extra_classes = extra_classes
        self.require_valid_data = require_valid_data

    @tornado.gen.engine
    def __call__(self, form, callback=None):
        if self._generator:
            result = yield tornado.gen.Task(self._action_func, form)
        else:
            result = self._action_func(form)
        callback(result)


class FormClass(type):

    def __new__(cls, name, bases, dictionary):

        new_class = super(FormClass, cls).__new__(cls, name, bases, dictionary)

        form_elements = {
            'buttons': (new_class, FormButton),
            'fields': (new_class.__dict__.get('Fields'), Field),
        }

        for element_type, (container, element_class) in form_elements.iteritems():

            elements = {}

            # Find all of the elements from the parent classes.
            for base in bases:
                parent_elements = base.__dict__.get(element_type, [])
                for item in parent_elements:
                    elements.setdefault(item.name, item)

            # Find all of the elements in this class. These override
            # any existing parent class elements with the same name.
            if container:
                for name, item in container.__dict__.iteritems():

                    # Allow for decorated functions defined within a form.
                    # Automatically initialize these elements.
                    if getattr(item, 'form_class', None) is element_class:
                        item = item()
                        setattr(new_class, name, item)

                    if isinstance(item, element_class):
                        item.name = name
                        elements[name] = item

            # Sort and remember the results.
            setattr(new_class, element_type, sorted(elements.values()))
            setattr(new_class, ('%s_dict' % element_type), elements)

        return new_class


class Form(object):
    """The base Form class to be used in Breeze apps."""

    __metaclass__ = FormClass

    method = 'post'
    uimodule = uimodules.WebForm

    @tornado.gen.engine
    def __init__(self, handler, callback=None):
        """
        Validates and processes the given data.
        Performs a button action if necessary.

        """

        self.handler = handler
        self.data = {}
        self.cleaned = {}
        self.errors = {}

        # Get the data from the request.
        for key in handler.request.arguments:
            if key.endswith('[]'):
                self.data[key[:-2]] = handler.get_arguments(key)
            else:
                self.data[key] = handler.get_argument(key)

        # Initialize all fields that have not been provided with data.
        initial_values = yield tornado.gen.Task(self.initial_values)
        for field in self.fields:
            if field.name not in self.data:
                initial_value = initial_values.get(field.name, Undefined)
                try:
                    result = yield tornado.gen.Task(field.initialize, self, initial_value)
                except ValidationError, error:
                    self.errors[field.name] = error
                else:
                    if result is not Undefined:
                        self.data[field.name] = result

        # Find the button/action that should happen.
        for button in self.buttons:
            if button.name in self.data:
                default_button = None
                break
        else:
            for button in self.buttons:
                if button.default is not Undefined:
                    default_button = button
                    break
            else:
                button = None
                default_button = None
        specific_action = button and not default_button

        # Process all provided field data.
        for field in self.fields:

            raw_value = self.data.get(field.name, Undefined)

            if raw_value is Undefined and not specific_action:
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
                self.data[field.name] = ''
            else:
                self.data[field.name] = raw_value

            # And perform validation.
            try:
                self.cleaned[field.name] = yield tornado.gen.Task(field.clean, self, raw_value)
            except ValidationError, error:
                self.errors[field.name] = error

        # Remember which button, if any, was clicked.
        if button and self.errors and button.require_valid_data:
            self.button = None
            self.errors[button.name] = True
        else:
            self.button = button

        callback(self)

    @tornado.gen.engine
    def __call__(self, callback=None):
        if self.button:
            result = yield tornado.gen.Task(self.button, self)
        else:
            result = None
        callback(result)

    @tornado.gen.engine
    def initial_values(self, callback=None):
        callback({})


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


################################################################################
## Form table for displaying data                                              #
################################################################################


class FormTable(object):

    columns = ()
    data = []
    selected = []
    checkbox_field = None

    def __init__(self, selected=None):
        # TODO: move assertion into a metaclass
        assert self.columns
        self.set_selected(selected or [])

    def _is_selected(self, item):
        if self.checkbox_field:
            if self.checkbox_field in item:
                if unicode(item[self.checkbox_field]) in self.selected:
                    return True
        return False

    def get_rows(self):
        for item in self.data:
            columns = tuple(self.create_columns(item))
            selected = self._is_selected(item)
            yield (item, columns, selected)

    def get_selected(self):
        if self.checkbox_field:
            for item in self.data:
                if self._is_selected(item):
                    yield item

    def get_url(self, column, item):
        get_url = getattr(self, '%s_url' % column, None)
        if get_url:
            return get_url(item)
        else:
            return ''

    def set_selected(self, selected):
        self.selected = [unicode(item) for item in selected]

    @tornado.gen.engine
    def initialize(self, form, value, callback=None):
        callback(True)

    def create_columns(self, item):
        for column in self.columns:
            text = item.get(column)
            yield (text, self.get_url(column, item))
