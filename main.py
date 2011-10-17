import os
import sys

root_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(root_dir)
sys.path.append(parent_dir)

from tornado.ioloop import IOLoop
from tornado.options import options, parse_command_line, parse_config_file
from tornado.web import Application

from breeze.handlers import PageHandler, FakePageHandler
from breeze.ui import uimodules


# Define the application's URL handlers.
urls = (
    (r'/create-fake/', FakePageHandler),
    (r'/(.*)', PageHandler),
    (r'/', PageHandler),
)


if __name__ == '__main__':

    # Parse the options.
    parse_config_file(os.path.join(root_dir, 'server.conf'))
    parse_command_line()

    # Define the settings.
    settings = {
        'cookie_secret': options.cookie_secret,
        'debug': options.debug,
        'static_path': os.path.join(root_dir, 'static'),
        'ui_modules': uimodules,
    }

    # Create and run the application server.
    application = Application(urls, **settings)    
    application.listen(options.port, address=options.address)
    IOLoop.instance().start()
