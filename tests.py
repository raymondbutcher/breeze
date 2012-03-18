# Sort out paths so that breeze import will work.
import cwd
assert cwd

from breeze.forms import Form
from breeze.forms.fields import integer, text, json_string


class NewPage(Form):
    path = text()
    title = text()
    structure = json_string()


class EditPage(NewPage):
    page_id = integer()


form = EditPage(
    page_id=1,
    path='/dogs/',
    title='Dogs',
    structure='{}',
)


print dict(form)
