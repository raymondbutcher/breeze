import json

from breeze.forms import FormField, ValidationError


def formfield(validator_func):
    def create_field(**options):
        return FormField(validator_func, **options)
    return create_field


@formfield
def integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError('%r is not an integer' % value)


@formfield
def json_string(value):
    try:
        return json.loads(value)
    except ValueError, error:
        raise ValidationError(error)


@formfield
def text(value):
    return unicode(value)
