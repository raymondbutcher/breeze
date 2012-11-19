#!/usr/bin/env python

import cwd
assert cwd

import os

from tornado.ioloop import IOLoop
from tornado.options import options, parse_command_line, parse_config_file
from tornado.web import Application

from breeze import uimodules
from breeze.apps.core.urls import setup_urls
from breeze.registry import AdminRegistry, AppRegistry, FormRegistry
from breeze.template import MapTemplateLoader


# TODO: Static paths within apps?


class Breeze(object):

    def __init__(self, project_dir):

        self.project_dir = project_dir
        self.breeze_dir = os.path.dirname(__file__)

        self.parse_options()

        self.apps = AppRegistry(self.breeze_dir, self.project_dir)
        self.admins = AdminRegistry(self.apps)
        self.forms = FormRegistry(self.apps)

        self.settings = {
            'cookie_secret': options.cookie_secret,
            'debug': options.debug,
            'login_url': '/sign-in/',
            'static_path': os.path.join(self.breeze_dir, 'static'),
            'template_loader': self.get_template_loader(),
            'ui_modules': list(self.get_ui_modules()),
        }

    def get_template_loader(self):
        def get_template_paths():
            for app in self.apps.keys():
                for root in (self.breeze_dir, self.project_dir):
                    path = os.path.join(root, 'apps', app, 'templates')
                    if os.path.exists(path):
                        yield app, path
        return MapTemplateLoader(dict(get_template_paths()), self.breeze_dir)

    def get_ui_modules(self):
        yield uimodules
        for app in self.apps.values():
            if hasattr(app, 'uimodules'):
                yield app.uimodules

    def get_urls(self):
        if options.setup:
            urls = list(setup_urls)
        else:
            urls = []
        for app_name, app in self.apps.iteritems():
            if hasattr(app, 'urls'):
                try:
                    urls += app.urls.urls
                except AttributeError, error:
                    raise AttributeError('%s: %s' % (app_name, error))
        return urls

    def parse_options(self):
        parse_config_file(os.path.join(self.breeze_dir, 'options.conf'))
        parse_command_line()
        if options.settings:
            # Import the settings from the provided settings module.
            current_settings = __import__(name=options.settings, fromlist=['*'])
            for name in dir(current_settings):
                if name in options:
                    value = getattr(current_settings, name)
                    option = options[name]
                    option.set(value)
            # Parse the command line again as it has top priority.
            parse_command_line()

    def launch(self):
        """Create and run the application server."""
        application = Application(self.get_urls(), **self.settings)
        application.breeze = self
        application.listen(options.listen_port, address=options.listen_address)
        IOLoop.instance().start()


if __name__ == '__main__':
    Breeze(cwd.root_dir).launch()
