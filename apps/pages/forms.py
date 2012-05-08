from breeze.forms import admin, fields
from breeze.apps.pages import uimodules


class PageContentField(fields.DictField):
    uimodule = uimodules.PageContentFormField


class PageFormBuilder(admin.FormBuilder):

    name = 'Page'
    mongo_collection = 'pages'

    class Browse:
        columns = ('title', 'path')
        path_header = 'URL Path'

    class Fields:
        _id = fields.ObjectIdField()
        path = fields.URLField(label='URL path', help_text='e.g. /about/', relative=True)
        title = fields.TextField(label='Page title')
        structure = PageContentField(
            label='Page content',
        )
        fluid = fields.BooleanField(label='Fluid grid layout')


BrowsePages, CreatePage, EditPage = PageFormBuilder.make_classes(
    'pages.BrowsePages',
    'pages.CreatePage',
    'pages.EditPage',
)
