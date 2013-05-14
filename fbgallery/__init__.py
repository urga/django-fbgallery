# -*- coding: utf-8 -*-
"""
fbgallery
"""
# Author: Douglas Creager <dcreager@dcreager.net>,
# adapted to Urga's pipeline by Dries Desmet <dries@urga.be>.
# This file is placed into the public domain.
 
# Calculates the current version number.  If possible, this is the
# output of “git describe”, modified to conform to the versioning
# scheme that setuptools uses.  If “git describe” returns an error
# (most likely because we're in an unpacked copy of a release tarball,
# rather than in a git working copy), then we fall back on reading the
# contents of the RELEASE-VERSION file.
#
# To use this script, place it in your main module's __init__.py file,
# and use the results of get_git_version() as your package version:
#
# setup(
#     version=__import__("{{ project_name }}").__version__,
#     .
#     .
#     .
# )
#
# This will automatically update the RELEASE-VERSION file, if
# necessary.  Note that the RELEASE-VERSION file should *not* be
# checked into git; please add it to your top-level .gitignore file.
#
# You'll probably want to distribute the RELEASE-VERSION file in your
# sdist tarballs; to do this, just create a MANIFEST.in file that
# contains the following line:
#
#   include RELEASE-VERSION
 
__all__ = ("get_git_version")
 
from subprocess import Popen, PIPE
 
 
def call_git_describe():
    try:
        # the options to git describe mean:
        # --dirty: describe HEAD and appends "-dirty" if the working tree is not clean.
        #          So you can get 76001f2-dirty as an example. Obviously, seeing 'dirty'
        #          means somebody messed up.
        # --always: show commit hash only when there is no tag yet. 
        
        p = Popen(
            ['git', 'describe', '--dirty', '--always'],
            stdout=PIPE,
            stderr=PIPE,
            )
        p.stderr.close()
        line = p.stdout.readlines()[0]
        return line.strip()
 
    except:
        return None
 
 
def read_release_version():
    try:
        f = open("RELEASE-VERSION", "r")
 
        try:
            version = f.readlines()[0]
            return version.strip()
 
        finally:
            f.close()
 
    except:
        return None
 
 
def write_release_version(version):
    f = open("RELEASE-VERSION", "w")
    f.write("%s\n" % version)
    f.close()
 
 
def get_git_version():
    # Read in the version that's currently in RELEASE-VERSION.
 
    release_version = read_release_version()
 
    # First try to get the current version using “git describe”.
 
    version = call_git_describe()
 
    # If that doesn't work, fall back on the value that's in
    # RELEASE-VERSION.
 
    if version is None:
        version = release_version
 
    # If we still don't have anything, that's an error.
 
    if version is None:
        raise ValueError("Cannot find the version number!")
 
    # If the current version is different from what's in the
    # RELEASE-VERSION file, update the file to be current.
 
    if version != release_version:
        write_release_version(version)
 
    # Finally, return the current version.
 
    return version
 
 
__version__ = get_git_version()