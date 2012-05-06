import tornado.gen

from breeze import forms


class CreateForm(forms.Form):

    browse_form_key = 'pages.BrowsePages'
    edit_form_key = 'pages.EditPage'
    mongo_collection = 'pages'

    @tornado.gen.engine
    def _save_item(self, callback=None):
        yield tornado.gen.Task(self.handler.db[self.mongo_collection].save, self.cleaned)
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


class BrowseAdminForm(forms.Form):
    pass


class CreateAdminForm(forms.Form):
    pass


class EditAdminForm(CreateAdminForm):
    pass
