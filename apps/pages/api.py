from breeze.apps.api import API
from breeze.forms import Form, integer, text


class BrowsePages(Form):
    start = integer(default=0)
    limit = integer(default=20)


class CreatePage(Form):
    path = text()
    title = text()
    structure = text()


class EditPage(CreatePage):
    _id = text()


class PagesAPI(API):

    name = 'Pages'

    browse = BrowsePages
    create = CreatePage
    edit = EditPage
