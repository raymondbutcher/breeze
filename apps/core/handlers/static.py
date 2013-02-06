import hashlib
import logging
import os
import re

from tornado.web import StaticFileHandler


class AppStaticFileHandler(StaticFileHandler):
    """
    An application-aware handler for serving static files.

    """

    @classmethod
    def create(cls, breeze):
        cls.app_paths = {}
        for app_name, app in breeze.apps.iteritems():
            cls.app_paths[app_name] = os.path.join(os.path.dirname(app.__file__), 'static')
        app_names = '|'.join(re.escape(app_name) for app_name in cls.app_paths)
        cls.app_path_re = re.compile('^(' + app_names + ')(?=/)')
        cls.root_dir = os.path.join(breeze.breeze_dir, 'static')
        return cls

    def initialize(self, path, default_filename=None):
        """
        Hack: Disable the root path value and allow the get() method to
        handle the root paths using the app names. It was this or entirely
        replace the get() method.

        """
        self.root = ''
        self.default_filename = default_filename

    def get(self, path, *args, **kwargs):
        path = self.get_abs_path(self.parse_url_path(path))
        return super(AppStaticFileHandler, self).get(path, *args, **kwargs)

    @classmethod
    def get_abs_path(cls, path):
        match = cls.app_path_re.match(path)
        if match:
            app_name = match.group()
            app_path = cls.app_paths[app_name]
            return cls.app_path_re.sub(app_path, path)
        else:
            return os.path.join(cls.root_dir, path)

    @classmethod
    def get_version(cls, settings, path):
        """Generate the version string to be used in static URLs.

        This method may be overridden in subclasses (but note that it
        is a class method rather than a static method).  The default
        implementation uses a hash of the file's contents.

        ``settings`` is the `Application.settings` dictionary and ``path``
        is the relative location of the requested asset on the filesystem.
        The returned value should be a string, or ``None`` if no version
        could be determined.
        """
        abs_path = cls.get_abs_path(path)
        with cls._lock:
            hashes = cls._static_hashes
            if abs_path not in hashes:
                try:
                    f = open(abs_path, "rb")
                    hashes[abs_path] = hashlib.md5(f.read()).hexdigest()
                    f.close()
                except Exception:
                    logging.error("Could not open static file %r", path)
                    hashes[abs_path] = None
            hsh = hashes.get(abs_path)
            if hsh:
                return hsh[:5]
        return None
