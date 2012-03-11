#!/usr/bin/env python

import os
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(root_dir)
sys.path.append(parent_dir)

from tornado.ioloop import IOLoop
from tornado.options import options, parse_command_line, parse_config_file
from tornado.web import Application

from breeze.handlers.admin import AdminHandler
from breeze.handlers.auth import GoogleAuthHandler, LogoutAuthHandler, RegisterAuthHandler, SignInAuthHandler
from breeze.handlers.page import PageHandler
from breeze.handlers.fakepage import FakePageHandler

from breeze.ui import uimodules


# Define the application's URL handlers.
urls = (
    (r'/admin/', AdminHandler),
    (r'/auth/google/', GoogleAuthHandler),
    (r'/auth/logout/', LogoutAuthHandler),
    (r'/auth/register/', RegisterAuthHandler),
    (r'/auth/sign-in/', SignInAuthHandler),
    (r'/create-fake/', FakePageHandler),  # TODO: Delete this, it sucks and I hate it.
    (r'/(.*)', PageHandler),
    #(r'/', PageHandler),
)


if __name__ == '__main__':

    # Parse the options.
    parse_config_file(os.path.join(root_dir, 'options.conf'))
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

    # Define the settings.
    settings = {
        'cookie_secret': options.cookie_secret,
        'debug': options.debug,
        'static_path': os.path.join(root_dir, 'static'),
        'ui_modules': uimodules,
    }

    if options.setup:
        from breeze.handlers.setup import SetupHandler
        urls = [(r'.*', SetupHandler)]

    # Create and run the application server.
    application = Application(urls, **settings)
    application.listen(options.listen_port, address=options.listen_address)
    IOLoop.instance().start()
