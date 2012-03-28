import urllib

import tornado.gen

from breeze import forms
from breeze import search


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


class PageTable(forms.FormTable):

    headers = ('Title', 'URL Path')
    columns = ('title', 'path')

    @tornado.gen.engine
    def source(self, callback=None):
        keywords = self.form.__validated__.get('keywords', '')
        lookup = search.match_all_words(keywords, *self.columns)
        handler = self.form.__handler__
        result = yield tornado.gen.Task(handler.db.pages.find, lookup)
        pages = handler.get_mongo_result(result, allow_none=True)
        callback(pages or [])

    def title_url(self, item):
        form_key = self.form.__handler__.application.breeze.forms.get_key(EditPage)
        return '%s?_id=%s' % (form_key, item['_id'])


class BrowsePages(forms.Form):

    __method__ = 'get'

    keywords = forms.text(default='', label='Search', type='')
    page = forms.positive_integer(default=1, hidden=True)
    perpage = forms.positive_integer(default=10, hidden=True)
    pages = forms.table(PageTable)

    @forms.button(default=True, hidden=True)
    def search(self, handler):
        pass


#class CreatePageFormIdea(object):
#
#    method = 'post'
#    uimodule = uimodules.Form
#
#    class Fields:
#        path = forms.url_path(label='URL path', help_text='e.g. /about/')
#        title = forms.text(label='Page title')
#        structure = forms.json_string(
#            label='Content structure',
#            help_text='A JSON string containing the grid structure.',
#        )
#
#    class Buttons:
#
#        # If no buttons defined, maybe automatically create a Submit button?
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
#        # Create page here...
#        page_id = 452
#        return page_id
#
