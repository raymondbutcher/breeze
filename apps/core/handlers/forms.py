import tornado.gen
import tornado.web

from breeze import Undefined
from breeze.handlers import MongoRequestHandler


class FormValidationHandler(MongoRequestHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, key):

        form = self.application.breeze.forms.get(key)
        if not form:
            raise tornado.web.HTTPError(404, 'Form "%s" not found.' % key)

        field_name = self.get_argument('name', '')

        multi_value = field_name.endswith('[]')
        if multi_value:
            field_name = field_name[:-2]

        for field in form.fields:
            if field.name == field_name:
                break
        else:
            raise tornado.web.HTTPError(404, 'Field "%s.%s" not found.' % (key, field_name))

        if multi_value:
            raw_value = []
            values = self.get_argument('values')
            for index in xrange(int(values)):
                value = self.get_argument('value[%d]' % index, '')
                raw_value.append(value)
        else:
            raw_value = self.get_argument('value', '')
            raw_value = raw_value.strip()

        if not raw_value:
            raw_value = Undefined

        try:
            yield tornado.gen.Task(field.clean, form, raw_value)
        except Exception, error:
            success = False
            error = unicode(error)
        else:
            success = True
            error = False

        self.finish({
            'success': success,
            'error': error,
        })
