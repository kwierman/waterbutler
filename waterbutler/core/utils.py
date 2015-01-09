import os

from stevedore import driver


def make_provider(name, auth, credentials, settings):
    manager = driver.DriverManager(
        namespace='waterbutler.providers',
        name=name,
        invoke_on_load=True,
        invoke_args=(auth, credentials, settings),
    )
    return manager.driver


class WaterButlerPath:
    """
    A standardized and validated immutable WaterButler path.
    """
    def __init__(self, path, prefix=True, suffix=True):
        self._validate_path(path)

        self._orig_path = path
        self._parts = path.rstrip('/').split('/')
        self._is_dir = path.endswith('/')
        self._is_root = path == '/'
        self._prefix = prefix
        self._suffix = suffix

        # after class variables have been setup
        self._path = self._format_path(path)

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self._orig_path)

    def __str__(self):
        return self._orig_path

    @property
    def path(self):
        return self._path

    @property
    def is_dir(self):
        return self._is_dir

    @property
    def is_file(self):
        return not self._is_dir

    @property
    def is_root(self):
        return self._is_root

    @property
    def name(self):
        return self._parts[-1]

    @property
    def parts(self):
        return self._parts

    @property
    def parent(self):
        cls = self.__class__
        return cls('/'.join(self._parts[:-1]) + '/', prefix=self._prefix, suffix=self._suffix)

    def _format_path(self, path):
        """Formats the specified path per the class configuration prefix/suffix configuration.
        :param str path: WaterButler specific path
        :rtype str: Provider specific path
        """
        # Display root as '/' if prefix is true
        if not self._prefix:
            path = path.lstrip('/')
        if path and path != '/':
            if not self._suffix:
                path = path.rstrip('/')
        return path

    def _validate_path(self, path):
        """Validates a WaterButler specific path, e.g. /folder/file.txt, /folder/
        :param str path: WaterButler path
        """
        if not path:
            raise ValueError('Must specify path')
        if not path.startswith('/'):
            raise ValueError('Invalid path \'{}\' specified'.format(path))
        if '//' in path:
            raise ValueError('Invalid path \'{}\' specified'.format(path))
        # Do not allow path manipulation via shortcuts, e.g. '..'
        absolute_path = os.path.abspath(path)
        if not path == '/' and path.endswith('/'):
            absolute_path += '/'
        if not path == absolute_path:
            raise ValueError('Invalid path \'{}\' specified'.format(absolute_path))
