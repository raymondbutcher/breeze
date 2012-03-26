from breeze.admin import Admin

from forms import BrowsePages, CreatePage, EditPage


class PagesAdmin(Admin):
    name = 'Pages'
    description = 'Page management'
    show = (
        (BrowsePages, 'Browse pages'),
        (CreatePage, 'Create a new page'),
    )
    hide = (
        (EditPage, 'Edit an existing page'),
    )
