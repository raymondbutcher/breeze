import tornado.gen

from breeze import forms, search
from breeze.forms import fields


class FormBuilder(object):

    mongo_collection = None
    name = None
    name_plural = None  # Optional

    class Browse:
        columns = ()

    class Fields:
        pass

    @classmethod
    def browse_form(cls, name):

        if not cls.Browse.columns:
            return

        class AutoFormTable(cls.Browse, BrowseFormTable):
            edit_form_key = '%s.Edit%s' % (name.split('.')[0], cls.name)
            mongo_collection = cls.mongo_collection

        AutoFormTable.__name__ = name.split('.')[-1] + 'FormTable'

        class AutoBrowseForm(BrowseForm):

            mongo_collection = cls.mongo_collection

            class Fields:
                items = fields.TableField(table_class=AutoFormTable)

        AutoBrowseForm.__name__ = name.split('.')[-1]

        return AutoBrowseForm

    @classmethod
    def _generate_form(cls, base_class, name):

        class AutoForm(base_class):

            browse_form_key = '%s.Browse%s' % (name.split('.')[0], cls.name_plural or cls.name + 's')
            edit_form_key = '%s.Edit%s' % (name.split('.')[0], cls.name)
            mongo_collection = cls.mongo_collection

            Fields = cls.Fields

        AutoForm.__name__ = name.split('.')[-1]

        return AutoForm

    @classmethod
    def create_form(cls, name):
        return cls._generate_form(CreateForm, name)

    @classmethod
    def edit_form(cls, name):
        return cls._generate_form(EditForm, name)

    @classmethod
    def make_classes(cls, browse_form_name, create_form_name, edit_form_name):
        return (
            browse_form_name and cls.browse_form(browse_form_name),
            create_form_name and cls.create_form(create_form_name),
            edit_form_name and cls.edit_form(edit_form_name),
        )


class BrowseFormTable(forms.FormTable):

    checkbox_field = '_id'
    edit_form_key = None
    mongo_collection = None

    def get_url(self, column, item):
        """Makes the first column link to the edit page."""
        get_url = getattr(self, '%s_url' % column, None)
        if get_url:
            return get_url(item)
        elif column == self.columns[0]:
            return '%s?%s=%s' % (
                self.edit_form_key,
                self.checkbox_field,
                item[self.checkbox_field],
            )
        else:
            return ''

    @tornado.gen.engine
    def initialize(self, form, callback=None):

        # Look up items based on the IDs and/or search keywords.
        lookups = []
        items = form.data.get('items')
        if items:
            lookups.append(search.id_search(*items))
        keywords = form.data.get('keywords')
        if keywords:
            lookups.append(search.match_all_words(keywords, *self.columns))
        lookup = search.combine_lookups('$and', *lookups)

        # Now fetch the items.
        result = yield tornado.gen.Task(form.handler.db[self.mongo_collection].find, lookup)
        self.data = form.handler.get_mongo_result(result, allow_none=True) or []

        callback(True)


class BrowseForm(forms.Form):

    method = 'get'
    mongo_collection = None

    class Fields:
        keywords = fields.TextField(default='', label='Search')

    @forms.button(style='inverse', confirm=True)
    @tornado.gen.engine
    def delete(self, callback=None):

        selected_ids = [item['_id'] for item in self.cleaned['items'].get_selected()]
        if selected_ids:
            lookup = search.id_search(*selected_ids)
            yield tornado.gen.Task(self.handler.db[self.mongo_collection].remove, lookup)

        keywords = self.data.get('keywords')
        if keywords:
            self.handler.redirect('?keywords=%s' % keywords)
        else:
            self.handler.redirect('.')

        callback(True)


class CreateForm(forms.Form):

    browse_form_key = None
    edit_form_key = None
    mongo_collection = None

    @tornado.gen.engine
    def _save_item(self, callback=None):
        print self.cleaned
        lookup = {'_id': self.cleaned['_id']}
        document = self.cleaned
        upsert = True
        yield tornado.gen.Task(self.handler.db[self.mongo_collection].update, lookup, document, upsert)
        callback(self.cleaned['_id'])

    @forms.button(style='primary')
    @tornado.gen.engine
    def save(self, callback=None):
        item_id = yield tornado.gen.Task(self._save_item)
        self.handler.redirect(self.browse_form_key)
        callback(item_id)

    @forms.button
    @tornado.gen.engine
    def save_and_edit(self, callback=None):
        item_id = yield tornado.gen.Task(self._save_item)
        self.handler.redirect('%s?_id=%s' % (self.edit_form_key, item_id))
        callback(item_id)


class EditForm(CreateForm):

    @tornado.gen.engine
    def initial_values(self, callback=None):
        if self.handler.request.method in ('GET', 'HEAD'):
            item_id = yield tornado.gen.Task(self.fields_dict['_id'].clean, self, self.data['_id'])
            result = yield tornado.gen.Task(self.handler.db[self.mongo_collection].find_one, {
                '_id': item_id,
            })
            item = self.handler.get_mongo_result(result)
        else:
            item = {}
        callback(item)

    @forms.button(style='inverse', extra_classes='pull-right', require_valid_data=False, confirm=True)
    @tornado.gen.engine
    def delete(self, callback=None):
        lookup = {'_id': self.cleaned['_id']}
        yield tornado.gen.Task(self.handler.db[self.mongo_collection].remove, lookup)
        self.handler.redirect(self.browse_form_key)
        callback(True)
