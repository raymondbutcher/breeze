import os

import tornado.template

# TODO: Create a loader which uses a database?

template_loader = tornado.template.Loader(os.path.dirname(__file__))
