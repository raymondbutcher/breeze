import tornado.web
from breeze.uimodules import FormField


class PageContent(tornado.web.UIModule):
    def render(self, content):
        if isinstance(content, dict):
            raise NotImplementedError('TODO: Render %s' % content)
        else:
            return content


class PageContentFormField(FormField):

    def embedded_javascript(self):
        return "$deps.load('breeze-forms-pages');"

    template = 'pages/page-content-form-field.html'
