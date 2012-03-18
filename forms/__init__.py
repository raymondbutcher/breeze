class Undefined(Exception):
    pass


class ValidationError(Exception):
    pass


class FormField(object):

    _order = 0

    optional = False

    def __init__(self, validator_func, default=Undefined):

        self._validator_func = validator_func
        self._order = self.__class__._order
        self.__class__._order += 1

        self.default = default

    def __cmp__(self, other):
        return cmp(self._order, other._order)

    def __repr__(self):
        try:
            return self.name
        except AttributeError:
            return super(FormField, self).__repr__()

    def __get__(self, obj, obj_type):
        return self.value

    def __set__(self, obj, raw_value):

        self.raw_value = raw_value

        if raw_value is Undefined:
            if self.default is Undefined:
                raise Undefined('%r is a required field.' % self)
            else:
                self.value = self.default
        else:
            try:
                self.value = self._validator_func(raw_value)
            except Exception, error:
                raise ValidationError('%r: %s' % (self, error))

        return self.value


class FormType(type):

    def __new__(cls, name, bases, dictionary):

        new_class = super(FormType, cls).__new__(cls, name, bases, dictionary)

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

        return new_class


class Form(object):

    __metaclass__ = FormType

    def __init__(self, **data):
        """Validates and processes the given data."""

        for field in self.__fields__:
            # Set the field value using the given data.
            # This will perform validation..
            raw_value = data.get(field.name, Undefined)
            setattr(self, field.name, raw_value)

    def __iter__(cls):
        """
        Allows simple conversion of a form into a dictionary
        of its field names and processed (validated) values.

        """

        for field in cls.__fields__:
            yield field.name, field.value

    def __repr__(self):
        kwargs = ('%s=%r' % item for item in self)
        return '%s(%s)' % (self.__class__.__name__, ', '.join(kwargs))
