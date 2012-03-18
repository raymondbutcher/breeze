#!/usr/bin/env python

import cwd
import glob
import os
import sys

from tornado.ioloop import IOLoop
from tornado.options import options, parse_command_line, parse_config_file
from tornado.web import Application

from breeze.apps.core.urls import setup_urls
from breeze.template import MapTemplateLoader


class Breeze(object):

    def __init__(self):

        # Parse the options.
        parse_config_file(os.path.join(cwd.root_dir, 'options.conf'))
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

        # Now that the options are parsed, prepare the settings for Tornado.
        self.settings = {
            'cookie_secret': options.cookie_secret,
            'debug': options.debug,
            'static_path': os.path.join(cwd.root_dir, 'static'),
            'template_loader': self.template_loader,
            'ui_modules': list(self.ui_modules),
        }

    @property
    def apps(self):
        if not hasattr(self, '_apps'):
            self._apps = {}
            app_dir = os.path.join(cwd.root_dir, 'apps')
            pattern = os.path.join(app_dir, '*', '__init__.py')
            for path in glob.iglob(pattern):
                app_name = os.path.basename(os.path.dirname(path))
                app_path = 'breeze.apps.%s' % app_name
                __import__(app_path, fromlist=['api', 'uimodules', 'urls'])
                self._apps[app_name] = sys.modules[app_path]
        return self._apps

    def get_template_paths(self):
        for app in self.apps.keys():
            path = os.path.join(cwd.root_dir, 'apps', app, 'templates')
            if os.path.exists(path):
                yield app, path

    @property
    def template_loader(self):
        return MapTemplateLoader(dict(self.get_template_paths()), cwd.root_dir)

    @property
    def ui_modules(self):
        from breeze import uimodules
        yield uimodules
        for app in self.apps.values():
            if hasattr(app, 'uimodules'):
                yield app.uimodules

    @property
    def urls(self):
        if options.setup:
            return setup_urls
        else:
            urls = []
            for app_name, app in self.apps.iteritems():
                if hasattr(app, 'urls'):
                    try:
                        urls += app.urls.urls
                    except AttributeError, error:
                        raise AttributeError('%s: %s' % (app_name, error))
            return urls

    def launch(self):
        """Create and run the application server."""
        application = Application(self.urls, **self.settings)
        application.breeze = self
        application.listen(options.listen_port, address=options.listen_address)
        IOLoop.instance().start()


if __name__ == '__main__':
    Breeze().launch()
