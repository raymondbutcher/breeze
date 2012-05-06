import tornado.gen

from breeze import forms
from breeze.forms import fields
from breeze import search


class CreateUser(forms.Form):

    class Fields:
        _id = fields.ObjectIdField()
        email = fields.EmailField(label='Email address')
        name = fields.TextField()
        first_name = fields.TextField()
        last_name = fields.TextField()
        superuser = fields.BooleanField()

    @tornado.gen.engine
    def _save_user(self, callback=None):
        yield tornado.gen.Task(self.handler.db.users.save, self.cleaned)
        callback(self.cleaned['_id'])

    @forms.button(style='primary')
    @tornado.gen.engine
    def save(self, callback=None):
        user_id = yield tornado.gen.Task(self._save_user)
        form_key = 'core.BrowseUsers'
        self.handler.redirect(form_key)
        callback(user_id)

    @forms.button
    @tornado.gen.engine
    def save_and_edit(self, callback=None):
        user_id = yield tornado.gen.Task(self._save_user)
        form_key = 'core.EditUser'
        self.handler.redirect('%s?_id=%s' % (form_key, user_id))
        callback(user_id)


class EditUser(CreateUser):

    @tornado.gen.engine
    def _save_user(self, callback=None):
        lookup = {'_id': self.cleaned['_id']}
        yield tornado.gen.Task(self.handler.db.users.update, lookup, self.cleaned)
        callback(self.cleaned['_id'])

    @tornado.gen.engine
    def initial_values(self, callback=None):
        if self.handler.request.method in ('POST', 'PUT'):
            # There is no need to get database values
            # when submitting new values.
            callback({})
        else:
            # Get the initial values from the database
            # so they can be displayed in the form.
            user_id = yield tornado.gen.Task(self.fields_dict['_id'].clean, self, self.data['_id'])
            result = yield tornado.gen.Task(self.handler.db.users.find_one, {
                '_id': user_id,
            })
            user = self.handler.get_mongo_result(result)
            callback(user)

    @forms.button(style='inverse', extra_classes='pull-right', require_valid_data=False)
    @tornado.gen.engine
    def delete(self, callback=None):
        lookup = {'_id': self.cleaned['_id']}
        yield tornado.gen.Task(self.handler.db.users.remove, lookup)
        form_key = 'core.BrowseUsers'
        self.handler.redirect(form_key)
        callback(True)


class UserTable(forms.FormTable):

    headers = ('Name', 'Email')
    columns = ('name', 'email')
    checkbox_field = '_id'

    @tornado.gen.engine
    def initialize(self, form, callback=None):

        # Look up the users based on the IDs and/or search keywords.
        lookups = []
        users = form.data.get('users')
        if users:
            lookups.append(search.id_search(*users))
        keywords = form.data.get('keywords')
        if keywords:
            lookups.append(search.match_all_words(keywords, 'name', 'email'))
        lookup = search.combine_lookups('$and', *lookups)

        # Now fetch the user data.
        result = yield tornado.gen.Task(form.handler.db.users.find, lookup)
        self.data = form.handler.get_mongo_result(result, allow_none=True) or []

        callback(True)

    def name_url(self, item):
        form_key = 'core.EditUser'
        return '%s?_id=%s' % (form_key, item['_id'])


class BrowseUsers(forms.Form):

    method = 'get'

    class Fields:
        keywords = fields.TextField(default='', label='Search')
        users = fields.TableField(table_class=UserTable)

    @forms.button(style='inverse', confirm=True)
    @tornado.gen.engine
    def delete(self, callback=None):

        user_ids = [user['_id'] for user in self.cleaned['users'].get_selected()]
        if user_ids:
            lookup = search.id_search(*user_ids)
            yield tornado.gen.Task(self.handler.db.users.remove, lookup)

        form_key = 'core.BrowseUsers'

        keywords = self.data.get('keywords')
        if keywords:
            self.handler.redirect('%s?keywords=%s' % (form_key, keywords))
        else:
            self.handler.redirect(form_key)

        callback(True)
