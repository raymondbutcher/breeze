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


#class SaveAndContinue(object):
#
#    form = CreatePage
#    label = 'Save and continue'
#
#    def callback(self, form_result):
#        page_id = form_result
#        redirect_to_EditPage with page_id
