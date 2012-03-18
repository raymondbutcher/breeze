from breeze.forms import Form, integer, text


class NewPage(Form):
    path = text()
    title = text()
    structure = text()


class EditPage(NewPage):
    _id = text()


class ListPages(Form):

    start = integer(default=0)
    limit = integer(default=20)
