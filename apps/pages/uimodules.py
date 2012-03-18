import tornado.web


class PageContent(tornado.web.UIModule):
    def render(self, content):
        if isinstance(content, dict):
            raise NotImplementedError('TODO: Render %s' % content)
        else:
            return content
