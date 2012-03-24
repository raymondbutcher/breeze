import tornado.web


class BaseModal(tornado.web.UIModule):

    template = 'modals/base.html'

    def render(self, **context):
        assert 'id' in context
        assert 'js' in context
        assert 'next_url' in context
        return self.render_string(self.template, **context)


class CancelModalButton(tornado.web.UIModule):

    template = 'modals/buttons/cancel.html'

    def render(self, **context):
        assert 'js' in context
        assert 'next_url' in context
        context.setdefault('label', 'Cancel')
        return self.render_string(self.template, **context)


class LinkModalButton(tornado.web.UIModule):
    """
    A link button for modals.

    Required:   js (in js mode or not)
                next_url (link href)

    Optional:   label (button contents, defaults to 'Continue')
                modal (switch to this modal instead of
                       following the link if in js mode)

    """

    template = 'modals/buttons/link.html'

    def render(self, **context):
        assert 'js' in context
        assert 'next_url' in context
        context.setdefault('label', 'Continue')
        context.setdefault('modal', False)
        return self.render_string(self.template, **context)


class Form(tornado.web.UIModule):

    def embedded_javascript(self):
        return "$deps.load('breeze-forms');"

    def render(self, form):
        context = {
            'form': form,
            'form_registry': self.handler.application.breeze.forms,
        }
        return self.render_string('forms/form.html', **context)


class FormField(tornado.web.UIModule):

    def render(self, form, field):
        context = {
            'form': form,
            'field': field,
        }
        return self.render_string('forms/field.html', **context)


class FormButton(tornado.web.UIModule):

    def render(self, form, button):
        context = {
            'form': form,
            'button': button,
        }
        return self.render_string('forms/button.html', **context)
