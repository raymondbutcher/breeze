from breeze.forms import Form, button, integer, text, json_string, url_path


class CreatePage(Form):
    path = url_path(
        label='URL path',
        help_text='e.g. /about/',
    )
    title = text(
        label='Page title',
    )
    structure = json_string(
        label='Content structure',
        help_text='A JSON string containing the grid structure.',
    )


class EditPage(CreatePage):
    _id = text()


class BrowsePages(Form):

    page = integer(
        label='Page number',
        default=1,
    )
    perpage = integer(
        label='Results per page',
        default=10,
    )

    @button
    def save(self):
        print dict(self)
        print bool(self)





#    def __call__(self, handler):
#        return []
#
#
#class AdminBrowsePages(BrowsePages):
#
#    @classmethod
#    def __call__(cls, handler):
#        data = {}
#        for key in handler.request.arguments:
#            data[key] = handler.get_argument(key)
#        result = BrowsePages(**data)(handler)
#



