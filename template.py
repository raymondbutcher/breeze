import os
import re

from tornado.template import Loader, Template


class MapTemplateLoader(Loader):

    def __init__(self, mappings, *root_directories, **kwargs):
        super(Loader, self).__init__(**kwargs)
        self.mappings = dict(self._prepare_mappings(mappings))
        self.root_directories = root_directories

    def _create_template(self, name):
        for root in self.root_directories:
            path = os.path.join(root, name)
            try:
                with open(path, 'r') as template:
                    return Template(template.read(), name=name, loader=self)
            except IOError:
                pass
        raise

    def _prepare_mappings(self, mappings):
        for pretend_path, real_path in mappings.iteritems():
            expression = re.compile('^%s(?=/)' % re.escape(pretend_path))
            yield expression, real_path

    def resolve_path(self, name, parent_path=None):
        for pattern, real_path in self.mappings.iteritems():
            if pattern.search(name):
                path = pattern.sub(real_path, name)
                return path
        else:
            return name
