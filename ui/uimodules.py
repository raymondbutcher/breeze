import tornado.web


class PageContent(tornado.web.UIModule):
    def render(self, content):
        if isinstance(content, dict):
            raise NotImplementedError('TODO: Render %s' % content)
        else:
            return content


class BaseModal(tornado.web.UIModule):

    template = 'includes/modals/base.html'

    def render(self, **context):
        assert 'id' in context
        assert 'js' in context
        assert 'after' in context
        return self.render_string(self.template, **context)


class SignInModal(BaseModal):
    template = 'includes/auth/sign-in-modal.html'


class RegisterModal(SignInModal):
    template = 'includes/auth/register-modal.html'


class CancelModalButton(tornado.web.UIModule):

    template = 'includes/modals/buttons/cancel.html'

    def render(self, **context):
        assert 'js' in context
        assert 'after' in context
        context.setdefault('label', 'Cancel')
        return self.render_string(self.template, **context)


class LinkModalButton(tornado.web.UIModule):
    """
    A link button for modals.

    Required:   js (in js mode or not)
                after (link href)

    Optional:   label (button contents, defaults to 'Continue')
                modal (switch to this modal instead of
                       following the link if in js mode)

    """

    template = 'includes/modals/buttons/link.html'

    def render(self, **context):
        assert 'js' in context
        assert 'after' in context
        context.setdefault('label', 'Continue')
        context.setdefault('modal', False)
        return self.render_string(self.template, **context)
