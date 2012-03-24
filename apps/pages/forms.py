import urllib
from breeze.forms import Form, ValidationError, formfield, button, positive_integer, text, json_string, url_path


class CreatePage(Form):

    path = url_path(
        label='URL path',
        help_text='e.g. /about/',
    )

    title = text(
        label='Page title',
    )

    structure = json_string(
        label='Content structure',
        help_text='A JSON string containing the grid structure.',
    )

    @button(style='primary')
    def save(self, handler):
        handler.redirect('')

    @button
    def save_and_edit(self, handler):
        form_key = handler.application.breeze.forms.get_key(EditPage)
        query = {
            '_id': 123,
        }
        handler.redirect('%s?%s' % (form_key, urllib.urlencode(query)))


class EditPage(CreatePage):
    _id = text(hidden=True)


class BrowsePages(Form):

    __method__ = 'get'

    page = positive_integer(
        label='Page number',
        default=1,
    )

    perpage = positive_integer(
        label='Results per page',
        #default=10,
    )

    @formfield(label='Sort by', type='')
    def sort(raw_value):
        allowed = ('name', 'path')
        if raw_value in allowed:
            return raw_value
        else:
            raise ValidationError('Invalid sort value - must be one of: %s' % ', '.join(allowed))


    #@feed
    #def pages(self, handler):
    #    


    @button
    def view(self, handler):
        pass
