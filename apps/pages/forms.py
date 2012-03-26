import urllib

import tornado.gen

from collections import namedtuple

from breeze import forms
from breeze import uimodules


class CreatePage(forms.Form):

    path = forms.url_path(label='URL path', help_text='e.g. /about/')
    title = forms.text(label='Page title')
    structure = forms.json_string(
        label='Content structure',
        help_text='A JSON string containing the grid structure.',
    )

    @forms.button(style='primary')
    def save(self, handler):
        handler.redirect('')

    @forms.button
    def save_and_edit(self, handler):
        form_key = handler.application.breeze.forms.get_key(EditPage)
        query = {
            '_id': 123,
        }
        handler.redirect('%s?%s' % (form_key, urllib.urlencode(query)))


class EditPage(CreatePage):
    _id = forms.text(hidden=True)


class BrowsePages(forms.Form):

    __method__ = 'get'

    keywords = forms.text(default='', label='Search', type='')
    page = forms.positive_integer(default=1, hidden=True)
    perpage = forms.positive_integer(default=10, hidden=True)

    @forms.formfield(default=None, uimodule=uimodules.CollectionFormField)
    def collection(self, value, callback=None):

        result = yield tornado.gen.Task(self.__handler__.db.pages.find)
        pages = self.__handler__.get_mongo_result(result)

        class Result(object):

            columns = (
                ('title', 'Title'),
                ('path', 'URL Path'),
            )

            form_key = self.__handler__.application.breeze.forms.get_key(EditPage)

            def __init__(self, **values):
                self.values = values

            def __iter__(self):
                for name, title in self.columns:
                    yield self.values.get(name)

            @property
            def url(self):
                return '%s?_id=%s' % (self.form_key, self.values['_id'])

        rows = []
        for page in pages:
            rows.append(Result(**page))

        callback(rows)

    @forms.button(default=True, hidden=True)
    def search(self, handler):
        pass


#class CreatePageFormIdea(object):
#
#    method = 'get'  # Defaults to 'post'
#    uimodule = CollectionForm  # Defaults to Form
#
#    class Fields:
#        keywords = forms.text(default='', label='Search', type='')
#        page = forms.positive_integer(default=1, hidden=True)
#        perpage = forms.positive_integer(default=10, hidden=True)
#
#        @forms.formfield
#        def special_field(form, raw_value):
#            return int(raw_value) * 2453
#
#    class Buttons:
#
#        @forms.button(style='primary')
#        def save(form):
#            form.submit()
#            form_key = form.handler.application.breeze.forms.get_key(BrowsePages)
#            form.handler.redirect(form_key)
#
#        @forms.button
#        def save_and_edit(form):
#            created_page_id = form.submit()
#            query = {
#                '_id': created_page_id,
#            }
#            form_key = form.handler.application.breeze.forms.get_key(EditPage)
#            form.handler.redirect('%s?%s' % (form_key, urllib.urlencode(query)))
#
#    def submit(self):
#
#        # Make a raw_values and values descriptor
#        # setting a value on values will also set it on raw_values
#        # but the values one will get validated after setting raw_values
#
#        self.raw_values['page'] = '10'
#
#        self['page'] = 1
#        self['perpage'] = 10
#
#        start = (self['page'] - 1) * self['perpage']
#        end = (self['page']) * self['perpage']
#
#        return range(start, end)
