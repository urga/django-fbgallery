"""
fbgallery
"""

import subprocess
from os.path import isdir, dirname, join


__version_info__ = {
    'major': 0,
    'minor': 1,
    'micro': 1,
    'releaselevel': 'dev',
    'serial': 1
}

def get_version(short=False):
    """Derive version number from git tags, if that is not possible, get it from the source code"""
    
    if isdir(join(dirname(dirname(__file__)), ".git")):
        return subprocess.Popen(
            ["git", "describe", "--tags", "--always"],
            stdout=subprocess.PIPE
        ).communicate()[0].strip()
    else:
        assert __version_info__['releaselevel'] in ('dev', 'alpha', 'beta', 'final')
        vers = ["%(major)i.%(minor)i" % __version_info__, ]
        if __version_info__['micro']:
            vers.append(".%(micro)i" % __version_info__)
        if __version_info__['releaselevel'] != 'final' and not short:
            vers.append('%s%i' % (__version_info__['releaselevel'], __version_info__['serial']))
        return ''.join(vers)

__version__ = get_version()
