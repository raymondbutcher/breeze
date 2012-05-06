from breeze.admin import Admin

from forms import BrowseUsers, CreateUser, EditUser


class UsersAdmin(Admin):
    name = 'Users'
    description = 'User management'
    show = (
        (BrowseUsers, 'Browse users'),
        (CreateUser, 'Create a new user'),
    )
    hide = (
        (EditUser, 'Edit an existing user'),
    )
