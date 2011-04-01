import os

cwd = os.path.dirname(__file__)
__version__ = open(os.path.join(cwd, 'version.txt'), 'r').read().strip()

def get_version():
    return __version__
