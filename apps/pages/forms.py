import tornado.gen

from breeze import forms
from breeze.forms import fields
from breeze import search


class CreatePage(forms.Form):

    class Fields:
        _id = fields.ObjectIdField()
        path = fields.URLField(label='URL path', help_text='e.g. /about/', relative=True)
        title = fields.TextField(label='Page title')
        structure = fields.DictField(
            label='Content structure',
            help_text='A JSON string containing the grid structure.',
        )

    @tornado.gen.engine
    def _save_page(self, callback=None):
        yield tornado.gen.Task(self.handler.db.pages.save, self.cleaned)
        callback(self.cleaned['_id'])

    @forms.button(style='primary')
    @tornado.gen.engine
    def save(self, callback=None):
        page_id = yield tornado.gen.Task(self._save_page)
        form_key = 'pages.BrowsePages'
        self.handler.redirect(form_key)
        callback(page_id)

    @forms.button
    @tornado.gen.engine
    def save_and_edit(self, callback=None):
        page_id = yield tornado.gen.Task(self._save_page)
        form_key = 'pages.EditPage'
        self.handler.redirect('%s?_id=%s' % (form_key, page_id))
        callback(page_id)


class EditPage(CreatePage):

    @tornado.gen.engine
    def _save_page(self, callback=None):
        lookup = {'_id': self.cleaned['_id']}
        yield tornado.gen.Task(self.handler.db.pages.update, lookup, self.cleaned)
        callback(self.cleaned['_id'])

    @tornado.gen.engine
    def initial_values(self, callback=None):
        page_id = yield tornado.gen.Task(self.fields_dict['_id'].clean, self, self.data['_id'])
        result = yield tornado.gen.Task(self.handler.db.pages.find_one, {
            '_id': page_id,
        })
        page = self.handler.get_mongo_result(result)
        callback(page)

    @forms.button(style='inverse', extra_classes='pull-right', require_valid_data=False)
    @tornado.gen.engine
    def delete(self, callback=None):
        lookup = {'_id': self.cleaned['_id']}
        yield tornado.gen.Task(self.handler.db.pages.remove, lookup)
        form_key = 'pages.BrowsePages'
        self.handler.redirect(form_key)
        callback(True)


class PageTable(forms.FormTable):

    headers = ('Title', 'URL Path')
    columns = ('title', 'path')
    checkbox_field = '_id'

    @tornado.gen.engine
    def initialize(self, form, callback=None):

        # Look up the pages based on the IDs and/or search keywords.
        lookups = []
        pages = form.data.get('pages')
        if pages:
            lookups.append(search.id_search(*pages))
        keywords = form.data.get('keywords')
        if keywords:
            lookups.append(search.match_all_words(keywords, 'title', 'path'))
        lookup = search.combine_lookups('$and', *lookups)

        # Now fetch the page data.
        result = yield tornado.gen.Task(form.handler.db.pages.find, lookup)
        self.data = form.handler.get_mongo_result(result, allow_none=True) or []

        callback(True)

    def title_url(self, item):
        form_key = 'pages.EditPage'
        return '%s?_id=%s' % (form_key, item['_id'])


class BrowsePages(forms.Form):

    method = 'get'

    class Fields:
        keywords = fields.TextField(default='', label='Search')
        pages = fields.TableField(table_class=PageTable)

    @forms.button(style='inverse', confirm=True)
    @tornado.gen.engine
    def delete(self, callback=None):

        page_ids = [page['_id'] for page in self.cleaned['pages'].get_selected()]
        if page_ids:
            lookup = search.id_search(*page_ids)
            yield tornado.gen.Task(self.handler.db.pages.remove, lookup)

        form_key = 'pages.BrowsePages'

        keywords = self.data.get('keywords')
        if keywords:
            self.handler.redirect('%s?keywords=%s' % (form_key, keywords))
        else:
            self.handler.redirect(form_key)

        callback(True)
