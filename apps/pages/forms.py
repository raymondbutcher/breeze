from breeze.forms import Form, integer, text


class CreatePage(Form):
    """Create a new page"""

    path = text()
    title = text()
    structure = text()


class EditPage(CreatePage):
    """Edit an existing page"""

    _id = text()


class BrowsePages(Form):
    """Browse pages"""

    start = integer(default=0)
    limit = integer(default=20)

    def __call__(self):
        return 'list of pages'
