from breeze.admin import Admin

from forms import BrowseUsers, CreateUser


class UsersAdmin(Admin):

    name = 'Users'
    description = 'User management'

    browse = BrowseUsers
    create = CreateUser
