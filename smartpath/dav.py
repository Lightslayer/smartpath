import easywebdav

import dateutil
import time
import os

from .base import BasePath

class stat_result(object):
    def __init__(self, path):
        self._file = path

    @property
    def st_mode(self):
        raise NotImplementedError

    @property
    def st_ino(self):
        '''return inode number'''
        raise NotImplementedError

    @property
    def st_dev(self):
        '''return device'''
        raise NotImplementedError

    @property
    def st_nlink(self):
        '''return number of hard links'''
        raise NotImplementedError

    @property
    def st_uid(self):
        '''return user id of owner'''
        raise NotImplementedError

    @property
    def st_gid(self):
        '''return group id of owner'''
        raise NotImplementedError

    @property
    def st_size(self):
        '''return size of file, in bytes'''
        return self._file.size

    @property
    def st_atime(self):
        '''time of most recent access'''
        atime = dateutil.parser.parse(self.mtime)
        return round(time.mktime(atime.timetuple()))

    @property
    def st_mtime(self):
        '''return time of most recent content modification'''
        mtime = dateutil.parser.parse(self.mtime)
        return round(time.mktime(mtime.timetuple()))

    @property
    def st_ctime(self):
        '''return time of most recent metadata change'''
        ctime = dateutil.parser.parse(self.ctime)
        return round(time.mktime(ctime.timetuple()))


class WebDavPath(easywebdav.File, BasePath):
    @property
    def anchor(self):
        '''The concatenation of the host and root, or ''.'''
        return '{}/'.format(self.hostname)

    @property
    def stem(self):
        return os.path.splitext(os.path.basename(self.path))[0]


class WebDavClient(easywebdav.Client):
    '''WebDAV client providing os-like functions'''

    def __init__(self, host, port=0, auth=None,
                 username=None, password=None, protocol=None,
                 verify_ssl=True, path=None, cert=None, use_env=True):
        if use_env:
            username = username or os.environ.get('WEBDAV_USERNAME')
            password = password or os.environ.get('WEBDAV_PASSWORD')
            auth = auth or os.environ.get('WEBDAV_AUTH')
            port = port or os.environ.get('WEBDAV_SERVER_PORT')
            protocol = protocol or os.environ.get('WEBDAV_SERVER_PROTOCOL',
                                                  'https')
            verify_ssl = os.environ.get('WEBDAV_VERIFY_SSL', verify_ssl)
            path = path or os.environ.get('WEBDAV_PATH')
            cert = cert or os.environ.get('WEBDAV_CERT')
        kwargs = dict([(key, val) for key, val in locals().items()
                       if key not in ['self', '__class__', 'use_env']])
        super(easywebdav.Client, self).__init__(**kwargs)

    def stat(self, path):
        return stat_result(self.ls(path)[0])

    def lstat(self, path):
        raise NotImplementedError

    def open(self, path, mode='r'):
        if 'r' in mode:
            pass
        elif 'w' in mode:
            os.path.split(path)[0]
        else:
            raise ValueError('Unsupported mode: {}'.format(repr(mode)))

    def listdir(self, path=''):
        [f.name for f in self.ls(path)]

    def scandir(self, *args):
        raise (f.name for f in self.ls('/' + '/'.join(args)))

    def utime(self, path, times=None, *, ns=None,
              dir_fd=None, follow_symlinks=True):
        raise NotImplementedError

    # alias functions for uniform interface
    unlink = easywebdav.Client.delete
    replace = easywebdav.Client.rename
    makedirs = easywebdav.Client.mkdirs
