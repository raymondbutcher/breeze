from breeze.forms import admin, fields


class UserFormBuilder(admin.FormBuilder):

    name = 'User'
    mongo_collection = 'users'

    class Browse:
        columns = ('name', 'email')

    class Fields:
        _id = fields.ObjectIdField()
        email = fields.EmailField(label='Email address')
        name = fields.TextField()
        first_name = fields.TextField(default='')
        last_name = fields.TextField(default='')
        superuser = fields.BooleanField()


BrowseUsers, CreateUser, EditUser = UserFormBuilder.make_classes(
    'core.BrowseUsers',
    'core.CreateUser',
    'core.EditUser',
)
