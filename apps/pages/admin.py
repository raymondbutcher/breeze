from breeze.admin import Admin

from forms import BrowsePages, CreatePage, EditPage


class PagesAdmin(Admin):

    name = 'Pages'
    description = 'Page management'

    browse = BrowsePages
    create = CreatePage
    _edit = EditPage
